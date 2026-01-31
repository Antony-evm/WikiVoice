variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., prod, dev, staging)"
  type        = string
}

variable "image_tag_mutability" {
  description = "Image tag mutability setting (MUTABLE or IMMUTABLE)"
  type        = string
  default     = "MUTABLE"

  validation {
    condition     = contains(["MUTABLE", "IMMUTABLE"], var.image_tag_mutability)
    error_message = "Image tag mutability must be either MUTABLE or IMMUTABLE."
  }
}

variable "scan_on_push" {
  description = "Enable vulnerability scanning on image push"
  type        = bool
  default     = true
}

variable "encryption_type" {
  description = "Encryption type (AES256 or KMS)"
  type        = string
  default     = "AES256"

  validation {
    condition     = contains(["AES256", "KMS"], var.encryption_type)
    error_message = "Encryption type must be either AES256 or KMS."
  }
}

variable "kms_key_id" {
  description = "KMS key ID for encryption (required if encryption_type is KMS)"
  type        = string
  default     = null
}

variable "max_image_count" {
  description = "Maximum number of tagged images to retain"
  type        = number
  default     = 10
}

variable "untagged_image_expiration_days" {
  description = "Number of days to retain untagged images"
  type        = number
  default     = 7
}

variable "repository_policy" {
  description = "Optional repository policy JSON for cross-account access"
  type        = string
  default     = null
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
