terraform {
  backend "s3" {
    bucket = "fastapi-demo-bucket-jul"
    key    = "statefiledir/terraform.tfstate"
    region = "ap-south-1"
  }

  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}






provider "aws" {
  region = var.aws_region

}



data "aws_availability_zones" "available" {
  state = "available"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.cluster_name}-vpc"
  cidr = var.vpc_cidr

  azs             = slice(data.aws_availability_zones.available.names, 0, 2)
  private_subnets = [cidrsubnet(var.vpc_cidr, 8, 1), cidrsubnet(var.vpc_cidr, 8, 2)]
  public_subnets  = [cidrsubnet(var.vpc_cidr, 8, 101), cidrsubnet(var.vpc_cidr, 8, 102)]

  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  }

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = ">= 20.0"

  name               = var.cluster_name
  kubernetes_version = "1.34"

  endpoint_public_access = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  addons = {
    coredns    = {}
    kube-proxy = {}
    vpc-cni = {
      before_compute = true
    }
  }

  enable_cluster_creator_admin_permissions = true

  access_entries = {
    github_actions = {
      principal_arn = aws_iam_role.github_oidc_role.arn
      policy_associations = {
        admin = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
      }
    }
  }

  eks_managed_node_groups = {
    main = {
      min_size       = var.min_node_count
      max_size       = var.max_node_count
      desired_size   = var.desired_node_count
      instance_types = var.node_instance_types
      capacity_type  = "ON_DEMAND"
    }
  }

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}
