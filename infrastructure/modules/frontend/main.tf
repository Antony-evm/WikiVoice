# ============================================
# Frontend Static Hosting Module
# S3 bucket + CloudFront for Vue.js SPA
# Now also routes /api/* to backend ALB (same-origin)
# ============================================

# S3 bucket for frontend static files
resource "aws_s3_bucket" "frontend" {
  bucket = "${var.project_name}-${var.environment}-frontend"

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-frontend"
  })
}

# Block all public access - CloudFront uses OAC
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Bucket versioning for rollback capability
resource "aws_s3_bucket_versioning" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# CloudFront Origin Access Control
resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = "${var.project_name}-${var.environment}-frontend-oac"
  description                       = "OAC for frontend S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# ============================================
# API Origin Verification (for ALB)
# ============================================

resource "random_password" "origin_verify" {
  count   = var.alb_dns_name != "" ? 1 : 0
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "cloudfront_origin" {
  count       = var.alb_dns_name != "" ? 1 : 0
  name_prefix = "${var.project_name}-${var.environment}-cloudfront-origin-"
  description = "CloudFront origin verification secret for ALB"

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "cloudfront_origin" {
  count     = var.alb_dns_name != "" ? 1 : 0
  secret_id = aws_secretsmanager_secret.cloudfront_origin[0].id
  secret_string = jsonencode({
    X-Origin-Verify = random_password.origin_verify[0].result
  })
}

# CloudFront cache policy for static assets
resource "aws_cloudfront_cache_policy" "frontend" {
  name        = "${var.project_name}-${var.environment}-frontend-cache"
  comment     = "Cache policy for frontend static assets"
  default_ttl = 86400    # 1 day
  max_ttl     = 31536000 # 1 year
  min_ttl     = 0

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    headers_config {
      header_behavior = "none"
    }
    query_strings_config {
      query_string_behavior = "none"
    }
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true
  }
}

# ============================================
# API Cache and Origin Request Policies
# ============================================

resource "aws_cloudfront_cache_policy" "api" {
  count   = var.alb_dns_name != "" ? 1 : 0
  name    = "${var.project_name}-${var.environment}-api-cache"
  comment = "Cache policy for API - no caching, forward cookies for auth"

  default_ttl = 0
  max_ttl     = 0
  min_ttl     = 0

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    headers_config {
      header_behavior = "none"
    }
    query_strings_config {
      query_string_behavior = "none"
    }
    enable_accept_encoding_gzip   = false
    enable_accept_encoding_brotli = false
  }
}

resource "aws_cloudfront_origin_request_policy" "api" {
  count   = var.alb_dns_name != "" ? 1 : 0
  name    = "${var.project_name}-${var.environment}-api-origin-request"
  comment = "Origin request policy for API - forward all for auth"

  cookies_config {
    cookie_behavior = "all"
  }

  headers_config {
    header_behavior = "allViewerAndWhitelistCloudFront"
    headers {
      items = ["CloudFront-Viewer-Country"]
    }
  }

  query_strings_config {
    query_string_behavior = "all"
  }
}

# CloudFront response headers policy
resource "aws_cloudfront_response_headers_policy" "frontend" {
  name    = "${var.project_name}-${var.environment}-frontend-headers"
  comment = "Security headers for frontend"

  security_headers_config {
    content_type_options {
      override = true
    }
    frame_options {
      frame_option = "DENY"
      override     = true
    }
    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }
    xss_protection {
      mode_block = true
      protection = true
      override   = true
    }
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      preload                    = true
      override                   = true
    }
  }
}

# CloudFront function for SPA routing
resource "aws_cloudfront_function" "spa_routing" {
  name    = "${var.project_name}-${var.environment}-spa-routing"
  runtime = "cloudfront-js-2.0"
  comment = "Rewrite requests for SPA routing (skip /api paths)"
  publish = true
  code    = <<-EOF
    function handler(event) {
      var request = event.request;
      var uri = request.uri;

      // Don't rewrite /api requests - they go to the API origin
      if (uri.startsWith('/api')) {
        return request;
      }

      // Check if the URI has a file extension
      if (uri.includes('.')) {
        return request;
      }

      // Rewrite to index.html for SPA routing
      request.uri = '/index.html';
      return request;
    }
  EOF
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${var.project_name} ${var.environment} frontend"
  default_root_object = "index.html"
  price_class         = "PriceClass_100" # US, Canada, Europe only (cost optimized)
  http_version        = "http2and3"
  web_acl_id          = var.waf_web_acl_arn != "" ? var.waf_web_acl_arn : null

  # Origin 1: S3 for frontend static files
  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = "s3-frontend"
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
  }

  # Origin 2: ALB for API (conditional - only if alb_dns_name is provided)
  dynamic "origin" {
    for_each = var.alb_dns_name != "" ? [1] : []
    content {
      domain_name = var.alb_dns_name
      origin_id   = "alb-api"

      custom_origin_config {
        http_port                = 80
        https_port               = 443
        origin_protocol_policy   = var.alb_https_enabled ? "https-only" : "http-only"
        origin_ssl_protocols     = ["TLSv1.2"]
        origin_read_timeout      = 60
        origin_keepalive_timeout = 5
      }

      custom_header {
        name  = "X-Origin-Verify"
        value = random_password.origin_verify[0].result
      }
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-frontend"

    cache_policy_id            = aws_cloudfront_cache_policy.frontend.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.frontend.id

    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.spa_routing.arn
    }
  }

  # API behavior: /api/* -> ALB (only if alb_dns_name is provided)
  dynamic "ordered_cache_behavior" {
    for_each = var.alb_dns_name != "" ? [1] : []
    content {
      path_pattern           = "/api/*"
      allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
      cached_methods         = ["GET", "HEAD"]
      target_origin_id       = "alb-api"
      viewer_protocol_policy = "redirect-to-https"
      compress               = true

      cache_policy_id          = aws_cloudfront_cache_policy.api[0].id
      origin_request_policy_id = aws_cloudfront_origin_request_policy.api[0].id
    }
  }

  # Cache behavior for static assets (long cache)
  ordered_cache_behavior {
    path_pattern     = "/assets/*"
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-frontend"

    cache_policy_id            = aws_cloudfront_cache_policy.frontend.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.frontend.id

    viewer_protocol_policy = "redirect-to-https"
    compress               = true
  }

  # Custom error responses for SPA
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-frontend-cdn"
  })
}

# S3 bucket policy to allow CloudFront OAC access
resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontServicePrincipal"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.frontend.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.frontend.arn
          }
        }
      }
    ]
  })
}
