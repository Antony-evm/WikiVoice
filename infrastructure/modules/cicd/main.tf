# GitHub OIDC Provider for secure authentication
# Use existing provider if it already exists
data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

# IAM Role for GitHub Actions - Terraform Plan
resource "aws_iam_role" "github_actions_plan" {
  name_prefix = "${var.project_name}-${var.environment}-gh-plan-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = data.aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:pull_request"
          }
        }
      }
    ]
  })

  tags = var.tags
}

# IAM Policy for Terraform Plan (read-only)
resource "aws_iam_role_policy" "github_actions_plan" {
  name_prefix = "${var.project_name}-${var.environment}-plan-"
  role        = aws_iam_role.github_actions_plan.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "ecs:Describe*",
          "ecs:List*",
          "rds:Describe*",
          "elasticloadbalancing:Describe*",
          "ecr:Describe*",
          "ecr:List*",
          "ecr:GetLifecyclePolicy",
          "logs:Describe*",
          "logs:ListTagsForResource",
          "s3:GetObject",
          "s3:ListBucket",
          "secretsmanager:Describe*",
          "secretsmanager:List*",
          "secretsmanager:GetSecretValue",
          "secretsmanager:GetResourcePolicy",
          "rds:ListTagsForResource",
          "iam:Get*",
          "iam:List*",
          "cloudwatch:Describe*",
          "cloudwatch:List*",
          "cloudwatch:Get*",
          "autoscaling:Describe*",
          "application-autoscaling:Describe*",
          "application-autoscaling:ListTagsForResource",
          "events:Describe*",
          "events:List*",
          "cloudfront:Describe*",
          "cloudfront:Get*",
          "cloudfront:List*",
          "wafv2:Describe*",
          "wafv2:Get*",
          "wafv2:List*",
          "route53:Get*",
          "route53:List*",
          "acm:Describe*",
          "acm:Get*",
          "acm:List*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${var.terraform_state_bucket_arn}/*"
      }
    ]
  })
}

# IAM Role for GitHub Actions - Terraform Apply
resource "aws_iam_role" "github_actions_apply" {
  name_prefix = "${var.project_name}-${var.environment}-gh-apply-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = data.aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            # Allow both environment-based and branch-based subject claims
            "token.actions.githubusercontent.com:sub" = [
              "repo:${var.github_org}/${var.github_repo}:environment:${var.github_environment}",
              "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/${var.github_branch}"
            ]
          }
        }
      }
    ]
  })

  tags = var.tags
}

# IAM Policy for Terraform Apply (full access needed for infrastructure management)
resource "aws_iam_role_policy" "github_actions_apply" {
  name_prefix = "${var.project_name}-${var.environment}-apply-"
  role        = aws_iam_role.github_actions_apply.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "ecs:*",
          "rds:*",
          "elasticloadbalancing:*",
          "ecr:*",
          "logs:*",
          "secretsmanager:*",
          "iam:*",
          "cloudwatch:*",
          "autoscaling:*",
          "application-autoscaling:*",
          "s3:*",
          "kms:*",
          "events:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudfront:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "wafv2:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "route53:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "acm:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# ============================================================================
# GitHub Actions Role for Backend Application Deployment (ECR Push + ECS Deploy)
# ============================================================================

# IAM Role for Backend Repo - Deploy to ECS
resource "aws_iam_role" "github_actions_backend_deploy" {
  count       = var.backend_repo != "" ? 1 : 0
  name_prefix = "${var.project_name}-${var.environment}-gh-backend-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = data.aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = [
              "repo:${var.github_org}/${var.backend_repo}:ref:refs/heads/main",
              "repo:${var.github_org}/${var.backend_repo}:pull_request",
              "repo:${var.github_org}/${var.backend_repo}:environment:production",
              "repo:${var.github_org}/${var.backend_repo}:environment:staging"
            ]
          }
        }
      }
    ]
  })

  tags = var.tags
}

# IAM Policy for Backend Deploy - ECR Push + ECS Deploy
resource "aws_iam_role_policy" "github_actions_backend_deploy" {
  count       = var.backend_repo != "" ? 1 : 0
  name_prefix = "${var.project_name}-${var.environment}-backend-deploy-"
  role        = aws_iam_role.github_actions_backend_deploy[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # ECR Authentication
      {
        Sid    = "ECRAuth"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      # ECR Push/Pull
      {
        Sid    = "ECRPushPull"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories",
          "ecr:ListImages"
        ]
        Resource = var.ecr_repository_arn != "" ? var.ecr_repository_arn : "*"
      },
      # ECS Task Definition
      {
        Sid    = "ECSTaskDefinition"
        Effect = "Allow"
        Action = [
          "ecs:DescribeTaskDefinition",
          "ecs:RegisterTaskDefinition",
          "ecs:DeregisterTaskDefinition",
          "ecs:ListTaskDefinitions"
        ]
        Resource = "*"
      },
      # ECS Service Deployment
      {
        Sid    = "ECSServiceDeploy"
        Effect = "Allow"
        Action = [
          "ecs:DescribeServices",
          "ecs:UpdateService",
          "ecs:DescribeTasks",
          "ecs:ListTasks"
        ]
        Resource = "*"
      },
      # IAM PassRole for ECS Task Execution
      {
        Sid    = "PassRoleForECS"
        Effect = "Allow"
        Action = "iam:PassRole"
        Resource = compact([
          var.ecs_task_execution_role_arn,
          var.ecs_task_role_arn
        ])
        Condition = {
          StringEquals = {
            "iam:PassedToService" = "ecs-tasks.amazonaws.com"
          }
        }
      }
    ]
  })
}

# ============================================================================
# GitHub Actions Role for Frontend Deployment (S3 + CloudFront)
# ============================================================================

resource "aws_iam_role" "github_actions_frontend_deploy" {
  count       = var.enable_frontend_deploy ? 1 : 0
  name_prefix = "${var.project_name}-${var.environment}-gh-frontend-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = data.aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            # Allow workflow_run triggers from main branch, workflow_dispatch, and environment-based deployments
            "token.actions.githubusercontent.com:sub" = [
              "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/main",
              "repo:${var.github_org}/${var.github_repo}:environment:${var.github_environment}",
              "repo:${var.github_org}/${var.github_repo}:environment:staging"
            ]
          }
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-gh-frontend-deploy"
  })
}

resource "aws_iam_role_policy" "github_actions_frontend_deploy" {
  count       = var.enable_frontend_deploy ? 1 : 0
  name_prefix = "${var.project_name}-${var.environment}-frontend-deploy-"
  role        = aws_iam_role.github_actions_frontend_deploy[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # S3 bucket access for frontend deployment
      {
        Sid    = "S3FrontendDeploy"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          var.frontend_bucket_arn,
          "${var.frontend_bucket_arn}/*"
        ]
      },
      # CloudFront invalidation
      {
        Sid    = "CloudFrontInvalidation"
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation",
          "cloudfront:GetInvalidation",
          "cloudfront:ListInvalidations"
        ]
        Resource = var.frontend_cloudfront_distribution_arn != "" ? var.frontend_cloudfront_distribution_arn : "*"
      }
    ]
  })
}
