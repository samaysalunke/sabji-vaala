# SabjiGPT Project Structure

## 🏗️ **Clean Architecture Overview**

```
sabjiGPT/
├── 🚀 PRODUCTION FILES
│   ├── final_mcp_server.py          # ✅ Main MCP server for Puch AI
│   ├── Procfile                     # ✅ Railway deployment config  
│   ├── railway.toml                 # ✅ Railway settings
│   ├── requirements-railway.txt     # ✅ Minimal prod dependencies
│   └── requirements.txt             # ✅ Full dev dependencies
│
├── 📦 CORE MODULES  
│   └── src/
│       ├── scraper/                 # Web scraping logic
│       │   └── improved_scraper.py  # ✅ Working Agmarknet scraper
│       ├── database/                # Data persistence
│       │   └── price_db.py          # ✅ SQLite operations
│       ├── data/                    # Static data
│       │   └── vegetables.py        # ✅ Mappings & constants
│       ├── cache/                   # Caching layer
│       │   └── simple_cache.py      # ✅ TTL cache
│       ├── scheduler/               # Automation
│       │   └── automated_scraper.py # ✅ Daily scraping (9am/6pm)
│       └── api/                     # REST API
│           └── main.py              # ✅ FastAPI endpoints
│
├── 🚀 DEPLOYMENT
│   ├── deploy/                      # VPS deployment
│   ├── docker-compose.yml           # Docker setup
│   ├── Dockerfile                   # Container config
│   └── render.yaml                  # Render deployment
│
├── 📚 DOCUMENTATION
│   ├── README.md                    # ✅ Project overview
│   ├── SETUP.md                     # ✅ Setup instructions  
│   ├── PRODUCTION.md                # ✅ Deployment guide
│   └── PROJECT_STRUCTURE.md         # ✅ This file
│
└── 🗃️ ARCHIVE
    └── archive/                     # Debug files & samples
```

## 🎯 **Key Components**

### **Production Server**
- **`final_mcp_server.py`**: Main MCP server with 4 tools:
  - `validate()` - Returns phone number (required by Puch AI)
  - `get_vegetable_price()` - Price data for city/vegetable
  - `get_market_trends()` - Market insights
  - `compare_vegetable_prices()` - Cross-city comparison

### **MCP Protocol Compliance**
- ✅ JSON-RPC 2.0 protocol
- ✅ Bearer token authentication  
- ✅ Protocol version: `2025-06-18`
- ✅ Required methods: `initialize`, `ping`, `tools/list`, `tools/call`

### **Deployment Status**
- ✅ **Railway**: https://sabji-vaala-production.up.railway.app
- ✅ **GitHub**: https://github.com/samaysalunke/sabji-vaala.git
- ✅ **Dependencies**: Only FastAPI + minimal deps (no external MCP libs)

## 🔧 **Development vs Production**

| Environment | Server File | Requirements | Purpose |
|-------------|-------------|--------------|---------|
| **Production** | `final_mcp_server.py` | `requirements-railway.txt` | Puch AI MCP |
| **Development** | `run_automated_system.py` | `requirements.txt` | Full system |

## 🎯 **Next Steps**

1. ✅ **Codebase Cleaned** - Removed all duplicate/broken servers
2. ✅ **Single Source of Truth** - `final_mcp_server.py` is the only server
3. 🎯 **Ready for Puch AI** - Test connection with clean setup
