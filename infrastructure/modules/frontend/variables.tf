variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "api_url" {
  description = "Backend API URL for frontend configuration (deprecated - now same-origin)"
  type        = string
  default     = ""
}

variable "alb_dns_name" {
  description = "DNS name of the ALB for API routing. If provided, /api/* requests will be routed to this ALB."
  type        = string
  default     = ""
}

variable "alb_https_enabled" {
  description = "Whether the ALB has HTTPS enabled"
  type        = bool
  default     = false
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
