resource "aws_dynamodb_table" "candidates" {
  name         = "candidates"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "candidate_id"

  attribute {
    name = "candidate_id"
    type = "S"
  }

  attribute {
    name = "ranking_group"
    type = "S"
  }

  attribute {
    name = "ats_score"
    type = "N"
  }

  global_secondary_index {
    name               = "ScoreIndex"
    hash_key           = "ranking_group"
    range_key          = "ats_score"
    projection_type    = "ALL"
  }
}