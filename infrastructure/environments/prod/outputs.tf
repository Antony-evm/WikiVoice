output "vpc_id" {
  description = "ID of the VPC"
  value       = module.networking.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = module.networking.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = module.networking.private_subnet_ids
}

output "nat_gateway_public_ips" {
  description = "Public IPs of NAT Gateways"
  value       = module.networking.nat_gateway_public_ips
}

# Database Outputs
output "db_endpoint" {
  description = "Database connection endpoint"
  value       = module.database.db_endpoint
}

output "db_credentials_secret_arn" {
  description = "ARN of Secrets Manager secret containing database credentials"
  value       = module.database.db_credentials_secret_arn
}

# ECR Outputs
output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = module.ecr.repository_url
}

# ECS Outputs
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = module.ecs.service_name
}

# CloudFront Outputs
output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = module.cloudfront.distribution_id
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution - USE THIS for your frontend API endpoint"
  value       = module.cloudfront.distribution_domain_name
}

output "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = module.cloudfront.distribution_arn
}

output "cloudfront_origin_secret_arn" {
  description = "ARN of the Secrets Manager secret containing CloudFront origin verification header"
  value       = module.cloudfront.origin_verify_secret_arn
}

# WAF Outputs
output "waf_web_acl_id" {
  description = "ID of the WAF Web ACL"
  value       = module.waf.web_acl_id
}

output "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = module.waf.web_acl_arn
}

# API Access
output "api_url" {
  description = "CloudFront URL for API access"
  value       = "https://${module.cloudfront.distribution_domain_name}"
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer (use CloudFront instead)"
  value       = module.ecs.alb_dns_name
}

output "alb_url" {
  description = "URL of the Application Load Balancer"
  value       = var.enable_https ? "https://${module.ecs.alb_dns_name}" : "http://${module.ecs.alb_dns_name}"
}

# Monitoring Outputs
output "cloudwatch_dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = module.monitoring.dashboard_name
}

# CI/CD Outputs
output "github_actions_plan_role_arn" {
  description = "ARN of IAM role for GitHub Actions (plan)"
  value       = module.cicd.github_actions_plan_role_arn
}

output "github_actions_apply_role_arn" {
  description = "ARN of IAM role for GitHub Actions (apply)"
  value       = module.cicd.github_actions_apply_role_arn
}

output "github_actions_backend_deploy_role_arn" {
  description = "ARN of IAM role for GitHub Actions backend deployment (ECR + ECS)"
  value       = module.cicd.github_actions_backend_deploy_role_arn
}

output "github_actions_frontend_deploy_role_arn" {
  description = "ARN of IAM role for GitHub Actions frontend deployment (S3 + CloudFront)"
  value       = module.cicd.github_actions_frontend_deploy_role_arn
}

# Frontend Outputs
output "frontend_bucket_name" {
  description = "S3 bucket name for frontend"
  value       = module.frontend.bucket_name
}

output "frontend_cloudfront_distribution_id" {
  description = "CloudFront distribution ID for frontend"
  value       = module.frontend.cloudfront_distribution_id
}

output "frontend_url" {
  description = "URL for the frontend application"
  value       = module.frontend.frontend_url
}

output "ecs_task_definition_family" {
  description = "Family name of the ECS task definition"
  value       = module.ecs.task_definition_family
}

# Bastion Outputs
output "bastion_public_ip" {
  description = "Public IP of bastion host"
  value       = var.enable_bastion ? module.bastion[0].bastion_public_ip : null
}

output "bastion_ssh_command" {
  description = "SSH command to connect to bastion"
  value       = var.enable_bastion ? module.bastion[0].ssh_command : null
}

output "rds_tunnel_command" {
  description = "SSH tunnel command for RDS access via bastion"
  value       = var.enable_bastion ? "ssh -i ~/.ssh/wikivoice-bastion -L 5432:${split(":", module.database.db_endpoint)[0]}:5432 -N ec2-user@${module.bastion[0].bastion_public_ip}" : null
}

# Quick Start Instructions
output "next_steps" {
  description = "Next steps to complete the setup"
  value       = <<-EOT

    ========================================
    WIKIVOICE - INFRASTRUCTURE DEPLOYED
    ========================================

    Application Load Balancer URL:
    ${var.enable_https ? "https://${module.ecs.alb_dns_name}" : "http://${module.ecs.alb_dns_name}"}

    Frontend URL:
    ${module.frontend.frontend_url}

    API URL (CloudFront):
    https://${module.cloudfront.distribution_domain_name}

    ECR Repository:
    ${module.ecr.repository_url}

    Database Endpoint:
    ${module.database.db_endpoint}

    ========================================
    GITHUB SECRETS FOR BACKEND REPO
    ========================================

    Add these secrets to your ${var.github_backend_repo} repository:

    AWS_REGION             = ${var.aws_region}
    AWS_ROLE_ARN           = ${module.cicd.github_actions_backend_deploy_role_arn}
    ECS_CLUSTER_NAME       = ${module.ecs.cluster_name}
    ECS_SERVICE_NAME       = ${module.ecs.service_name}
    ECS_TASK_DEFINITION_FAMILY = ${module.ecs.task_definition_family}

    ========================================
    GITHUB SECRETS FOR FRONTEND DEPLOY
    ========================================

    AWS_REGION              = ${var.aws_region}
    AWS_ROLE_ARN            = ${module.cicd.github_actions_frontend_deploy_role_arn}
    S3_BUCKET               = ${module.frontend.bucket_name}
    CLOUDFRONT_DISTRIBUTION = ${module.frontend.cloudfront_distribution_id}
    VITE_API_URL            = https://${module.cloudfront.distribution_domain_name}

    ========================================
    GITHUB SECRETS FOR INFRA REPO
    ========================================

    AWS_PLAN_ROLE_ARN  = ${module.cicd.github_actions_plan_role_arn}
    AWS_APPLY_ROLE_ARN = ${module.cicd.github_actions_apply_role_arn}

    ========================================
  EOT
}
