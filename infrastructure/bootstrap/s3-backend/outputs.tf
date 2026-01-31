output "state_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.id
}

output "state_bucket_arn" {
  description = "ARN of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.arn
}

output "state_bucket_region" {
  description = "Region of the S3 bucket"
  value       = aws_s3_bucket.terraform_state.region
}

output "backend_config" {
  description = "Backend configuration for use in other Terraform projects"
  value       = <<-EOT
    terraform {
      backend "s3" {
        bucket = "${aws_s3_bucket.terraform_state.id}"
        key    = "path/to/your/terraform.tfstate"
        region = "${aws_s3_bucket.terraform_state.region}"
      }
    }
  EOT
}
