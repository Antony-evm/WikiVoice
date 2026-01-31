variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., prod, dev, staging)"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the database"
  type        = list(string)
}

variable "db_security_group_id" {
  description = "Security group ID for the database"
  type        = string
}

variable "db_name" {
  description = "Name of the database to create"
  type        = string
  default     = "wikivoice"
}

variable "db_username" {
  description = "Master username for the database"
  type        = string
  default     = "wikivoice_admin"
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "18"
}

variable "db_instance_class" {
  description = "Instance class for the database"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_storage_type" {
  description = "Storage type for the database"
  type        = string
  default     = "gp3"
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Preferred backup window"
  type        = string
  default     = "03:00-04:00" # 3-4 AM UTC
}

variable "maintenance_window" {
  description = "Preferred maintenance window"
  type        = string
  default     = "sun:04:00-sun:05:00" # Sunday 4-5 AM UTC
}

variable "db_parameter_group_family" {
  description = "Parameter group family"
  type        = string
  default     = "postgres16"
}

variable "db_max_connections" {
  description = "Maximum number of database connections"
  type        = string
  default     = "100"
}

variable "enable_performance_insights" {
  description = "Enable Performance Insights"
  type        = bool
  default     = false
}

variable "performance_insights_retention_days" {
  description = "Performance Insights retention period in days"
  type        = number
  default     = 7
}

variable "auto_minor_version_upgrade" {
  description = "Enable automatic minor version upgrades"
  type        = bool
  default     = true
}

variable "apply_immediately" {
  description = "Apply changes immediately (instead of during maintenance window)"
  type        = bool
  default     = false
}

variable "deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = true
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot when destroying"
  type        = bool
  default     = false
}

variable "secret_recovery_window_days" {
  description = "Number of days to retain secret after deletion"
  type        = number
  default     = 7
}

variable "kms_key_id" {
  description = "KMS key ID for encryption (uses default if not specified)"
  type        = string
  default     = null
}

variable "enable_cloudwatch_alarms" {
  description = "Enable CloudWatch alarms for database monitoring"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
