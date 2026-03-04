variable "project_name" {
  default = "ai-resume-system"
}

variable "gemini_api_key_v2" {
  description = "Gemini API Key"
  type        = string
  sensitive   = true
}