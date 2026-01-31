variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where bastion will be created"
  type        = string
}

variable "public_subnet_id" {
  description = "Public subnet ID for bastion host"
  type        = string
}

variable "rds_security_group_id" {
  description = "RDS security group ID to allow access to"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type for bastion host"
  type        = string
  default     = "t3.micro"
}

variable "bastion_public_key" {
  description = "SSH public key for bastion host access"
  type        = string
}

variable "allowed_ssh_cidr_blocks" {
  description = "CIDR blocks allowed to SSH to bastion"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
