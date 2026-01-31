output "bastion_public_ip" {
  description = "Public IP address of the bastion host"
  value       = aws_instance.bastion.public_ip
}

output "bastion_instance_id" {
  description = "Instance ID of the bastion host"
  value       = aws_instance.bastion.id
}

output "bastion_security_group_id" {
  description = "Security group ID of the bastion host"
  value       = aws_security_group.bastion.id
}

output "ssh_command" {
  description = "SSH command to connect to bastion"
  value       = "ssh -i ~/.ssh/wikivoice-bastion ec2-user@${aws_instance.bastion.public_ip}"
}

output "tunnel_command" {
  description = "SSH tunnel command for RDS access"
  value       = "ssh -i ~/.ssh/wikivoice-bastion -L 5432:<RDS_ENDPOINT>:5432 -N ec2-user@${aws_instance.bastion.public_ip}"
}
