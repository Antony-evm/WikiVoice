# General
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "wikivoice"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"
}

# Networking
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["eu-west-2a", "eu-west-2b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "nat_gateway_count" {
  description = "Number of NAT Gateways (1 for cost optimization, 2 for HA)"
  type        = number
  default     = 0
}

variable "enable_vpc_endpoints" {
  description = "Enable VPC endpoints for cost optimization"
  type        = bool
  default     = false
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = false
}

# Application
variable "app_port" {
  description = "Port on which the application listens"
  type        = number
  default     = 8000
}

# Note: container_image is derived from module.ecr.repository_url
# No variable needed - it's automatically set in main.tf

# ECS Configuration
variable "task_cpu" {
  description = "CPU units for ECS task (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Memory for ECS task in MB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}

variable "environment_variables" {
  description = "Environment variables for the container"
  type = list(object({
    name  = string
    value = string
  }))
  default = [
    {
      name  = "ENVIRONMENT"
      value = "production"
    },
    {
      name  = "LOG_LEVEL"
      value = "info"
    },
    {
      name  = "JSON_LOGS"
      value = "true"
    },
    {
      name  = "DEBUG"
      value = "false"
    },
    {
      name  = "WORKERS"
      value = "1"
    },
    {
      name  = "MAX_REQUESTS_PER_WORKER"
      value = "10000"
    },
    {
      name  = "MAX_REQUESTS_JITTER"
      value = "1000"
    },
    {
      name  = "SHUTDOWN_TIMEOUT_SECONDS"
      value = "30"
    }
  ]
}

variable "health_check_path" {
  description = "Health check endpoint path"
  type        = string
  default     = "/health"
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}

# Database
variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "wikivoice"
}

variable "db_username" {
  description = "Master username for database"
  type        = string
  default     = "wikivoice_admin"
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "16"
}

variable "db_instance_class" {
  description = "Database instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for database in GB"
  type        = number
  default     = 20
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for database"
  type        = bool
  default     = false
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "deletion_protection" {
  description = "Enable deletion protection for database"
  type        = bool
  default     = true
}

# Auto Scaling
variable "autoscaling_min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 1
}

variable "autoscaling_max_capacity" {
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
  description = "Target CPU utilization percentage"
  type        = number
  default     = 70
}

variable "enable_memory_scaling" {
  description = "Enable memory-based auto scaling"
  type        = bool
  default     = true
}

variable "memory_target_value" {
  description = "Target memory utilization percentage"
  type        = number
  default     = 70
}

# Monitoring
variable "enable_cloudwatch_alarms" {
  description = "Enable CloudWatch alarms"
  type        = bool
  default     = true
}

# HTTPS/SSL
variable "enable_https" {
  description = "Enable HTTPS listener"
  type        = bool
  default     = false
}

variable "certificate_arn" {
  description = "ARN of ACM certificate (required if enable_https is true)"
  type        = string
  default     = null
}

variable "custom_domain" {
  description = "Custom domain for the application. Leave empty to use CloudFront URL directly."
  type        = string
  default     = ""
}

# CI/CD
variable "github_org" {
  description = "GitHub organization or username"
  type        = string
  default     = "Antony-evm"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "WikiVoice"
}

variable "github_backend_repo" {
  description = "GitHub repository name for the backend application"
  type        = string
  default     = "WikiVoice"
}

# Stytch Secrets
variable "stytch_secret_arn" {
  description = "ARN of the Secrets Manager secret containing Stytch credentials"
  type        = string
}

variable "openai_secret_arn" {
  description = "ARN of the Secrets Manager secret containing OpenAI API key"
  type        = string
}

# Bastion Host
variable "enable_bastion" {
  description = "Enable bastion host for secure RDS access"
  type        = bool
  default     = false
}

variable "bastion_public_key" {
  description = "SSH public key for bastion host"
  type        = string
  default     = ""
}

variable "bastion_allowed_ssh_cidr_blocks" {
  description = "CIDR blocks allowed to SSH to bastion"
  type        = list(string)
  default     = []
}

variable "bastion_instance_type" {
  description = "Instance type for bastion host"
  type        = string
  default     = "t3.micro"
}

# CloudFront
variable "cloudfront_price_class" {
  description = "CloudFront price class (PriceClass_All, PriceClass_200, PriceClass_100)"
  type        = string
  default     = "PriceClass_100" # US, Canada, Europe - cheapest for EU users
}

variable "cloudfront_default_ttl" {
  description = "Default TTL for cached objects in seconds"
  type        = number
  default     = 60 # 1 minute - appropriate for API responses
}

variable "cloudfront_max_ttl" {
  description = "Maximum TTL for cached objects in seconds"
  type        = number
  default     = 300 # 5 minutes - reasonable max for API
}

variable "cloudfront_min_ttl" {
  description = "Minimum TTL for cached objects in seconds"
  type        = number
  default     = 0
}

variable "cloudfront_cache_behaviors" {
  description = "Ordered cache behaviors for specific paths. Empty list uses default behavior."
  type = list(object({
    path_pattern    = string
    allowed_methods = list(string)
    cached_methods  = list(string)
    min_ttl         = number
    default_ttl     = number
    max_ttl         = number
  }))
  default = [] # Use default cache behavior for all paths
}

variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS on the API CloudFront distribution"
  type        = list(string)
  default     = ["http://localhost:5173"]
}

# WAF Configuration
variable "waf_rate_limit_per_ip" {
  description = "Maximum requests per 5 minutes per IP address"
  type        = number
  default     = 2000 # 400 per minute = ~6-7 per second
}

variable "waf_auth_rate_limit" {
  description = "Maximum auth requests per 5 minutes per IP. Set to 0 to disable."
  type        = number
  default     = 100 # 20 per minute for auth endpoints
}

variable "waf_enable_managed_rules" {
  description = "Enable AWS managed WAF rules (Common Rule Set + Bad Inputs)"
  type        = bool
  default     = true
}

variable "waf_blocked_countries" {
  description = "List of country codes to block (ISO 3166-1 alpha-2)"
  type        = list(string)
  default     = []
}

variable "waf_enable_logging" {
  description = "Enable WAF logging to CloudWatch"
  type        = bool
  default     = true
}
