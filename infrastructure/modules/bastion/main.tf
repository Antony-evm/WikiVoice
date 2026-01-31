# Get latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security Group for Bastion Host
resource "aws_security_group" "bastion" {
  name_prefix = "${var.project_name}-${var.environment}-bastion-"
  description = "Security group for bastion host"
  vpc_id      = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-bastion-sg"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# Allow SSH from specified IP addresses
resource "aws_security_group_rule" "bastion_ssh_ingress" {
  type              = "ingress"
  description       = "SSH from allowed IPs"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = var.allowed_ssh_cidr_blocks
  security_group_id = aws_security_group.bastion.id
}

# Allow outbound to RDS
resource "aws_security_group_rule" "bastion_rds_egress" {
  type                     = "egress"
  description              = "PostgreSQL to RDS"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.bastion.id
  source_security_group_id = var.rds_security_group_id
}

# Allow outbound HTTPS for updates
resource "aws_security_group_rule" "bastion_https_egress" {
  type              = "egress"
  description       = "HTTPS for package updates"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.bastion.id
}

# Allow outbound HTTP for updates
resource "aws_security_group_rule" "bastion_http_egress" {
  type              = "egress"
  description       = "HTTP for package updates"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.bastion.id
}

# Create SSH Key Pair
resource "aws_key_pair" "bastion" {
  key_name_prefix = "${var.project_name}-${var.environment}-bastion-"
  public_key      = var.bastion_public_key

  tags = var.tags
}

# Bastion EC2 Instance
resource "aws_instance" "bastion" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  subnet_id                   = var.public_subnet_id
  vpc_security_group_ids      = [aws_security_group.bastion.id]
  key_name                    = aws_key_pair.bastion.key_name
  associate_public_ip_address = true

  # Enable detailed monitoring
  monitoring = false

  # Root volume configuration
  # Note: Amazon Linux 2023 requires minimum 30GB (their AMI snapshot size)
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 30
    delete_on_termination = true
    encrypted             = true
  }

  user_data = <<-EOF
              #!/bin/bash
              # Update system
              yum update -y

              # Install PostgreSQL client for testing connections
              yum install -y postgresql15

              # Configure automatic security updates
              yum install -y yum-cron
              systemctl enable yum-cron
              systemctl start yum-cron
              EOF

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-bastion"
    }
  )

  lifecycle {
    ignore_changes = [
      ami,
      user_data
    ]
  }
}
