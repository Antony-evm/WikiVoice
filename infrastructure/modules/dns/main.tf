# Route53 Hosted Zone (optional - use existing if provided)
data "aws_route53_zone" "main" {
  count        = var.create_hosted_zone ? 0 : 1
  name         = var.domain_name
  private_zone = false
}

resource "aws_route53_zone" "main" {
  count = var.create_hosted_zone ? 1 : 0
  name  = var.domain_name

  tags = merge(
    var.tags,
    {
      Name = var.domain_name
    }
  )
}

locals {
  zone_id = var.create_hosted_zone ? aws_route53_zone.main[0].zone_id : data.aws_route53_zone.main[0].zone_id
}

# A Record for CloudFront (API subdomain)
resource "aws_route53_record" "api_cloudfront" {
  zone_id         = local.zone_id
  name            = var.api_subdomain
  type            = "A"
  allow_overwrite = true

  alias {
    name                   = var.cloudfront_domain_name
    zone_id                = var.cloudfront_hosted_zone_id
    evaluate_target_health = false
  }
}

# AAAA Record for CloudFront (IPv6)
resource "aws_route53_record" "api_cloudfront_ipv6" {
  zone_id         = local.zone_id
  name            = var.api_subdomain
  type            = "AAAA"
  allow_overwrite = true

  alias {
    name                   = var.cloudfront_domain_name
    zone_id                = var.cloudfront_hosted_zone_id
    evaluate_target_health = false
  }
}
