output "bucket_name" {
  description = "Name of the S3 bucket for frontend"
  value       = aws_s3_bucket.frontend.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.frontend.arn
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.frontend.id
}

output "cloudfront_distribution_arn" {
  description = "CloudFront distribution ARN"
  value       = aws_cloudfront_distribution.frontend.arn
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "frontend_url" {
  description = "URL for the frontend"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "api_url" {
  description = "URL for the API (same domain, /api path)"
  value       = var.alb_dns_name != "" ? "https://${aws_cloudfront_distribution.frontend.domain_name}/api" : ""
}

output "origin_verify_secret_arn" {
  description = "ARN of the Secrets Manager secret containing the origin verification header"
  value       = var.alb_dns_name != "" ? aws_secretsmanager_secret.cloudfront_origin[0].arn : ""
}

output "origin_verify_header_value" {
  description = "The X-Origin-Verify header value (sensitive)"
  value       = var.alb_dns_name != "" ? random_password.origin_verify[0].result : ""
  sensitive   = true
}
