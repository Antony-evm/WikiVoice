variable "domain_name" {
  description = "Root domain name (e.g., example.com)"
  type        = string
}

variable "api_subdomain" {
  description = "API subdomain (e.g., api for api.example.com)"
  type        = string
  default     = "api"
}

variable "create_hosted_zone" {
  description = "Whether to create a new hosted zone or use existing"
  type        = bool
  default     = false
}

variable "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  type        = string
}

variable "cloudfront_hosted_zone_id" {
  description = "Hosted zone ID of the CloudFront distribution"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
