# 🌟 SabjiGPT Complete Setup Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install all dependencies (including new scheduling libraries)
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 2. Environment Setup
Environment file `.env` is already created with:
```bash
AUTH_TOKEN=sabji_gpt_secret_2025
MY_NUMBER=919876543210
# ... other configurations
```

### 3. Test the System
```bash
# Test scraper functionality
python run_automated_system.py --test-scrape

# Expected output:
# ✅ Test SUCCESSFUL!
#    Price: ₹2.0/kg
#    Market: Onion
#    Source: agmarknet.gov.in
```

## 🎯 Usage Options

### Option 1: Complete System (Recommended)
```bash
# Runs both scheduler (9AM & 6PM) AND MCP server
python run_automated_system.py

# Output:
# 🌟 Starting COMPLETE SYSTEM
# 📅 Automated Scraping: 9:00 AM & 6:00 PM daily
# 🔌 MCP Server: http://0.0.0.0:8087
# 🔑 Auth Token: sabji_gpt_secret_2025
```

### Option 2: MCP Server Only
```bash
# For Puch AI integration without scheduling
python run_automated_system.py --mcp-only
```

### Option 3: Scheduler Only
```bash
# For automated data collection without MCP
python run_automated_system.py --scheduler-only
```

### Option 4: Individual Components
```bash
# Run original API server (port 8000)
python src/api/main.py

# Run MCP server directly (port 8087)
python src/mcp/sabji_mcp_server.py

# Run scheduler manually
python src/scheduler/automated_scraper.py
```

## 🌐 Puch AI Integration

### Step 1: Expose Server Publicly
```bash
# Install ngrok (if not already)
# Download from: https://ngrok.com/download

# Get your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_AUTHTOKEN

# Expose MCP server
ngrok http 8087

# Example output:
# Forwarding: https://abc123.ngrok.app -> http://localhost:8087
```

### Step 2: Connect to Puch AI
```bash
# In Puch AI chat:
/mcp connect https://abc123.ngrok.app/mcp sabji_gpt_secret_2025

# Success message:
# ✅ Connected to SabjiGPT MCP Server
# 🛠️ Available tools: 4
```

### Step 3: Test Integration
Ask Puch AI:
- "What's the price of onions in Mumbai?"
- "Compare tomato prices across cities"
- "Show me all vegetable prices in Delhi"
- "What are the market trends?"

## 📊 System Architecture

```
┌─────────────────────┐
│   Puch AI           │
│   User Interface    │
└─────────┬───────────┘
          │ MCP Protocol (HTTPS)
          │ Bearer Token Auth
          │
┌─────────▼───────────┐    ┌─────────────────────┐
│   MCP Server        │    │   Scheduler         │
│   Port 8087         │    │   9AM & 6PM Daily   │
│   4 Tools           │    │   24 Combinations   │
└─────────┬───────────┘    └─────────┬───────────┘
          │                          │
          │                          │
          ▼                          ▼
┌─────────────────────────────────────────────────┐
│              Core Components                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Scraper   │ │  Database   │ │    Cache    ││
│  │  (Working)  │ │  (SQLite)   │ │   (5 min)   ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐
│   Agmarknet.gov.in  │
│   Live Price Data   │
└─────────────────────┘
```

## 🛠️ Available MCP Tools

1. **get_vegetable_price**
   - Get live prices for specific vegetable in a city
   - Example: "Get onion price in Mumbai"

2. **get_city_prices**  
   - Get all vegetable prices for a city
   - Example: "Show all prices in Delhi"

3. **compare_vegetable_prices**
   - Compare prices across multiple cities
   - Example: "Compare tomato prices"

4. **get_market_trends**
   - Get market insights and database stats
   - Example: "Show market trends"

## 📅 Automated Scheduling

### Data Collection Schedule
- **9:00 AM Daily**: Morning market price collection
- **6:00 PM Daily**: Evening market updates

### Target Combinations (24 total)
- **Cities**: Mumbai, Delhi, Pune, Bengaluru, Hyderabad, Chennai, Kolkata, Ahmedabad
- **Vegetables**: Tomato, Onion, Potato
- **Markets**: All available markets per city

### Data Flow
1. **Scheduled Run** → Scrape 24 combinations
2. **Live Data Found** → Store in database → Update cache
3. **No Data Found** → Log and continue
4. **API/MCP Requests** → Check cache → Check database → Scrape if needed

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Authentication
AUTH_TOKEN=sabji_gpt_secret_2025

# Scraping
SCRAPE_HEADLESS=true
SCRAPE_TIMEOUT=30000

# Database
DATABASE_PATH=mandi_prices.db

# Cache
CACHE_TTL_MINUTES=5

# Servers
API_PORT=8000        # Original API
MCP_PORT=8087        # MCP Server for Puch AI

# Logging
LOG_LEVEL=INFO       # DEBUG, INFO, WARNING, ERROR
```

## 🔍 Troubleshooting

### Common Issues

1. **"No Data Found" for all cities**
   - Markets might be closed (try during business hours)
   - Website might be down (check https://agmarknet.gov.in)

2. **MCP Connection Failed**
   - Check if AUTH_TOKEN matches in .env and connection command
   - Verify ngrok is running and URL is correct
   - Check if port 8087 is accessible

3. **Scheduler Not Running**
   - Check timezone settings (scheduler uses local time)
   - Verify virtual environment is activated
   - Check log files for errors

### Health Checks
```bash
# Check MCP server
curl http://localhost:8087/health

# Check original API
curl http://localhost:8000/health

# Test database
python -c "from src.database.price_db import PriceDatabase; print(PriceDatabase().get_db_stats())"
```

## 📚 Next Steps

1. **Production Deployment**
   - Deploy to cloud service (Railway, Render, DigitalOcean)
   - Use process manager (PM2, systemd)
   - Set up monitoring and alerts

2. **Scale Up**
   - Add more cities and vegetables
   - Implement retry logic for failed scrapes
   - Add price change alerts

3. **Integration**
   - Connect with other AI assistants
   - Create web dashboard
   - Build mobile app

## 🎉 Success Indicators

✅ Scraper extracts live data from Agmarknet
✅ Scheduler runs twice daily automatically  
✅ MCP server responds to Puch AI requests
✅ Database stores and retrieves price data
✅ Cache improves response times
✅ All 4 MCP tools work correctly

**Your SabjiGPT system is now complete and ready for production! 🚀**
