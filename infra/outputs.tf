# ============ VPC OUTPUTS ============
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "VPC CIDR"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnets" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnets
}

output "private_subnets" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

# ============ EKS OUTPUTS ============
output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "eks_cluster_certificate_authority_data" {
  description = "EKS cluster certificate authority data"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "eks_cluster_security_group_id" {
  description = "EKS cluster security group ID"
  value       = module.eks.cluster_security_group_id
}

# ============ RDS OUTPUTS ============
output "rds_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_address" {
  description = "RDS address"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "RDS port"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.postgres.db_name
}

# ============ S3 OUTPUTS ============
output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.static_files.bucket
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.static_files.arn
}

# ============ SECURITY GROUPS ============
output "app_security_group_id" {
  description = "Application security group ID"
  value       = aws_security_group.app.id
}

output "rds_security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}

# ============ EC2 OUTPUTS (if enabled) ============
output "ec2_instance_public_ips" {
  description = "EC2 instance public IPs"
  value       = aws_instance.app_server[*].public_ip
}

output "ec2_instance_ids" {
  description = "EC2 instance IDs"
  value       = aws_instance.app_server[*].id
}

# ============ CONNECTION STRINGS ============
output "database_connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgresql://${var.rds_username}:${var.rds_password}@${aws_db_instance.postgres.endpoint}/${var.rds_database_name}"
  sensitive   = true
}



# ============ CLOUDFRONT URL (if enabled later) ============
output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = null  # Placeholder for future
}