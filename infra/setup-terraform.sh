#!/bin/bash
echo "🚀 Setting up Terraform for Hospital Management System"

# Initialize Terraform
echo "1. Initializing Terraform..."
terraform init

# Create terraform.tfvars if it doesn't exist
if [ ! -f terraform.tfvars ]; then
    echo "2. Creating terraform.tfvars from example..."
    cp terraform.tfvars.example terraform.tfvars
    echo "⚠️  Please edit terraform.tfvars with your values before proceeding!"
    echo "   Important: Set rds_password and other sensitive values"
    exit 1
fi

# Validate configuration
echo "3. Validating Terraform configuration..."
terraform validate

# Plan infrastructure
echo "4. Creating execution plan..."
terraform plan -out=tfplan

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review the plan: terraform show tfplan"
echo "2. Apply: terraform apply tfplan"
echo "3. Check outputs: terraform output"
echo ""
echo "⚠️  WARNING: This will create AWS resources that may incur costs!"