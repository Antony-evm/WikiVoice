variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  type        = string
}

variable "enable_https" {
  description = "Enable HTTPS on CloudFront"
  type        = bool
  default     = true
}

variable "custom_domain" {
  description = "Custom domain name for CloudFront distribution"
  type        = string
  default     = ""
}

variable "price_class" {
  description = "CloudFront price class (PriceClass_All, PriceClass_200, PriceClass_100)"
  type        = string
  default     = "PriceClass_100" # US, Canada, Europe - cheapest
}

variable "waf_web_acl_arn" {
  description = "ARN of WAF Web ACL to attach to CloudFront (must be in us-east-1)"
  type        = string
  default     = null
}

variable "default_ttl" {
  description = "Default TTL for cached objects (seconds)"
  type        = number
  default     = 300 # 5 minutes
}

variable "max_ttl" {
  description = "Maximum TTL for cached objects (seconds)"
  type        = number
  default     = 300 # 5 minutes - reasonable for API
}

variable "min_ttl" {
  description = "Minimum TTL for cached objects (seconds)"
  type        = number
  default     = 0
}

variable "cache_behaviors" {
  description = "Ordered cache behaviors for specific paths. Empty list uses default behavior which caches GET/HEAD and passes through POST/PUT/DELETE."
  type = list(object({
    path_pattern    = string
    allowed_methods = list(string)
    cached_methods  = list(string)
    min_ttl         = number
    default_ttl     = number
    max_ttl         = number
  }))
  default = [] # Empty = use default cache behavior for all paths
}

variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "tags" {
  description = "Tags to apply to CloudFront resources"
  type        = map(string)
  default     = {}
}
