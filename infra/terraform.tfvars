# Copy this to terraform.tfvars and fill in values

# AWS Configuration
aws_region  = "us-east-1"
environment = "dev"
project_name = "hospital-management"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]
public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]

# EKS Configuration
eks_cluster_name = "hospital-cluster"
eks_cluster_version = "1.34"
eks_node_instance_type = "t3.micro"
eks_node_desired_size = 2
eks_node_min_size = 1
eks_node_max_size = 2

# RDS Configuration
rds_instance_class = "db.t3.micro"
rds_allocated_storage = 20
rds_database_name = "hospital_db"
rds_username = "postgres"
rds_password = "YourSecurePassword123!"  # CHANGE THIS!
rds_port = 5432

# S3 Configuration
s3_bucket_name = "hospital-static-files"

# EC2 Fallback
enable_ec2_fallback = false
ec2_instance_type = "t3.micro"
ec2_instance_count = 2