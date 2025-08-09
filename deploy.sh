#!/bin/bash

# SabjiGPT Production Deployment Script
# Usage: ./deploy.sh [platform]
# Platforms: railway, render, digitalocean, docker, vps

set -e

PLATFORM=${1:-"railway"}
PROJECT_NAME="sabji-gpt"

echo "🚀 Deploying SabjiGPT to $PLATFORM..."

# Check if git repo is clean
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  Working directory not clean. Committing changes..."
    git add .
    git commit -m "Production deployment prep"
fi

case $PLATFORM in
    "railway")
        echo "📡 Deploying to Railway..."
        echo "1. Go to https://railway.app"
        echo "2. Connect this GitHub repo"
        echo "3. Set environment variables:"
        echo "   AUTH_TOKEN=sabji_gpt_secret_2025"
        echo "   MCP_PORT=8087"
        echo "   SCRAPE_HEADLESS=true"
        echo "   LOG_LEVEL=INFO"
        echo "4. Railway will auto-deploy from main branch"
        ;;
        
    "render")
        echo "🎨 Deploying to Render..."
        echo "1. Go to https://render.com"
        echo "2. Create new web service from GitHub"
        echo "3. Use these settings:"
        echo "   Build: pip install -r requirements.txt && playwright install"
        echo "   Start: python run_automated_system.py --mcp-only"
        echo "   Environment: Python 3"
        echo "4. Add environment variables in Render dashboard"
        ;;
        
    "digitalocean")
        echo "🌊 Deploying to DigitalOcean..."
        echo "1. Install doctl CLI: https://docs.digitalocean.com/reference/doctl/"
        echo "2. Run: doctl apps create .do/app.yaml"
        echo "3. Update repo URL in .do/app.yaml first"
        ;;
        
    "docker")
        echo "🐳 Building Docker containers..."
        docker-compose build
        echo "✅ Built successfully!"
        echo ""
        echo "To run locally:"
        echo "  docker-compose up -d"
        echo ""
        echo "To deploy to cloud:"
        echo "  docker push your-registry/sabji-gpt"
        ;;
        
    "vps")
        echo "🖥️  VPS Deployment Instructions..."
        cat << EOF

VPS Deployment Steps:
===================

1. **SSH into your server:**
   ssh user@your-server.com

2. **Install dependencies:**
   sudo apt update
   sudo apt install python3 python3-pip git nginx certbot
   
3. **Clone repository:**
   git clone https://github.com/your-username/sabjiGPT.git
   cd sabjiGPT
   
4. **Setup environment:**
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install --with-deps
   
5. **Configure environment:**
   cp .env.example .env
   # Edit .env with your settings
   
6. **Setup systemd service:**
   sudo cp deploy/sabji-gpt.service /etc/systemd/system/
   sudo systemctl enable sabji-gpt
   sudo systemctl start sabji-gpt
   
7. **Setup Nginx:**
   sudo cp deploy/nginx.conf /etc/nginx/sites-available/sabji-gpt
   sudo ln -s /etc/nginx/sites-available/sabji-gpt /etc/nginx/sites-enabled/
   sudo systemctl reload nginx
   
8. **Setup SSL:**
   sudo certbot --nginx -d your-domain.com

EOF
        ;;
        
    *)
        echo "❌ Unknown platform: $PLATFORM"
        echo "Available platforms: railway, render, digitalocean, docker, vps"
        exit 1
        ;;
esac

echo ""
echo "📝 Don't forget to:"
echo "✅ Set up your domain name"
echo "✅ Configure environment variables"
echo "✅ Test the deployment"
echo "✅ Connect to Puch AI with your production URL"
echo ""
echo "🔗 Connection command for Puch AI:"
echo "/mcp connect https://your-domain.com/mcp sabji_gpt_secret_2025"
echo ""
echo "🎉 Deployment guide complete!"
