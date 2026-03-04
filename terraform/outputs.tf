output "api_endpoint" {
  value = aws_apigatewayv2_api.resume_api.api_endpoint
}

output "lambda_name" {
  value = aws_lambda_function.resume_lambda.function_name
}

output "dynamodb_table" {
  value = aws_dynamodb_table.candidates.name
}