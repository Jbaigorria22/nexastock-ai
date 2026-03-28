variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for naming resources"
  type        = string
  default     = "inventory-api"
}

variable "lambda_role_arn" {
  description = "ARN of the IAM role for Lambda"
  type        = string
  default     = "arn:aws:iam::720412502759:role/role-lambda-inventory"
}