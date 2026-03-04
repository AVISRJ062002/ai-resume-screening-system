# AI Resume Screening System (Serverless + AI)

This project is an **AI-powered Resume Screening and ATS Scoring System** built using **AWS Serverless architecture, Terraform, Python, and Groq AI**.

The system automatically reads resumes sent via **Gmail**, extracts candidate details using **AI + regex**, calculates an **ATS score**, and stores structured data in **Google Sheets and DynamoDB** for easy recruiter analysis.

---

# 🚀 Features

- Automated resume extraction from Gmail
- AI-based candidate data extraction
- Smart ATS scoring system
- Resume ranking automatically in Google Sheets
- Fully serverless architecture
- Infrastructure managed using Terraform
- Cost-optimized design

---

# 🏗 System Architecture

```
Candidate Email
      ↓
Gmail Inbox
      ↓
Google Apps Script
      ↓
AWS API Gateway
      ↓
AWS Lambda (Resume Processor)
      ↓
Groq AI (Extraction + ATS Scoring)
      ↓
AWS DynamoDB
      ↓
Google Sheets (Candidate Ranking)
```

---

# ☁️ AWS Services Used

- AWS Lambda
- AWS API Gateway
- AWS DynamoDB
- AWS Secrets Manager
- AWS CloudWatch

All infrastructure is deployed using **Terraform**.

---

# 🧠 AI Used

The system uses **Groq LLM API** for:

- Resume understanding
- Skill extraction
- Education parsing
- Smart ATS scoring
- Candidate evaluation summary

---

# 📂 Project Structure

```
ai-resume-screening/
│
├── terraform/          # Infrastructure as Code (Terraform)
│
├── lambda/             # Lambda resume processing code
│   ├── lambda_function.py
│   └── requirements.txt
│
├── .gitignore
│
└── README.md
```
Interactive Architecture Demo:
View the animated workflow here: https://avisrj062002.github.io/ai-resume-screening-system/
---

# ⚙️ Setup Instructions

## 1️⃣ Clone Repository

```
git clone https://github.com/YOUR_USERNAME/ai-resume-screening-system.git
cd ai-resume-screening-system
```

---

## 2️⃣ Deploy AWS Infrastructure

```
cd terraform
terraform init
terraform apply
```

Terraform will automatically create:

- Lambda Function
- API Gateway
- DynamoDB Table
- IAM Roles
- Secrets Manager configuration

---

# 📧 Google Apps Script Automation

This script automatically detects **resume emails with PDF attachments** and sends them to the AWS API.

### Setup Steps

1. Open **Google Sheets**
2. Go to **Extensions → Apps Script**
3. Replace the script with the following code.

```
function safe(value) {
  return value ? String(value) : "";
}

function checkNewResumes() {

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");

  var threads = GmailApp.search('is:unread has:attachment filename:pdf');

  for (var i = 0; i < threads.length; i++) {

    var messages = threads[i].getMessages();

    for (var j = 0; j < messages.length; j++) {

      var attachments = messages[j].getAttachments();

      for (var k = 0; k < attachments.length; k++) {

        var file = attachments[k];

        if (file.getContentType() === "application/pdf") {

          var base64Data = Utilities.base64Encode(file.getBytes());

          var payload = {
            body: base64Data
          };

          var options = {
            method: "post",
            contentType: "application/json",
            payload: JSON.stringify(payload)
          };

          var response = UrlFetchApp.fetch(
            "YOUR_API_GATEWAY_URL/upload",
            options
          );

          var result = JSON.parse(response.getContentText());

          sheet.appendRow([
            safe(result.name),
            safe(result.email),
            safe(result.phone),
            safe((result.skills || []).join(", ")),
            safe(result.education),
            safe(result.cgpa),
            safe(result.experience_years),
            safe(result.ats_score),
            safe(result.evaluation)
          ]);
        }
      }
    }

    threads[i].markRead();
  }

  autoSortSheet();
}

function autoSortSheet() {

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");

  if (sheet.getLastRow() > 1) {

    var range = sheet.getRange(2, 1, sheet.getLastRow() - 1, 9);

    range.sort({column: 8, ascending: false});

  }
}
```

Replace:

```
YOUR_API_GATEWAY_URL
```

with your deployed **API Gateway endpoint**.

---

# 📊 Output Example

The system extracts the following information from resumes:

| Field | Description |
|------|-------------|
| Name | Candidate Name |
| Email | Email Address |
| Phone | Contact Number |
| Skills | Technical Skills |
| Education | Degree & University |
| CGPA | Academic Score |
| Experience | Years of Experience |
| ATS Score | AI Calculated Score |
| Evaluation | AI Candidate Summary |

The Google Sheet automatically **sorts candidates by ATS score**.

---

# 💰 Cost Optimization

This project uses **AWS Serverless architecture**, making it extremely cost efficient.

Estimated monthly cost:

```
$1 – $2 per month
```

Reasons:

- Lambda pay-per-use
- DynamoDB on-demand
- API Gateway minimal cost
- Groq AI free tier

---

# 🔮 Future Improvements

- Multi-user SaaS platform
- Recruiter dashboard
- Job description based ATS scoring
- Resume similarity detection
- Automated interview shortlist emails
- Candidate analytics dashboard

---

# 👨‍💻 Author

**Sarthak Jadhav**

AWS | DevOps | AI Projects
