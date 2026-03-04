resource "aws_lambda_function" "resume_lambda" {
  function_name = "resume-processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.10"

  filename         = "../lambda/lambda.zip"
  source_code_hash = filebase64sha256("../lambda/lambda.zip")

  timeout = 30

  environment {
    variables = {
      TABLE_NAME         = aws_dynamodb_table.candidates.name
      GEMINI_SECRET_NAME = aws_secretsmanager_secret.gemini_secret.name
    }
  }
}