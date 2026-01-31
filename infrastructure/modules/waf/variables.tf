variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "rate_limit_per_ip" {
  description = "Maximum requests per 5 minutes per IP address"
  type        = number
  default     = 2000 # 400 requests per minute = ~6-7 per second
}

variable "auth_rate_limit" {
  description = "Maximum auth requests per 5 minutes per IP. Set to 0 to disable."
  type        = number
  default     = 100 # 20 per minute for auth endpoints
}

variable "enable_managed_rules" {
  description = "Enable AWS managed WAF rules (Common Rule Set + Bad Inputs)"
  type        = bool
  default     = true
}

variable "blocked_countries" {
  description = "List of country codes to block (ISO 3166-1 alpha-2)"
  type        = list(string)
  default     = []
}

variable "enable_logging" {
  description = "Enable WAF logging to CloudWatch"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Number of days to retain WAF logs"
  type        = number
  default     = 7
}

variable "tags" {
  description = "Tags to apply to WAF resources"
  type        = map(string)
  default     = {}
}
