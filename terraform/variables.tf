variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "fastapi-memories-eks"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "github_org" {
  description = "GitHub Organization or Personal Username"
  type        = string
  default     = "kasisubbarayudu"
}

variable "github_repo" {
  description = "GitHub Repository Name"
  type        = string
  default     = "fastapi-project"
}

variable "node_instance_types" {
  description = "Instance types for EKS worker nodes"
  type        = list(string)
  default     = ["t3.micro"]
}

variable "desired_node_count" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "min_node_count" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 2
}

variable "max_node_count" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 2
}
