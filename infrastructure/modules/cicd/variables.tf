variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., prod, dev, staging)"
  type        = string
}

variable "github_org" {
  description = "GitHub organization or username"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "github_branch" {
  description = "GitHub branch for auto-apply (e.g., main)"
  type        = string
  default     = "main"
}

variable "github_environment" {
  description = "GitHub environment name for OIDC (e.g., production)"
  type        = string
  default     = "production"
}

variable "terraform_state_bucket_arn" {
  description = "ARN of the S3 bucket storing Terraform state"
  type        = string
}

variable "backend_repo" {
  description = "GitHub repository name for the backend application"
  type        = string
  default     = ""
}

variable "ecr_repository_arn" {
  description = "ARN of the ECR repository for the backend"
  type        = string
  default     = ""
}

variable "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  type        = string
  default     = ""
}

variable "ecs_service_arn" {
  description = "ARN of the ECS service"
  type        = string
  default     = ""
}

variable "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  type        = string
  default     = ""
}

variable "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  type        = string
  default     = ""
}

variable "frontend_bucket_arn" {
  description = "ARN of the S3 bucket for frontend deployment"
  type        = string
  default     = ""
}

variable "frontend_cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution for frontend"
  type        = string
  default     = ""
}

variable "enable_frontend_deploy" {
  description = "Whether to create the frontend deployment role"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
