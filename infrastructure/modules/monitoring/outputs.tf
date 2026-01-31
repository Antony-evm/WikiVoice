output "autoscaling_target_id" {
  description = "ID of the auto scaling target"
  value       = aws_appautoscaling_target.ecs_service.id
}

output "cpu_scaling_policy_arn" {
  description = "ARN of the CPU scaling policy"
  value       = var.enable_cpu_scaling ? aws_appautoscaling_policy.ecs_cpu[0].arn : null
}

output "memory_scaling_policy_arn" {
  description = "ARN of the memory scaling policy"
  value       = var.enable_memory_scaling ? aws_appautoscaling_policy.ecs_memory[0].arn : null
}

output "alb_request_scaling_policy_arn" {
  description = "ARN of the ALB request count scaling policy"
  value       = var.enable_alb_request_scaling ? aws_appautoscaling_policy.ecs_alb_requests[0].arn : null
}

output "dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = var.enable_cloudwatch_dashboard ? aws_cloudwatch_dashboard.main[0].dashboard_name : null
}

output "alarm_arns" {
  description = "ARNs of all CloudWatch alarms"
  value = var.enable_cloudwatch_alarms ? {
    ecs_cpu_high      = aws_cloudwatch_metric_alarm.ecs_cpu_high[0].arn
    ecs_memory_high   = aws_cloudwatch_metric_alarm.ecs_memory_high[0].arn
    alb_response_time = aws_cloudwatch_metric_alarm.alb_response_time[0].arn
    alb_4xx_errors    = aws_cloudwatch_metric_alarm.alb_4xx_errors[0].arn
    alb_5xx_errors    = aws_cloudwatch_metric_alarm.alb_5xx_errors[0].arn
    alb_healthy_hosts = aws_cloudwatch_metric_alarm.alb_healthy_hosts[0].arn
  } : {}
}
