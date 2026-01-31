# WikiVoice Infrastructure

Terraform Infrastructure as Code (IaC) for WikiVoice AWS deployment.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              AWS Cloud                                  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                         CloudFront                                 │  │
│  │                    (CDN + SSL Termination)                        │  │
│  └─────────────────────────┬─────────────────────────────────────────┘  │
│                            │                                            │
│  ┌─────────────────────────┴─────────────────────────────────────────┐  │
│  │                          WAF                                       │  │
│  │               (Web Application Firewall)                          │  │
│  └─────────────────────────┬─────────────────────────────────────────┘  │
│                            │                                            │
│  ┌─────────────────────────┴─────────────────────────────────────────┐  │
│  │                     Application Load Balancer                     │  │
│  └─────────────────────────┬─────────────────────────────────────────┘  │
│                            │                                            │
│  ┌─────────────────────────┴─────────────────────────────────────────┐  │
│  │                        VPC (10.0.0.0/16)                          │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │                    Public Subnets                            │  │  │
│  │  │    ┌─────────────┐           ┌─────────────┐                │  │  │
│  │  │    │   NAT GW    │           │   Bastion   │                │  │  │
│  │  │    └─────────────┘           └─────────────┘                │  │  │
│  │  └─────────────────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │                   Private Subnets                            │  │  │
│  │  │    ┌─────────────┐           ┌─────────────┐                │  │  │
│  │  │    │ ECS Fargate │           │     RDS     │                │  │  │
│  │  │    │  (Backend)  │           │ (PostgreSQL)│                │  │  │
│  │  │    └─────────────┘           └─────────────┘                │  │  │
│  │  └─────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                          S3 Bucket                                 │  │
│  │                    (Frontend Static Files)                        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📁 Structure

```
infrastructure/
├── modules/           # Reusable Terraform modules
│   ├── bastion/       # Bastion host for SSH access
│   ├── cicd/          # CI/CD IAM roles
│   ├── cloudfront/    # CDN configuration
│   ├── database/      # RDS PostgreSQL
│   ├── dns/           # Route 53 DNS
│   ├── ecr/           # Container registry
│   ├── ecs/           # ECS Fargate service
│   ├── frontend/      # S3 bucket for frontend
│   ├── monitoring/    # CloudWatch alarms
│   ├── networking/    # VPC, subnets, NAT
│   ├── security/      # Security groups, IAM
│   └── waf/           # Web Application Firewall
├── environments/
│   └── prod/          # Production environment
└── bootstrap/         # Initial AWS account setup
```

## 🚀 Getting Started

### Prerequisites

- Terraform 1.13+
- AWS CLI configured
- Appropriate AWS permissions

### Initial Setup

1. **Bootstrap** (first time only):
```bash
cd bootstrap
terraform init
terraform apply
```

2. **Deploy Infrastructure**:
```bash
cd environments/prod
terraform init
terraform plan
terraform apply
```

## ⚙️ Configuration

### Required Secrets (GitHub Actions)

| Secret | Description |
|--------|-------------|
| `AWS_ROLE_TO_ASSUME_PLAN` | IAM role ARN for Terraform plan |
| `AWS_ROLE_TO_ASSUME_APPLY` | IAM role ARN for Terraform apply |
| `TF_VAR_STYTCH_SECRET_ARN` | Stytch secret ARN in Secrets Manager |
| `ACM_CERTIFICATE_ARN` | ACM certificate ARN for HTTPS |
| `TF_VAR_BASTION_PUBLIC_KEY` | SSH public key for bastion |

### Terraform Variables

Key variables in `environments/prod/terraform.tfvars`:

```hcl
project_name = "wikivoice"
environment  = "prod"
aws_region   = "eu-west-2"

# Networking
vpc_cidr             = "10.0.0.0/16"
availability_zones   = ["eu-west-2a", "eu-west-2b"]

# ECS
ecs_cpu    = 512
ecs_memory = 1024
min_tasks  = 1
max_tasks  = 4

# Database
db_instance_class = "db.t3.micro"
```

## 🔧 Common Operations

### View Current State
```bash
cd environments/prod
terraform show
```

### Plan Changes
```bash
terraform plan -out=tfplan
```

### Apply Changes
```bash
terraform apply tfplan
```

### Destroy (⚠️ Caution)
```bash
terraform destroy
```

### Import Existing Resource
```bash
terraform import module.networking.aws_vpc.main vpc-12345678
```

## 📊 Outputs

After applying, useful outputs include:

| Output | Description |
|--------|-------------|
| `alb_dns_name` | Load balancer DNS name |
| `cloudfront_domain` | CloudFront distribution domain |
| `rds_endpoint` | RDS database endpoint |
| `ecr_repository_url` | ECR repository URL |

## 🔐 Security Notes

- All secrets are stored in AWS Secrets Manager
- Database is in private subnets (no public access)
- Bastion host requires SSH key authentication
- WAF protects against common attacks
- All traffic encrypted with TLS

## 🔄 CI/CD Integration

Infrastructure changes are managed via GitHub Actions:

1. **PR Created**: `terraform-plan.yml` runs and comments plan
2. **PR Merged**: `terraform-apply.yml` applies changes

See `.github/workflows/terraform-*.yml` for details.

## 📄 License

Private - All rights reserved.
