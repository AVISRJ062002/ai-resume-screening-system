import json
import base64
import boto3
import uuid
import os
import requests
from decimal import Decimal
import re
from PyPDF2 import PdfReader
import io

dynamodb = boto3.resource("dynamodb")
secrets_client = boto3.client("secretsmanager")

TABLE_NAME = os.environ["TABLE_NAME"]
SECRET_NAME = os.environ["GEMINI_SECRET_NAME"]


# ------------------ SECRET ------------------

def get_api_key():
    response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
    return response["SecretString"]


# ------------------ PDF TEXT EXTRACTION ------------------

def extract_text_from_pdf(pdf_base64):
    pdf_bytes = base64.b64decode(pdf_base64)
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))

    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    # 🔥 Text normalization (IMPORTANT)
    text = text.replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)

    return text


# ------------------ REGEX EXTRACTION ------------------

def extract_basic_fields(text):

    # ---------------- EMAIL (Ultra Robust) ----------------

    # Fix broken email patterns like "abc @ gmail.com"
    text = re.sub(r'\s*@\s*', '@', text)

    # Fix "gmail . com"
    text = re.sub(r'\s*\.\s*', '.', text)

    email_match = re.search(
      r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
    text
)

    email = email_match.group(0) if email_match else None

    # ---------------- PHONE (Improved) ----------------
    phone = None

    phone_match = re.search(
        r'(\+?\d{1,3}[\s\-]?)?\(?\d{3,5}\)?[\s\-]?\d{3,5}[\s\-]?\d{3,5}',
        text
    )

    if phone_match:
        digits = re.sub(r'\D', '', phone_match.group(0))
        if len(digits) >= 10:
            phone = digits[-10:]  # Keep last 10 digits

    # ---------------- CGPA ----------------
    cgpa = None
    cgpa_patterns = [
        r'CGPA[:\s\-]*([\d\.]+)',
        r'([\d\.]+)\s*/\s*10',
        r'([\d\.]+)\s*CGPA',
        r'Aggregate[:\s\-]*([\d\.]+)',
    ]

    for pattern in cgpa_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1))
                if value <= 10:
                    cgpa = value
                    break
                elif value <= 100:
                    cgpa = round(value / 10, 2)
                    break
            except:
                pass

    # ---------------- EXPERIENCE ----------------
    experience = 0
    exp_patterns = [
        r'(\d+(\.\d+)?)\s*\+?\s*(years|yrs)',
        r'Experience[:\s\-]*(\d+(\.\d+)?)',
    ]

    for pattern in exp_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                experience = float(match.group(1))
                break
            except:
                pass

    return {
        "email": email,
        "phone": phone,
        "cgpa": cgpa,
        "experience_years": experience
    }


# ------------------ AI STRUCTURED EXTRACTION ------------------

def call_ai(resume_text):

    api_key = get_api_key()

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Extract structured data from this resume.

Return JSON with:
- name
- skills (array of only technical skills)
- education (Full degree name with specialization and university)

Return only valid JSON.

Resume:
{resume_text}
"""

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    if "choices" not in result:
        raise Exception(f"Groq API error: {result}")

    content = result["choices"][0]["message"]["content"]
    json_match = re.search(r"\{.*\}", content, re.DOTALL)

    if not json_match:
        raise Exception(f"AI did not return JSON. Raw: {content}")

    return json.loads(json_match.group(0))


# ------------------ AI SMART ATS SCORING ------------------

def calculate_ats(data):

    api_key = get_api_key()

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are an intelligent Applicant Tracking System (ATS).

Evaluate this engineering candidate holistically.

Consider:
- Technical skills depth and diversity
- Education strength
- CGPA
- Work experience
- Overall engineering potential

Return JSON only:
{{
  "ats_score": number (0-100),
  "evaluation": "short professional evaluation summary"
}}

Candidate Data:
{data}
"""

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    if "choices" not in result:
        raise Exception(f"Groq ATS error: {result}")

    content = result["choices"][0]["message"]["content"]
    json_match = re.search(r"\{.*\}", content, re.DOTALL)

    if not json_match:
        raise Exception(f"ATS AI did not return JSON. Raw: {content}")

    return json.loads(json_match.group(0))


# ------------------ MAIN HANDLER ------------------

def lambda_handler(event, context):
    try:

        raw_body = event["body"]

        if event.get("isBase64Encoded", False):
            raw_body = base64.b64decode(raw_body).decode("utf-8")

        body = json.loads(raw_body)
        pdf_base64 = body["body"]

        resume_text = extract_text_from_pdf(pdf_base64)

        basic_data = extract_basic_fields(resume_text)
        ai_data = call_ai(resume_text)

        structured = {**ai_data, **basic_data}

        ats_result = calculate_ats(structured)
        ats_score = ats_result["ats_score"]
        evaluation = ats_result["evaluation"]

        table = dynamodb.Table(TABLE_NAME)

        if structured.get("cgpa") is not None:
            structured["cgpa"] = Decimal(str(structured["cgpa"]))

        if structured.get("experience_years") is not None:
            structured["experience_years"] = Decimal(str(structured["experience_years"]))

        ats_score_decimal = Decimal(str(ats_score))

        table.put_item(
            Item={
                "candidate_id": str(uuid.uuid4()),
                "ranking_group": "ALL",
                "ats_score": ats_score_decimal,
                "evaluation": evaluation,
                **structured
            }
        )

        response_data = structured.copy()

        if isinstance(response_data.get("cgpa"), Decimal):
            response_data["cgpa"] = float(response_data["cgpa"])

        if isinstance(response_data.get("experience_years"), Decimal):
            response_data["experience_years"] = float(response_data["experience_years"])

        response_data["ats_score"] = float(ats_score)
        response_data["evaluation"] = evaluation

        return {
            "statusCode": 200,
            "body": json.dumps(response_data)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }