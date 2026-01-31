terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket  = "wikivoice-terraform-state-eu-west-2"
    key     = "prod/terraform.tfstate"
    region  = "eu-west-2"
    encrypt = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Provider for us-east-1 (required for CloudFront WAF and ACM certificates)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Local variables
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Networking Module
module "networking" {
  source = "../../modules/networking"

  project_name         = var.project_name
  environment          = var.environment
  aws_region           = var.aws_region
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  nat_gateway_count    = var.nat_gateway_count
  enable_vpc_endpoints = var.enable_vpc_endpoints
  enable_flow_logs     = var.enable_flow_logs

  tags = local.common_tags
}

# Security Module
module "security" {
  source = "../../modules/security"

  project_name              = var.project_name
  environment               = var.environment
  vpc_id                    = module.networking.vpc_id
  app_port                  = var.app_port
  enable_bastion_access     = var.enable_bastion
  bastion_security_group_id = var.enable_bastion ? module.bastion[0].bastion_security_group_id : null

  tags = local.common_tags
}

# ECR Module
module "ecr" {
  source = "../../modules/ecr"

  project_name = var.project_name
  environment  = var.environment

  tags = local.common_tags
}

# Database Module
module "database" {
  source = "../../modules/database"

  project_name         = var.project_name
  environment          = var.environment
  private_subnet_ids   = module.networking.private_subnet_ids
  db_security_group_id = module.security.rds_security_group_id

  db_name               = var.db_name
  db_username           = var.db_username
  db_engine_version     = var.db_engine_version
  db_instance_class     = var.db_instance_class
  db_allocated_storage  = var.db_allocated_storage
  db_multi_az           = var.db_multi_az
  backup_retention_days = var.backup_retention_days
  deletion_protection   = var.deletion_protection

  tags = local.common_tags
}

# Bastion Module (optional - for secure RDS access)
module "bastion" {
  count  = var.enable_bastion ? 1 : 0
  source = "../../modules/bastion"

  project_name            = var.project_name
  environment             = var.environment
  vpc_id                  = module.networking.vpc_id
  public_subnet_id        = module.networking.public_subnet_ids[0]
  rds_security_group_id   = module.security.rds_security_group_id
  bastion_public_key      = var.bastion_public_key
  allowed_ssh_cidr_blocks = var.bastion_allowed_ssh_cidr_blocks
  instance_type           = var.bastion_instance_type

  tags = local.common_tags
}

# ECS Module
module "ecs" {
  source = "../../modules/ecs"

  project_name            = var.project_name
  environment             = var.environment
  aws_region              = var.aws_region
  vpc_id                  = module.networking.vpc_id
  public_subnet_ids       = module.networking.public_subnet_ids
  private_subnet_ids      = module.networking.private_subnet_ids
  alb_security_group_id   = module.security.alb_security_group_id
  ecs_security_group_id   = module.security.ecs_tasks_security_group_id
  task_execution_role_arn = module.security.ecs_task_execution_role_arn
  task_role_arn           = module.security.ecs_task_role_arn

  container_image = "${module.ecr.repository_url}:latest"
  container_port  = var.app_port
  task_cpu        = var.task_cpu
  task_memory     = var.task_memory
  desired_count   = var.desired_count

  environment_variables = var.environment_variables
  secrets_from_secrets_manager = [
    {
      name      = "DATABASE_URL"
      valueFrom = module.database.db_credentials_secret_arn
    },
    {
      name      = "OPENAI_API_KEY"
      valueFrom = "${var.openai_secret_arn}:OPENAI_API_KEY::"
    },
    {
      name      = "STYTCH_SECRET"
      valueFrom = "${var.stytch_secret_arn}:STYTCH_SECRET::"
    },
    {
      name      = "STYTCH_PROJECT_ID"
      valueFrom = "${var.stytch_secret_arn}:STYTCH_PROJECT_ID::"
    },
    {
      name      = "STYTCH_PUBLIC_TOKEN"
      valueFrom = "${var.stytch_secret_arn}:STYTCH_PUBLIC_TOKEN::"
    }
  ]

  health_check_path  = var.health_check_path
  enable_https       = var.enable_https
  certificate_arn    = var.certificate_arn
  custom_domain      = var.custom_domain
  log_retention_days = var.log_retention_days

  tags = local.common_tags

  depends_on = [module.database]
}

# Monitoring Module
module "monitoring" {
  source = "../../modules/monitoring"

  project_name            = var.project_name
  environment             = var.environment
  aws_region              = var.aws_region
  cluster_name            = module.ecs.cluster_name
  service_name            = module.ecs.service_name
  alb_arn_suffix          = split("/", module.ecs.alb_arn)[1]
  target_group_arn_suffix = split("/", module.ecs.target_group_arn)[1]

  min_capacity          = var.autoscaling_min_capacity
  max_capacity          = var.autoscaling_max_capacity
  enable_cpu_scaling    = var.enable_cpu_scaling
  cpu_target_value      = var.cpu_target_value
  enable_memory_scaling = var.enable_memory_scaling
  memory_target_value   = var.memory_target_value

  enable_cloudwatch_alarms = var.enable_cloudwatch_alarms

  tags = local.common_tags
}

# WAF Module (must be in us-east-1 for CloudFront)
module "waf" {
  source = "../../modules/waf"
  providers = {
    aws = aws.us_east_1
  }

  project_name         = var.project_name
  environment          = var.environment
  rate_limit_per_ip    = var.waf_rate_limit_per_ip
  auth_rate_limit      = var.waf_auth_rate_limit
  enable_managed_rules = var.waf_enable_managed_rules
  blocked_countries    = var.waf_blocked_countries
  enable_logging       = var.waf_enable_logging
  log_retention_days   = var.log_retention_days

  tags = local.common_tags
}

# CloudFront Module
module "cloudfront" {
  source = "../../modules/cloudfront"
  providers = {
    aws = aws.us_east_1
  }

  project_name    = var.project_name
  environment     = var.environment
  alb_dns_name    = module.ecs.alb_dns_name
  enable_https    = var.enable_https
  custom_domain   = var.custom_domain
  price_class     = var.cloudfront_price_class
  waf_web_acl_arn = module.waf.web_acl_arn

  default_ttl = var.cloudfront_default_ttl
  max_ttl     = var.cloudfront_max_ttl
  min_ttl     = var.cloudfront_min_ttl

  cache_behaviors = var.cloudfront_cache_behaviors

  # CORS: Allow frontend origins (set via variable to break circular dependency)
  cors_allowed_origins = var.cors_allowed_origins

  tags = local.common_tags

  depends_on = [module.ecs, module.waf]
}

# ============================================
# Frontend Static Hosting
# ============================================
module "frontend" {
  source = "../../modules/frontend"

  project_name = var.project_name
  environment  = var.environment
  api_url      = module.cloudfront.distribution_domain_name

  # Optional: attach WAF to frontend CloudFront
  # waf_web_acl_arn = module.waf.web_acl_arn

  tags = local.common_tags

  depends_on = [module.cloudfront]
}

# CI/CD Module (optional - comment out if not using GitHub Actions)
module "cicd" {
  source = "../../modules/cicd"

  project_name               = var.project_name
  environment                = var.environment
  github_org                 = var.github_org
  github_repo                = var.github_repo
  terraform_state_bucket_arn = "arn:aws:s3:::wikivoice-terraform-state-eu-west-2"

  # Backend application deployment configuration
  backend_repo                = var.github_backend_repo
  ecr_repository_arn          = module.ecr.repository_arn
  ecs_cluster_arn             = module.ecs.cluster_arn
  ecs_service_arn             = module.ecs.service_arn
  ecs_task_execution_role_arn = module.security.ecs_task_execution_role_arn
  ecs_task_role_arn           = module.security.ecs_task_role_arn

  # Frontend deployment configuration
  enable_frontend_deploy               = true
  frontend_bucket_arn                  = module.frontend.bucket_arn
  frontend_cloudfront_distribution_arn = module.frontend.cloudfront_distribution_arn

  tags = local.common_tags
}
