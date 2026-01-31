variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., prod, dev, staging)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
}

variable "service_name" {
  description = "Name of the ECS service"
  type        = string
}

variable "alb_arn_suffix" {
  description = "ARN suffix of the ALB (for CloudWatch metrics)"
  type        = string
}

variable "target_group_arn_suffix" {
  description = "ARN suffix of the target group (for CloudWatch metrics)"
  type        = string
}

# Auto Scaling Configuration
variable "min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 4
}

variable "enable_cpu_scaling" {
  description = "Enable CPU-based auto scaling"
  type        = bool
  default     = true
}

variable "cpu_target_value" {
  description = "Target CPU utilization percentage for auto scaling"
  type        = number
  default     = 70
}

variable "enable_memory_scaling" {
  description = "Enable memory-based auto scaling"
  type        = bool
  default     = true
}

variable "memory_target_value" {
  description = "Target memory utilization percentage for auto scaling"
  type        = number
  default     = 70
}

variable "enable_alb_request_scaling" {
  description = "Enable ALB request count based auto scaling"
  type        = bool
  default     = false
}

variable "alb_request_count_target" {
  description = "Target ALB request count per target for auto scaling"
  type        = number
  default     = 1000
}

variable "scale_in_cooldown" {
  description = "Cooldown period (seconds) before another scale in"
  type        = number
  default     = 300
}

variable "scale_out_cooldown" {
  description = "Cooldown period (seconds) before another scale out"
  type        = number
  default     = 60
}

# CloudWatch Alarms Configuration
variable "enable_cloudwatch_alarms" {
  description = "Enable CloudWatch alarms"
  type        = bool
  default     = true
}

variable "alarm_actions" {
  description = "List of ARNs to notify when alarm triggers (SNS topics, etc.)"
  type        = list(string)
  default     = []
}

variable "min_healthy_hosts" {
  description = "Minimum number of healthy hosts before alarming"
  type        = number
  default     = 1
}

# CloudWatch Dashboard Configuration
variable "enable_cloudwatch_dashboard" {
  description = "Enable CloudWatch dashboard"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
