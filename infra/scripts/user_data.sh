#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
apt-get install -y docker.io docker-compose

# Install Python and dependencies
apt-get install -y python3 python3-pip python3-venv

# Clone application (in production, use your actual repo)
# git clone https://github.com/your-username/hospital-management-system.git
# cd hospital-management-system

# Create environment file
cat > .env << EOF
DB_HOST=${db_host}
DB_NAME=${db_name}
DB_USER=${db_user}
DB_PASSWORD=${db_password}
FLASK_ENV=production
EOF

# Run with Docker Compose
# docker-compose up -d

# Enable auto-start on boot
systemctl enable docker
# Add to crontab for auto-restart if needed

echo "Setup complete!"