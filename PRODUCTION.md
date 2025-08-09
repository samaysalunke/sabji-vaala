# 🚀 SabjiGPT Production Deployment Guide

## 🎯 Quick Start (Recommended)

### **Option 1: Railway (Easiest)**
```bash
# 1. Push your code to GitHub
git add .
git commit -m "Ready for production"
git push

# 2. Go to https://railway.app
# 3. Connect your GitHub repo
# 4. Set environment variables:
#    AUTH_TOKEN=sabji_gpt_secret_2025
#    MCP_PORT=8087
#    SCRAPE_HEADLESS=true
# 5. Deploy automatically!
```

**Railway URL**: `https://your-project.railway.app`

### **Option 2: Render (Great for Web Services)**
```bash
# 1. Go to https://render.com
# 2. Create Web Service from GitHub
# 3. Settings:
#    Build: pip install -r requirements.txt && playwright install
#    Start: python run_automated_system.py --mcp-only
# 4. Add environment variables
# 5. Deploy!
```

**Render URL**: `https://your-service.onrender.com`

## 🔧 Deployment Options

### **1. Cloud Platforms**

| Platform | Difficulty | Cost | Auto-scaling | SSL |
|----------|------------|------|--------------|-----|
| Railway | ⭐ Easy | $5/month | ✅ Yes | ✅ Auto |
| Render | ⭐ Easy | $7/month | ✅ Yes | ✅ Auto |
| DigitalOcean | ⭐⭐ Medium | $12/month | ✅ Yes | ✅ Auto |
| Heroku | ⭐ Easy | $7/month | ✅ Yes | ✅ Auto |

### **2. VPS/Self-hosted**

| Platform | Difficulty | Cost | Control | SSL |
|----------|------------|------|---------|-----|
| DigitalOcean Droplet | ⭐⭐⭐ Hard | $6/month | 🔥 Full | 🔧 Manual |
| AWS EC2 | ⭐⭐⭐⭐ Expert | $10/month | 🔥 Full | 🔧 Manual |
| Linode | ⭐⭐⭐ Hard | $5/month | 🔥 Full | 🔧 Manual |

## 🚀 Step-by-Step: Railway Deployment

### **1. Prepare Your Code**
```bash
# Ensure everything is committed
git status
git add .
git commit -m "Production ready"
git push origin main
```

