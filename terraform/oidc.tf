# creates identity provider in iam and tells sts to accept tokens signed by github actions oauth server...
module "github_oidc_provider" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-oidc-provider"
  version = "6.6.1"

  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}


# Iam policy for accessing eks...
resource "aws_iam_policy" "github_actions_eks_policy" {
  name        = "GitHubActionsEKSDeployPolicy"
  description = "Policy allowing GitHub Actions to describe and access EKS cluster"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "eks:DescribeCluster",
          "eks:ListClusters"
        ]
        Resource = "*"
      }
    ]
  })
}


# Trust policy...
data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    sid     = "GithubOidcAuth"
    effect  = "Allow"
    actions = [
      "sts:AssumeRoleWithWebIdentity",
      "sts:TagSession"
    ]

    principals {
      type        = "Federated"
      identifiers = [module.github_oidc_provider.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_org}*/${var.github_repo}*"]
    }
  }
}


# Iam role for github actions...
resource "aws_iam_role" "github_oidc_role" {
  name               = "github-actions-eks-deployer"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}


# Attaching policy to github actions iam role...
resource "aws_iam_role_policy_attachment" "github_actions_eks" {
  role       = aws_iam_role.github_oidc_role.name
  policy_arn = aws_iam_policy.github_actions_eks_policy.arn
}
