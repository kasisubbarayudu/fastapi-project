output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "eks_cluster_name" {
  description = "Name of the provisioned EKS cluster"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "Endpoint for the EKS cluster API"
  value       = module.eks.cluster_endpoint
}

output "github_actions_role_arn" {
  description = "IAM Role ARN to configure as AWS_ROLE_ARN secret in GitHub Actions"
  value       = aws_iam_role.github_oidc_role.arn
}

output "configure_kubectl_command" {
  description = "Command to configure kubectl locally"
  value       = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.aws_region}"
}
