#!/bin/bash

# Kernel Builder Telegram Bot Deployment Script
# This script helps deploy the bot in various environments

set -e

echo "🔧 Kernel Builder Bot Deployment Script"
echo "========================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install dependencies
install_dependencies() {
    echo "📦 Installing Python dependencies..."
    if command_exists pip3; then
        pip3 install -r requirements.txt
    elif command_exists pip; then
        pip install -r requirements.txt
    else
        echo "❌ Error: pip not found. Please install Python pip first."
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
}

# Function to setup environment
setup_environment() {
    echo "🔧 Setting up environment..."
    
    if [ ! -f .env ]; then
        echo "📝 Creating .env file from template..."
        cp .env.example .env
        echo "⚠️  Please edit .env file with your actual tokens before running the bot"
        echo "   Required: TELEGRAM_BOT_TOKEN, GITHUB_TOKEN"
    else
        echo "✅ .env file already exists"
    fi
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    python3 test_bot.py
    echo "✅ Tests completed"
}

# Function to create systemd service
create_systemd_service() {
    local service_name="kernel-builder-bot"
    local service_file="/etc/systemd/system/${service_name}.service"
    local current_dir=$(pwd)
    local current_user=$(whoami)
    
    echo "🔧 Creating systemd service..."
    
    # Check if running as root or with sudo
    if [ "$EUID" -ne 0 ]; then
        echo "⚠️  Creating systemd service requires root privileges"
        echo "   Run: sudo $0 systemd"
        return 1
    fi
    
    cat > "$service_file" << EOF
[Unit]
Description=Kernel Builder Telegram Bot
After=network.target

[Service]
Type=simple
User=$current_user
WorkingDirectory=$current_dir
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10
Environment=PATH=/usr/bin:/usr/local/bin
EnvironmentFile=$current_dir/.env

[Install]
WantedBy=multi-user.target
EOF

    echo "✅ Systemd service created at $service_file"
    echo "🔧 Enabling and starting service..."
    
    systemctl daemon-reload
    systemctl enable "$service_name"
    
    echo "✅ Service enabled. To start the service, run:"
    echo "   sudo systemctl start $service_name"
    echo "   sudo systemctl status $service_name"
}

# Function to create Docker setup
create_docker_setup() {
    echo "🐳 Creating Docker setup..."
    
    # Create Dockerfile
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Run the bot
CMD ["python", "bot.py"]
EOF

    # Create docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  kernel-builder-bot:
    build: .
    container_name: kernel-builder-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
EOF

    # Create .dockerignore
    cat > .dockerignore << 'EOF'
.env
.git
.gitignore
README.md
*.log
__pycache__
*.pyc
.pytest_cache
EOF

    echo "✅ Docker setup created"
    echo "📝 To build and run with Docker:"
    echo "   docker-compose up -d"
    echo "   docker-compose logs -f"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     Install dependencies and setup environment"
    echo "  test        Run tests"
    echo "  systemd     Create systemd service (requires root)"
    echo "  docker      Create Docker setup files"
    echo "  start       Start the bot directly"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install    # Install and setup"
    echo "  $0 test       # Run tests"
    echo "  $0 start      # Start bot"
}

# Main script logic
case "${1:-install}" in
    "install")
        install_dependencies
        setup_environment
        echo ""
        echo "🎉 Installation complete!"
        echo "📝 Next steps:"
        echo "   1. Edit .env file with your tokens"
        echo "   2. Run: $0 test"
        echo "   3. Run: $0 start"
        ;;
    
    "test")
        run_tests
        ;;
    
    "systemd")
        create_systemd_service
        ;;
    
    "docker")
        create_docker_setup
        ;;
    
    "start")
        echo "🚀 Starting Kernel Builder Bot..."
        if [ ! -f .env ]; then
            echo "❌ Error: .env file not found"
            echo "   Run: $0 install"
            exit 1
        fi
        
        # Check if required environment variables are set
        source .env
        if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$GITHUB_TOKEN" ]; then
            echo "❌ Error: Required environment variables not set"
            echo "   Please edit .env file with your tokens"
            exit 1
        fi
        
        python3 bot.py
        ;;
    
    "help"|"-h"|"--help")
        show_usage
        ;;
    
    *)
        echo "❌ Unknown command: $1"
        show_usage
        exit 1
        ;;
esac

