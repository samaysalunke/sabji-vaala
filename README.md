# 🥬 SabjiGPT - Mandi Price API

Real-time vegetable price data from Indian mandi markets, scraped from Agmarknet.

## ✨ Features

- **Real-time Prices**: Live vegetable prices from 10+ major Indian cities
- **Smart Caching**: Multi-tier caching (memory → database → fresh scrape)
- **RESTful API**: Clean JSON API with comprehensive documentation
- **20 Vegetables**: Support for commonly used vegetables with Hindi name recognition
- **Rate Limited**: Respectful scraping with exponential backoff
- **MCP Ready**: Built with MCP (Model Context Protocol) integration in mind

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repo-url>
cd sabjiGPT

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Start the API Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
python -m uvicorn src.api.main:app --reload

# Server will be available at http://localhost:8000
```

### Test with Sample Data

```bash
# Add test data (for demo purposes)
python -c "from test_api import populate_test_data; populate_test_data()"

# Test API
curl -X POST "http://localhost:8000/price" \
     -H "Content-Type: application/json" \
     -d '{"city": "Mumbai", "vegetable": "tomato"}'
```

## 📖 API Documentation

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Get Vegetable Price
```bash
POST /price
Content-Type: application/json

{
  "city": "Mumbai",
  "vegetable": "tomato",
  "language": "en"
}
```

**Response:**
```json
{
  "city": "mumbai",
  "vegetable": "tomato", 
  "price": 25.50,
  "price_per": "kg",
  "currency": "INR",
  "market": "Mumbai Central Market",
  "updated_at": "2025-08-09T17:18:41",
  "source": "agmarknet.gov.in",
  "cache_status": "database"
}
```

#### Health Check
```bash
GET /health
```

#### List Supported Vegetables
```bash
GET /vegetables
```

#### List Supported Cities  
```bash
GET /cities
```

#### Get All Prices for a City
```bash
GET /city/{city}/prices
```

#### Get Prices Across Cities for a Vegetable
```bash
GET /vegetable/{vegetable}/prices
```

## 🏙️ Supported Cities

- Mumbai
- Delhi
- Bengaluru/Bangalore
- Hyderabad
- Chennai
- Kolkata
- Pune
- Ahmedabad
- Jaipur
- Lucknow

## 🥕 Supported Vegetables

- Tomato (टमाटर)
- Potato (आलू)
- Onion (प्याज)
- Cauliflower (फूलगोभी)
- Cabbage (पत्तागोभी)
- Carrot (गाजर)
- Green Peas (हरी मटर)
- Spinach (पालक)
- Okra/Bhindi (भिंडी)
- Brinjal/Eggplant (बैंगन)

*Note: Vegetable names are normalized - you can use Hindi names, common variants, etc.*

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Cache Layer   │    │   Database      │
│   Server        │◄──►│   (Memory)      │◄──►│   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   Scraper       │◄──►│   Agmarknet     │
│   (Playwright)  │    │   Website       │
└─────────────────┘    └─────────────────┘
```

### Data Flow
1. **API Request** → Check cache (5min TTL)
2. **Cache Miss** → Check database (6hr freshness)
3. **Stale Data** → Scrape fresh data from Agmarknet
4. **Fresh Data** → Save to database → Cache response

## 🔧 Development

### Project Structure
```
sabjiGPT/
├── src/
│   ├── api/           # FastAPI server
│   ├── scraper/       # Agmarknet scraper
│   ├── database/      # SQLite database layer
│   ├── cache/         # In-memory cache
│   ├── data/          # Vegetable/city mappings
│   └── mcp/           # MCP server (coming soon)
├── tests/             # Test files
├── requirements.txt   # Dependencies
└── README.md         # This file
```

### Run Tests
```bash
# Test database
python src/database/price_db.py

# Test cache
python src/cache/simple_cache.py

# Test scraper (when Agmarknet is available)
python src/scraper/agmarknet_scraper.py

# Test API with sample data
python test_api.py
```

### Debug Scraper
```bash
# Explore Agmarknet structure
python src/scraper/explore_agmarknet.py

# Debug form interactions
python src/scraper/debug_scraper.py
```

## 🚨 Important Notes

### Rate Limiting
- Scraper includes delays and exponential backoff
- Respects Agmarknet's servers
- Uses caching to minimize requests

### Data Availability
- Vegetable prices aren't always available for all cities
- Data depends on market reporting to Agmarknet
- API returns 404 when no data is available

### Production Considerations
- Use PostgreSQL for production database
- Add Redis for distributed caching
- Implement proper monitoring and logging
- Use background job queues for scraping
- Add authentication for admin endpoints

## 🔮 Coming Soon

- **MCP Server**: Model Context Protocol integration for AI assistants
- **Webhook Support**: Real-time price alerts
- **Historical Data**: Price trends and analytics
- **More Markets**: Additional wholesale markets beyond Agmarknet
- **Mobile API**: Optimized endpoints for mobile apps

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Agmarknet.gov.in**: Source of vegetable price data
- **FastAPI**: For the excellent web framework
- **Playwright**: For reliable web scraping

---

**Made with ❤️ for Indian farmers, consumers, and developers**
