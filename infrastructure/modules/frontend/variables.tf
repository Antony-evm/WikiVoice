variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "api_url" {
  description = "Backend API URL for frontend configuration"
  type        = string
}

variable "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL to attach to CloudFront"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