### **2. Deploy to Railway**
1. **Sign up**: Go to [railway.app](https://railway.app)
2. **Connect GitHub**: Link your repository
3. **Auto-deploy**: Railway detects Python automatically
4. **Set Environment Variables**:
   ```
   AUTH_TOKEN=your_secure_token_here
   MCP_PORT=8087
   SCRAPE_HEADLESS=true
   LOG_LEVEL=INFO
   ```

### **3. Get Your Production URL**
- Railway provides: `https://sabji-gpt.railway.app`
- Custom domain: Link your own domain in settings

### **4. Test Production**
```bash
# Health check
curl https://sabji-gpt.railway.app/health

# MCP endpoint
curl -H "Authorization: Bearer your_token" \
     https://sabji-gpt.railway.app/mcp
```

## 🌐 Connect to Puch AI

### **Production Connection**
```
/mcp connect https://sabji-gpt.railway.app/mcp your_secure_token_here
```

### **Test Commands**
Once connected, try these in Puch AI:
- "What's the current price of onions in Mumbai?"
- "Compare tomato prices across Indian cities"
- "Show me vegetable prices in Delhi"
- "What are the latest market trends?"

## 🔒 Security Best Practices

### **1. Environment Variables**
```bash
# Generate a secure token
AUTH_TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Set in your platform's environment settings
AUTH_TOKEN=your_generated_secure_token
MCP_PORT=8087
SCRAPE_HEADLESS=true
LOG_LEVEL=INFO
DATABASE_PATH=/app/data/mandi_prices.db
```

### **2. Rate Limiting**
The MCP server includes built-in rate limiting. For additional protection:
- Use Cloudflare (free tier)
- Enable platform-level DDoS protection
- Monitor usage patterns

### **3. Monitoring**
```bash
# Health checks every 30 seconds
curl -f https://your-domain.com/health || alert

# Log monitoring (platform-specific)
# Railway: Built-in logs
# Render: Built-in logs  
# VPS: systemd journal
```

## 📊 Production Monitoring

### **Available Endpoints**
```bash
# Health check
GET /health

# Root info
GET /

# MCP protocol
POST /mcp
```

### **Database Stats**
```bash
# Get database statistics
curl -H "Authorization: Bearer token" \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_market_trends","arguments":{}},"id":"1"}' \
     https://your-domain.com/mcp
```

## 🐳 Docker Deployment

### **Local Testing**
```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Test endpoints
curl http://localhost:8087/health
```

### **Production Docker**
```bash
# Build for production
docker build -t sabji-gpt:latest .

# Run with environment
docker run -d \
  --name sabji-gpt \
  -p 8087:8087 \
  -e AUTH_TOKEN=your_token \
  -e SCRAPE_HEADLESS=true \
  -v $(pwd)/data:/app/data \
  sabji-gpt:latest
```

## 🖥️ VPS Deployment (Advanced)

### **Full Setup Script**
```bash
#!/bin/bash
# Run on Ubuntu 20.04+ VPS

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Create user and directory
sudo useradd -m -s /bin/bash sabji
sudo mkdir -p /opt/sabjiGPT
sudo chown sabji:sabji /opt/sabjiGPT

# Switch to sabji user
sudo -u sabji bash << 'EOF'
cd /opt/sabjiGPT

# Clone repository
git clone https://github.com/samaysalunke/sabji-vaala.git .

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install --with-deps

# Create data directory
mkdir -p data
EOF

# Install systemd service
sudo cp deploy/sabji-gpt.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sabji-gpt
sudo systemctl start sabji-gpt

# Setup Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/sabji-gpt
sudo ln -s /etc/nginx/sites-available/sabji-gpt /etc/nginx/sites-enabled/
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

echo "✅ SabjiGPT deployed successfully!"
echo "🌐 Access at: https://your-domain.com"
```

## 🔄 Automated Deployment

### **GitHub Actions** (Optional)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          # Railway CLI deployment
          npm install -g @railway/cli
          railway login --browserless
          railway up
```

## 📈 Scaling Considerations

### **Traffic Growth**
- **Small**: Railway/Render (< 1000 requests/day)
- **Medium**: DigitalOcean App Platform (< 10k requests/day)  
- **Large**: Multiple instances + Load balancer (> 10k requests/day)

### **Database Scaling**
- **SQLite**: Good for < 100GB data
- **PostgreSQL**: Upgrade when you need advanced queries
- **Backup Strategy**: Daily automated backups

### **Cost Optimization**
```bash
# Monitor usage
- Set up alerts for high CPU/memory
- Use platform auto-scaling
- Archive old price data (> 30 days)
```

## 🚨 Troubleshooting

### **Common Issues**

1. **Playwright Installation Fails**
   ```bash
   # On deployment platform, use:
   playwright install --with-deps chromium
   ```

2. **Database Permission Errors**
   ```bash
   # Ensure data directory is writable
   mkdir -p data
   chmod 755 data
   ```

3. **MCP Authentication Fails**
   ```bash
   # Check environment variables
   echo $AUTH_TOKEN
   
   # Test with curl
   curl -H "Authorization: Bearer $AUTH_TOKEN" \
        https://your-domain.com/mcp
   ```

4. **Scraper Timeouts**
   ```bash
   # Increase timeout in .env
   SCRAPE_TIMEOUT=60000
   ```

## ✅ Production Checklist

- [ ] Code pushed to GitHub
- [ ] Environment variables configured
- [ ] Health check endpoint working
- [ ] SSL certificate installed
- [ ] Domain name configured
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Puch AI connection tested
- [ ] Performance tested
- [ ] Error logging configured

## 🎉 Success!

Your SabjiGPT is now running in production! 

**Next steps:**
1. Test all MCP tools with Puch AI
2. Monitor performance and logs  
3. Set up alerts for issues
4. Scale as needed based on usage

**Connect with Puch AI:**
```
/mcp connect https://your-domain.com/mcp your_secure_token
```

**Happy vegetable price checking! 🥬📊**
