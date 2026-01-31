# WAF Web ACL for CloudFront
# Note: WAF for CloudFront must be created in us-east-1
resource "aws_wafv2_web_acl" "api" {
  name        = "${var.project_name}-${var.environment}-api-waf"
  description = "WAF for API rate limiting and protection"
  scope       = "CLOUDFRONT"

  default_action {
    allow {}
  }

  # Rule 1: Rate limiting per IP
  rule {
    name     = "rate-limit-per-ip"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = var.rate_limit_per_ip
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}-${var.environment}-rate-limit"
      sampled_requests_enabled   = true
    }
  }

  # Rule 2: AWS Managed Rules - Common Rule Set (blocks common attacks)
  dynamic "rule" {
    for_each = var.enable_managed_rules ? [1] : []
    content {
      name     = "aws-managed-common"
      priority = 2

      override_action {
        none {}
      }

      statement {
        managed_rule_group_statement {
          vendor_name = "AWS"
          name        = "AWSManagedRulesCommonRuleSet"

          # Exclude rules that might block legitimate API traffic
          rule_action_override {
            action_to_use {
              count {}
            }
            name = "SizeRestrictions_BODY"
          }
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.project_name}-${var.environment}-aws-common"
        sampled_requests_enabled   = true
      }
    }
  }

  # Rule 3: AWS Managed Rules - Known Bad Inputs
  dynamic "rule" {
    for_each = var.enable_managed_rules ? [1] : []
    content {
      name     = "aws-managed-bad-inputs"
      priority = 3

      override_action {
        none {}
      }

      statement {
        managed_rule_group_statement {
          vendor_name = "AWS"
          name        = "AWSManagedRulesKnownBadInputsRuleSet"
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.project_name}-${var.environment}-bad-inputs"
        sampled_requests_enabled   = true
      }
    }
  }

  # Rule 4: Block specific countries (optional)
  dynamic "rule" {
    for_each = length(var.blocked_countries) > 0 ? [1] : []
    content {
      name     = "geo-block"
      priority = 4

      action {
        block {}
      }

      statement {
        geo_match_statement {
          country_codes = var.blocked_countries
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.project_name}-${var.environment}-geo-block"
        sampled_requests_enabled   = true
      }
    }
  }

  # Rule 5: Custom rate limit for authentication endpoints
  dynamic "rule" {
    for_each = var.auth_rate_limit > 0 ? [1] : []
    content {
      name     = "auth-rate-limit"
      priority = 5

      action {
        block {}
      }

      statement {
        rate_based_statement {
          limit              = var.auth_rate_limit
          aggregate_key_type = "IP"

          scope_down_statement {
            byte_match_statement {
              search_string         = "/api/v1/auth"
              positional_constraint = "STARTS_WITH"
              field_to_match {
                uri_path {}
              }
              text_transformation {
                priority = 0
                type     = "LOWERCASE"
              }
            }
          }
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.project_name}-${var.environment}-auth-rate-limit"
        sampled_requests_enabled   = true
      }
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project_name}-${var.environment}-waf"
    sampled_requests_enabled   = true
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-api-waf"
    }
  )
}

# CloudWatch Log Group for WAF logs
resource "aws_cloudwatch_log_group" "waf" {
  count             = var.enable_logging ? 1 : 0
  name              = "aws-waf-logs-${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = var.tags
}

# WAF Logging Configuration
resource "aws_wafv2_web_acl_logging_configuration" "waf" {
  count                   = var.enable_logging ? 1 : 0
  log_destination_configs = [aws_cloudwatch_log_group.waf[0].arn]
  resource_arn            = aws_wafv2_web_acl.api.arn

  # Only log blocked requests to save costs
  logging_filter {
    default_behavior = "DROP"

    filter {
      behavior = "KEEP"

      condition {
        action_condition {
          action = "BLOCK"
        }
      }

      requirement = "MEETS_ANY"
    }
  }
}
