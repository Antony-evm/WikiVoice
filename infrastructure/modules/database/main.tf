# Generate random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
  # Avoid characters that might cause issues in connection strings
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Store database credentials in Secrets Manager
resource "aws_secretsmanager_secret" "db_credentials" {
  name_prefix             = "${var.project_name}-${var.environment}-db-credentials-"
  description             = "Database credentials for ${var.project_name} ${var.environment}"
  recovery_window_in_days = var.secret_recovery_window_days

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-db-credentials"
    }
  )
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id     = aws_secretsmanager_secret.db_credentials.id
  secret_string = "postgresql+asyncpg://${var.db_username}:${random_password.db_password.result}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${var.db_name}"
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name_prefix = "${var.project_name}-${var.environment}-"
  description = "Database subnet group for ${var.project_name} ${var.environment}"
  subnet_ids  = var.private_subnet_ids

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-db-subnet-group"
    }
  )
}

# DB Parameter Group
resource "aws_db_parameter_group" "main" {
  name_prefix = "${var.project_name}-${var.environment}-"
  family      = var.db_parameter_group_family
  description = "Parameter group for ${var.project_name} ${var.environment}"

  # Using minimal parameters to avoid static parameter issues
  # Additional tuning can be done manually in RDS console if needed

  tags = var.tags

  lifecycle {
    create_before_destroy = true
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier_prefix = "${var.project_name}-${var.environment}-"

  # Engine configuration
  engine            = "postgres"
  engine_version    = var.db_engine_version
  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  storage_type      = var.db_storage_type
  storage_encrypted = true
  kms_key_id        = var.kms_key_id

  # Database configuration
  db_name  = var.db_name
  username = var.db_username
  password = random_password.db_password.result
  port     = 5432

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.db_security_group_id]
  publicly_accessible    = false
  multi_az               = var.db_multi_az

  # Backup configuration
  backup_retention_period   = var.backup_retention_days
  backup_window             = var.backup_window
  maintenance_window        = var.maintenance_window
  copy_tags_to_snapshot     = true
  delete_automated_backups  = false
  skip_final_snapshot       = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.project_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Performance and monitoring
  enabled_cloudwatch_logs_exports       = ["postgresql", "upgrade"]
  performance_insights_enabled          = var.enable_performance_insights
  performance_insights_retention_period = var.enable_performance_insights ? var.performance_insights_retention_days : null

  # Parameter and option groups
  parameter_group_name = aws_db_parameter_group.main.name

  # Upgrade and maintenance
  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  apply_immediately          = var.apply_immediately
  deletion_protection        = var.deletion_protection

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-postgres"
    }
  )

  lifecycle {
    ignore_changes = [
      password, # Password managed by Secrets Manager
      final_snapshot_identifier
    ]
  }
}

# CloudWatch alarms for database monitoring
resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  count = var.enable_cloudwatch_alarms ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-db-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors RDS CPU utilization"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "database_storage" {
  count = var.enable_cloudwatch_alarms ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-db-storage-space"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "2147483648" # 2GB in bytes
  alarm_description   = "This metric monitors RDS free storage space"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "database_memory" {
  count = var.enable_cloudwatch_alarms ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-db-freeable-memory"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "134217728" # 128MB in bytes
  alarm_description   = "This metric monitors RDS freeable memory"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "database_connections" {
  count = var.enable_cloudwatch_alarms ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-db-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.db_max_connections * 0.8 # 80% of max connections
  alarm_description   = "This metric monitors RDS database connections"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = var.tags
}
