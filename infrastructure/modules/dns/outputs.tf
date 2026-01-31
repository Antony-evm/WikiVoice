output "zone_id" {
  description = "Route53 zone ID"
  value       = local.zone_id
}

output "api_fqdn" {
  description = "Fully qualified domain name for API"
  value       = "${var.api_subdomain}.${var.domain_name}"
}

output "nameservers" {
  description = "Nameservers for the hosted zone (if created)"
  value       = var.create_hosted_zone ? aws_route53_zone.main[0].name_servers : null
}
