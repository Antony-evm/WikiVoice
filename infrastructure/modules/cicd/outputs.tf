output "github_oidc_provider_arn" {
  description = "ARN of the GitHub OIDC provider"
  value       = data.aws_iam_openid_connect_provider.github.arn
}

output "github_actions_plan_role_arn" {
  description = "ARN of the IAM role for GitHub Actions (plan)"
  value       = aws_iam_role.github_actions_plan.arn
}

output "github_actions_apply_role_arn" {
  description = "ARN of the IAM role for GitHub Actions (apply)"
  value       = aws_iam_role.github_actions_apply.arn
}

output "github_actions_backend_deploy_role_arn" {
  description = "ARN of the IAM role for GitHub Actions backend deployment (ECR + ECS)"
  value       = length(aws_iam_role.github_actions_backend_deploy) > 0 ? aws_iam_role.github_actions_backend_deploy[0].arn : ""
}

output "github_actions_frontend_deploy_role_arn" {
  description = "ARN of the IAM role for GitHub Actions frontend deployment (S3 + CloudFront)"
  value       = length(aws_iam_role.github_actions_frontend_deploy) > 0 ? aws_iam_role.github_actions_frontend_deploy[0].arn : ""
}
