output "db_instance_id" {
  description = "ID of the database instance"
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "ARN of the database instance"
  value       = aws_db_instance.main.arn
}

output "db_endpoint" {
  description = "Connection endpoint for the database"
  value       = aws_db_instance.main.endpoint
}

output "db_address" {
  description = "Hostname of the database"
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "Port of the database"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "Name of the database"
  value       = aws_db_instance.main.db_name
}

output "db_username" {
  description = "Master username for the database"
  value       = var.db_username
  sensitive   = true
}

output "db_credentials_secret_arn" {
  description = "ARN of the Secrets Manager secret containing database credentials"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "db_credentials_secret_name" {
  description = "Name of the Secrets Manager secret containing database credentials"
  value       = aws_secretsmanager_secret.db_credentials.name
}

output "db_subnet_group_name" {
  description = "Name of the database subnet group"
  value       = aws_db_subnet_group.main.name
}

output "db_parameter_group_name" {
  description = "Name of the database parameter group"
  value       = aws_db_parameter_group.main.name
}
