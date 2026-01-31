variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., prod, dev, staging)"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "app_port" {
  description = "Port on which the application listens"
  type        = number
  default     = 8000
}

variable "bastion_security_group_id" {
  description = "Security group ID of bastion host (optional, for RDS access)"
  type        = string
  default     = null
}

variable "enable_bastion_access" {
  description = "Whether to create RDS ingress rule for bastion access. Use a static boolean to avoid for_each issues with unknown values."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
