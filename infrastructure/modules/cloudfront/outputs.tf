output "distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.api.id
}

output "distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.api.arn
}

output "distribution_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.api.domain_name
}

output "distribution_hosted_zone_id" {
  description = "CloudFront Route 53 zone ID"
  value       = aws_cloudfront_distribution.api.hosted_zone_id
}

output "cache_policy_id" {
  description = "ID of the CloudFront cache policy"
  value       = aws_cloudfront_cache_policy.api_cache.id
}

output "origin_request_policy_id" {
  description = "ID of the CloudFront origin request policy"
  value       = aws_cloudfront_origin_request_policy.api_origin.id
}

output "origin_verify_secret_arn" {
  description = "ARN of the Secrets Manager secret containing the origin verification header"
  value       = aws_secretsmanager_secret.cloudfront_origin.arn
}

output "origin_verify_header_value" {
  description = "The X-Origin-Verify header value (sensitive)"
  value       = random_password.origin_verify.result
  sensitive   = true
}
