# Security Group for Application Load Balancer
resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-${var.environment}-alb-"
  description = "Security group for Application Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-alb-sg"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name_prefix = "${var.project_name}-${var.environment}-ecs-tasks-"
  description = "Security group for ECS tasks"
  vpc_id      = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-ecs-tasks-sg"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# ECS ingress rule
resource "aws_security_group_rule" "ecs_ingress_from_alb" {
  type                     = "ingress"
  description              = "Allow traffic from ALB"
  from_port                = var.app_port
  to_port                  = var.app_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecs_tasks.id
  source_security_group_id = aws_security_group.alb.id
}

# ECS egress rules
resource "aws_security_group_rule" "ecs_egress_https" {
  type              = "egress"
  description       = "HTTPS for external APIs and package downloads"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.ecs_tasks.id
}

resource "aws_security_group_rule" "ecs_egress_http" {
  type              = "egress"
  description       = "HTTP for package repositories (if needed)"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.ecs_tasks.id
}

resource "aws_security_group_rule" "ecs_egress_rds" {
  type                     = "egress"
  description              = "PostgreSQL to RDS"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecs_tasks.id
  source_security_group_id = aws_security_group.rds.id
}

resource "aws_security_group_rule" "ecs_egress_dns" {
  type              = "egress"
  description       = "DNS queries"
  from_port         = 53
  to_port           = 53
  protocol          = "udp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.ecs_tasks.id
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-${var.environment}-rds-"
  description = "Security group for RDS database"
  vpc_id      = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-rds-sg"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# RDS ingress rule
resource "aws_security_group_rule" "rds_ingress_from_ecs" {
  type                     = "ingress"
  description              = "PostgreSQL from ECS tasks"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds.id
  source_security_group_id = aws_security_group.ecs_tasks.id
}

# RDS ingress from bastion (optional)
# Using enable_bastion_access boolean (known at plan time) instead of checking
# bastion_security_group_id value to avoid for_each issues with unknown values
resource "aws_security_group_rule" "rds_ingress_from_bastion" {
  for_each = var.enable_bastion_access ? toset(["bastion"]) : toset([])

  type                     = "ingress"
  description              = "PostgreSQL from bastion host"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds.id
  source_security_group_id = var.bastion_security_group_id
}

# RDS egress rule
resource "aws_security_group_rule" "rds_egress_all" {
  type              = "egress"
  description       = "Allow all outbound"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.rds.id
}

# IAM Role for ECS Task Execution (used by ECS agent)
resource "aws_iam_role" "ecs_task_execution" {
  name_prefix = "${var.project_name}-${var.environment}-ecs-exec-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# Attach AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional policy for Secrets Manager access
resource "aws_iam_role_policy" "ecs_task_execution_secrets" {
  name_prefix = "${var.project_name}-${var.environment}-secrets-"
  role        = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue",
          "kms:Decrypt"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# IAM Role for ECS Tasks (used by application code)
resource "aws_iam_role" "ecs_task" {
  name_prefix = "${var.project_name}-${var.environment}-ecs-task-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# Policy for ECS task role (customize based on app needs)
resource "aws_iam_role_policy" "ecs_task" {
  name_prefix = "${var.project_name}-${var.environment}-task-"
  role        = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${var.project_name}-${var.environment}-*/*"
        ]
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}
