# Look up ACM certificate by domain name (must be in us-east-1 for CloudFront)
data "aws_acm_certificate" "cloudfront" {
  count    = var.custom_domain != "" ? 1 : 0
  domain   = var.custom_domain
  statuses = ["ISSUED"]
}

# Generate random origin verify secret and store in Secrets Manager
resource "random_password" "origin_verify" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "cloudfront_origin" {
  name_prefix = "${var.project_name}-${var.environment}-cloudfront-origin-"
  description = "CloudFront origin verification secret for ALB"

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "cloudfront_origin" {
  secret_id = aws_secretsmanager_secret.cloudfront_origin.id
  secret_string = jsonencode({
    X-Origin-Verify = random_password.origin_verify.result
  })
}

# Cache Policy for API responses
resource "aws_cloudfront_cache_policy" "api_cache" {
  name        = "${var.project_name}-${var.environment}-api-cache"
  comment     = "Cache policy for API with query string support"
  default_ttl = var.default_ttl
  max_ttl     = var.max_ttl
  min_ttl     = var.min_ttl

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }

    headers_config {
      header_behavior = "whitelist"
      headers {
        items = ["Authorization", "CloudFront-Viewer-Country"]
      }
    }

    query_strings_config {
      query_string_behavior = "all"
    }

    enable_accept_encoding_gzip   = true
    enable_accept_encoding_brotli = true
  }
}

# Origin Request Policy
resource "aws_cloudfront_origin_request_policy" "api_origin" {
  name    = "${var.project_name}-${var.environment}-api-origin"
  comment = "Origin request policy for API"

  cookies_config {
    cookie_behavior = "all"
  }

  headers_config {
    header_behavior = "allViewerAndWhitelistCloudFront"
    headers {
      items = ["CloudFront-Viewer-Country", "CloudFront-Is-Mobile-Viewer"]
    }
  }

  query_strings_config {
    query_string_behavior = "all"
  }
}

# Response Headers Policy
resource "aws_cloudfront_response_headers_policy" "security" {
  name    = "${var.project_name}-${var.environment}-security-headers"
  comment = "Security headers policy"

  security_headers_config {
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      preload                    = true
      override                   = true
    }

    content_type_options {
      override = true
    }

    frame_options {
      frame_option = "DENY"
      override     = true
    }

    xss_protection {
      mode_block = true
      protection = true
      override   = true
    }

    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }
  }

  cors_config {
    access_control_allow_credentials = true

    access_control_allow_headers {
      items = ["Authorization", "Content-Type", "X-Session-Token", "X-Session-JWT", "X-Stytch-User-ID"]
    }

    access_control_allow_methods {
      items = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    }

    access_control_allow_origins {
      items = var.cors_allowed_origins
    }

    access_control_expose_headers {
      items = ["X-Session-JWT", "X-Session-Token", "X-Stytch-User-ID"]
    }

    access_control_max_age_sec = 3600
    origin_override            = false
  }
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "api" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${var.project_name} ${var.environment} API CDN"
  price_class         = var.price_class
  aliases             = var.custom_domain != "" ? [var.custom_domain] : []
  http_version        = "http2and3"
  wait_for_deployment = false
  web_acl_id          = var.waf_web_acl_arn

  origin {
    domain_name = var.alb_dns_name
    origin_id   = "alb-origin"

    custom_origin_config {
      http_port                = 80
      https_port               = 443
      origin_protocol_policy   = var.enable_https ? "https-only" : "http-only"
      origin_ssl_protocols     = ["TLSv1.2"]
      origin_read_timeout      = 60
      origin_keepalive_timeout = 5
    }

    custom_header {
      name  = "X-Origin-Verify"
      value = random_password.origin_verify.result
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "alb-origin"
    viewer_protocol_policy = var.enable_https ? "redirect-to-https" : "allow-all"
    compress               = true

    cache_policy_id            = aws_cloudfront_cache_policy.api_cache.id
    origin_request_policy_id   = aws_cloudfront_origin_request_policy.api_origin.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security.id

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.cache_control.arn
    }
  }

  # Ordered cache behaviors for specific paths
  dynamic "ordered_cache_behavior" {
    for_each = var.cache_behaviors
    content {
      path_pattern           = ordered_cache_behavior.value.path_pattern
      allowed_methods        = ordered_cache_behavior.value.allowed_methods
      cached_methods         = ordered_cache_behavior.value.cached_methods
      target_origin_id       = "alb-origin"
      viewer_protocol_policy = var.enable_https ? "redirect-to-https" : "allow-all"
      compress               = true

      cache_policy_id            = aws_cloudfront_cache_policy.api_cache.id
      origin_request_policy_id   = aws_cloudfront_origin_request_policy.api_origin.id
      response_headers_policy_id = aws_cloudfront_response_headers_policy.security.id

      min_ttl     = ordered_cache_behavior.value.min_ttl
      default_ttl = ordered_cache_behavior.value.default_ttl
      max_ttl     = ordered_cache_behavior.value.max_ttl
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = var.custom_domain == "" ? true : false
    acm_certificate_arn            = var.custom_domain != "" ? data.aws_acm_certificate.cloudfront[0].arn : null
    ssl_support_method             = var.custom_domain != "" ? "sni-only" : null
    minimum_protocol_version       = var.custom_domain != "" ? "TLSv1.2_2021" : null
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-cdn"
    }
  )
}

# CloudFront Function for cache control
resource "aws_cloudfront_function" "cache_control" {
  name    = "${var.project_name}-${var.environment}-cache-control"
  runtime = "cloudfront-js-2.0"
  comment = "Smart cache control - respects backend headers, blocks caching for mutations"
  publish = true
  code    = <<-EOT
function handler(event) {
    var request = event.request;

    // POST/PUT/DELETE/PATCH - NEVER cache, always pass through
    // These methods modify data, so caching would be dangerous
    if (request.method !== 'GET' && request.method !== 'HEAD') {
        return request; // Pass through as-is, backend response won't be cached
    }

    // For GET/HEAD requests:
    // - CloudFront will cache based on default_ttl/max_ttl settings
    // - OR respect Cache-Control header from your backend if present
    // - Your backend can send "Cache-Control: no-cache" for dynamic data
    // - Your backend can send "Cache-Control: max-age=300" for cacheable data

    return request;
}
EOT
}
