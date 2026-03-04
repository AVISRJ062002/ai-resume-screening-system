resource "aws_secretsmanager_secret" "gemini_secret" {
  name = "gemini-api-key_v2"
}

resource "aws_secretsmanager_secret_version" "gemini_secret_value" {
  secret_id     = aws_secretsmanager_secret.gemini_secret.id
  secret_string = var.gemini_api_key_v2
}