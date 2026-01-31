output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "nat_gateway_ids" {
  description = "IDs of NAT Gateways"
  value       = aws_nat_gateway.main[*].id
}

output "nat_gateway_public_ips" {
  description = "Public IPs of NAT Gateways"
  value       = aws_eip.nat[*].public_ip
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "vpc_endpoint_s3_id" {
  description = "ID of the S3 VPC endpoint"
  value       = var.enable_vpc_endpoints ? aws_vpc_endpoint.s3[0].id : null
}

output "vpc_endpoint_ecr_api_id" {
  description = "ID of the ECR API VPC endpoint"
  value       = var.enable_vpc_endpoints ? aws_vpc_endpoint.ecr_api[0].id : null
}

output "vpc_endpoint_ecr_dkr_id" {
  description = "ID of the ECR DKR VPC endpoint"
  value       = var.enable_vpc_endpoints ? aws_vpc_endpoint.ecr_dkr[0].id : null
}

output "vpc_endpoint_secretsmanager_id" {
  description = "ID of the Secrets Manager VPC endpoint"
  value       = var.enable_vpc_endpoints ? aws_vpc_endpoint.secretsmanager[0].id : null
}

output "vpc_endpoints_security_group_id" {
  description = "ID of the VPC endpoints security group"
  value       = var.enable_vpc_endpoints ? aws_security_group.vpc_endpoints[0].id : null
}
