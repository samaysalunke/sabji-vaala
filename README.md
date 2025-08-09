# 🥬 SabjiGPT - Indian Vegetable Price Intelligence

> Real-time vegetable price data from Indian agricultural markets through AI-powered scraping and MCP integration

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://puch.ai/mcp)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 **What is SabjiGPT?**

SabjiGPT is an intelligent system that scrapes live vegetable prices from [Agmarknet.gov.in](https://agmarknet.gov.in) and provides the data through:
- **🤖 AI Assistant Integration** via Model Context Protocol (MCP)
- **📅 Automated Data Collection** twice daily (9 AM & 6 PM IST)
- **🔍 Natural Language Queries** like "What's the price of onions in Mumbai?"

## ✨ **Features**

- 🥬 **Real-time Price Data** for tomatoes, onions, and potatoes
- 🏙️ **10+ Major Cities** across India (Mumbai, Delhi, Pune, Bengaluru, etc.)
- 🕒 **Automated Scraping** twice daily for fresh market data
- 🔌 **Puch AI Integration** through MCP protocol
- 💾 **SQLite Database** with price history and trends
- ⚡ **Smart Caching** for faster API responses
- 🛡️ **Production Ready** with Docker, Railway, Render support

## 🚀 **Quick Start**

### **1. Clone & Setup**
```bash
git clone https://github.com/samaysalunke/sabji-vaala.git
cd sabji-vaala
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

### **2. Test the Scraper**
```bash
python run_automated_system.py --test-scrape
```

Expected output:
```
✅ Test SUCCESSFUL!
   Price: ₹2.0/kg
   Market: Indapur
   Source: agmarknet.gov.in
```

### **3. Run Complete System**
```bash
# Runs both scheduler (9AM & 6PM) and MCP server (port 8087)
python run_automated_system.py
```

## 🔌 **Puch AI Integration**

### **Deploy to Production** (5 minutes)
1. **Railway** (Recommended): [railway.app](https://railway.app)
2. **Render**: [render.com](https://render.com)
3. **DigitalOcean**: [digitalocean.com](https://digitalocean.com)

### **Connect to Puch AI**
```
/mcp connect https://your-app.railway.app/mcp sabji_gpt_secret_2025
```

### **Try These Queries**
- "What's the current price of onions in Mumbai?"
- "Compare tomato prices across Indian cities" 
- "Show me all vegetable prices in Delhi"
- "What are the latest market trends?"

## 📊 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and system status |
| `/` | GET | API information and available tools |
| `/mcp` | POST | MCP protocol endpoint for AI integration |

## 🛠️ **MCP Tools**

1. **`get_vegetable_price`** - Get live prices for specific vegetable/city
2. **`get_city_prices`** - All vegetable prices for a city
3. **`compare_vegetable_prices`** - Price comparison across cities
4. **`get_market_trends`** - Market insights and database stats

## 🏗️ **Architecture**

```
┌─────────────────┐    MCP Protocol     ┌─────────────────┐
│   Puch AI       │ ───────────────────► │ MCP Server      │
│   Assistant     │                     │ Port 8087       │
└─────────────────┘                     └─────────┬───────┘
                                                  │
                  ┌─────────────────┐             │
                  │   Scheduler     │◄────────────┤
                  │   9AM & 6PM     │             │
                  └─────────┬───────┘             │
                            │                     │
                            ▼                     ▼
                  ┌─────────────────────────────────────────┐
                  │         Core Components                 │
                  │  ┌─────────┐ ┌──────────┐ ┌──────────┐ │
                  │  │Scraper  │ │Database  │ │  Cache   │ │
                  │  │(Live)   │ │(SQLite)  │ │(5 min)   │ │
                  │  └─────────┘ └──────────┘ └──────────┘ │
                  └─────────────────┬───────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │ Agmarknet.gov.in│
                          │ Live Data Source│
                          └─────────────────┘
```

## 🗂️ **Project Structure**

```
sabji-vaala/
├── src/
│   ├── scraper/          # Web scraping logic
│   ├── database/         # SQLite database operations
│   ├── api/             # FastAPI server
│   ├── cache/           # Response caching
│   ├── data/            # City/vegetable mappings
│   ├── scheduler/       # Automated scraping
│   └── mcp/             # MCP server for AI integration
├── deploy/              # Production deployment files
├── run_automated_system.py  # Main system runner
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🌐 **Supported Markets**

### **Cities**
Mumbai, Delhi, Pune, Bengaluru, Hyderabad, Chennai, Kolkata, Ahmedabad, Jaipur, Lucknow

### **Vegetables**
Tomato, Onion, Potato (more coming soon!)

## 📈 **Usage Modes**

```bash
# Complete system (scheduler + MCP server)
python run_automated_system.py

# MCP server only (for AI integration)
python run_automated_system.py --mcp-only

# Scheduler only (automated data collection)
python run_automated_system.py --scheduler-only

# One-time test scrape
python run_automated_system.py --test-scrape
```

## 🐳 **Docker Deployment**

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🔧 **Configuration**

Environment variables (`.env`):
```bash
AUTH_TOKEN=sabji_gpt_secret_2025
MCP_PORT=8087
SCRAPE_HEADLESS=true
LOG_LEVEL=INFO
DATABASE_PATH=mandi_prices.db
CACHE_TTL_MINUTES=5
```

## 📚 **Documentation**

- **[Setup Guide](SETUP.md)** - Detailed installation and usage
- **[Production Guide](PRODUCTION.md)** - Deploy to Railway, Render, VPS
- **[API Documentation](src/api/)** - FastAPI endpoints and schemas

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **[Agmarknet.gov.in](https://agmarknet.gov.in)** - Government of India's agricultural marketing platform
- **[Puch AI](https://puch.ai)** - AI assistant platform with MCP support
- **[TurboML MCP Starter](https://github.com/TurboML-Inc/mcp-starter)** - MCP implementation reference

## 🚨 **Disclaimer**

This project is for educational and research purposes. Always respect the terms of service of scraped websites and use responsibly.

---

**Made with ❤️ for Indian farmers and vegetable price transparency**

🌟 **Star this repo if you find it useful!** 🌟