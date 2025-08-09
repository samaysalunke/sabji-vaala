"""
SabjiGPT MCP Server for Puch AI Integration
Based on: https://github.com/TurboML-Inc/mcp-starter

Provides vegetable price data through MCP protocol with Bearer token authentication
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import our existing components
from src.scraper.improved_scraper import ImprovedAgmarknetScraper
from src.database.price_db import PriceDatabase
from src.cache.simple_cache import price_cache
from src.data.vegetables import list_supported_vegetables, list_supported_cities

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'sabji_gpt_secret_2025')
MCP_PORT = int(os.getenv('PORT', os.getenv('MCP_PORT', 8087)))

# Initialize FastAPI app
app = FastAPI(
    title="SabjiGPT MCP Server",
    version="1.0.0",
    description="MCP server providing Indian vegetable price data for Puch AI"
)

# Add CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = PriceDatabase()
scraper = ImprovedAgmarknetScraper()

# MCP Protocol Models
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

# Authentication middleware
async def verify_auth_token(authorization: str = Header(None)):
    """Verify Bearer token authentication"""
    if not authorization:
        logger.warning("Missing authorization header")
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        logger.warning(f"Invalid authorization format: {authorization[:20]}...")
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>'")
    
    token = authorization.replace("Bearer ", "")
    if token != AUTH_TOKEN:
        logger.warning(f"Invalid token received: {token[:10]}...")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    logger.debug("Authentication successful")
    return token

# MCP Tools Configuration
TOOLS = [
    Tool(
        name="get_vegetable_price",
        description="Get current vegetable prices from Indian agricultural markets (Agmarknet). Returns live price data for tomato, onion, or potato in major Indian cities.",
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string", 
                    "description": "City name (e.g., mumbai, delhi, pune, bengaluru, hyderabad, chennai)",
                    "enum": ["mumbai", "delhi", "pune", "bengaluru", "hyderabad", "chennai", "kolkata", "ahmedabad", "jaipur", "lucknow"]
                },
                "vegetable": {
                    "type": "string",
                    "description": "Vegetable name (tomato, onion, or potato)",
                    "enum": ["tomato", "onion", "potato"]
                }
            },
            "required": ["city", "vegetable"]
        }
    ),
    Tool(
        name="get_city_prices",
        description="Get prices for all available vegetables in a specific city. Shows market overview for the city.",
        inputSchema={
            "type": "object", 
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name (e.g., mumbai, delhi, pune)",
                    "enum": ["mumbai", "delhi", "pune", "bengaluru", "hyderabad", "chennai", "kolkata", "ahmedabad", "jaipur", "lucknow"]
                }
            },
            "required": ["city"]
        }
    ),
    Tool(
        name="compare_vegetable_prices",
        description="Compare prices of a specific vegetable across multiple cities. Useful for finding the cheapest markets.",
        inputSchema={
            "type": "object",
            "properties": {
                "vegetable": {
                    "type": "string", 
                    "description": "Vegetable to compare (tomato, onion, or potato)",
                    "enum": ["tomato", "onion", "potato"]
                },
                "cities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of cities to compare (optional, defaults to major cities)",
                    "default": ["mumbai", "delhi", "pune", "bengaluru", "hyderabad", "chennai"]
                }
            },
            "required": ["vegetable"]
        }
    ),
    Tool(
        name="get_market_trends",
        description="Get price trends and market insights for vegetables. Shows latest prices and market activity.",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back for trends (default: 7)",
                    "default": 7,
                    "minimum": 1,
                    "maximum": 30
                }
            }
        }
    )
]

# MCP Protocol Handlers
@app.post("/mcp")
async def mcp_handler(request: MCPRequest, authorization: str = Header(None)):
    """Main MCP protocol handler"""
    
    # Verify authentication
    await verify_auth_token(authorization)
    
    logger.info(f"MCP request: {request.method}")
    
    try:
        if request.method == "tools/list":
            logger.debug("Handling tools/list request")
            return MCPResponse(
                id=request.id,
                result={"tools": [tool.dict() for tool in TOOLS]}
            )
        
        elif request.method == "tools/call":
            tool_name = request.params.get("name") if request.params else None
            arguments = request.params.get("arguments", {}) if request.params else {}
            
            logger.info(f"Calling tool: {tool_name} with args: {arguments}")
            
            result = await handle_tool_call(tool_name, arguments)
            
            return MCPResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": result}]}
            )
        
        else:
            logger.warning(f"Unknown method: {request.method}")
            return MCPResponse(
                id=request.id,
                error={"code": -32601, "message": f"Method not found: {request.method}"}
            )
    
    except Exception as e:
        logger.error(f"MCP handler error: {e}")
        return MCPResponse(
            id=request.id,
            error={"code": -32603, "message": f"Internal error: {str(e)}"}
        )

async def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Handle individual tool calls"""
    
    if tool_name == "get_vegetable_price":
        city = arguments.get("city")
        vegetable = arguments.get("vegetable")
        
        logger.info(f"Getting {vegetable} price in {city}")
        
        # Check cache first
        cached_data = price_cache.get(city, vegetable)
        if cached_data:
            logger.debug("Returning cached data")
            return format_price_response(cached_data, source="cache")
        
        # Check database
        db_data = db.get_latest_price(city, vegetable)
        if db_data:
            logger.debug("Returning database data")
            price_cache.set(city, vegetable, db_data)
            return format_price_response(db_data, source="database")
        
        # Scrape live data as fallback
        logger.info("No cached/DB data found, scraping live data")
        live_data = scraper.get_vegetable_price(city, vegetable, headless=True)
        if live_data:
            db.insert_price(live_data)
            price_cache.set(city, vegetable, live_data)
            return format_price_response(live_data, source="live_scraping")
        
        return f"❌ No price data available for {vegetable} in {city}. The market might be closed or data unavailable."
    
    elif tool_name == "get_city_prices":
        city = arguments.get("city")
        logger.info(f"Getting all prices for {city}")
        
        city_prices = db.get_city_prices(city)
        
        if not city_prices:
            return f"❌ No price data available for {city}. Try using get_vegetable_price to collect fresh data first."
        
        return format_city_prices_response(city, city_prices)
    
    elif tool_name == "compare_vegetable_prices":
        vegetable = arguments.get("vegetable")
        cities = arguments.get("cities", ["mumbai", "delhi", "pune", "bengaluru", "hyderabad", "chennai"])
        
        logger.info(f"Comparing {vegetable} prices across {len(cities)} cities")
        
        # Get data across cities for the vegetable
        comparison_data = db.get_vegetable_prices_across_cities(vegetable)
        
        if not comparison_data:
            return f"❌ No price data available for {vegetable} across the specified cities. Try collecting some data first using get_vegetable_price."
        
        return format_comparison_response(vegetable, comparison_data)
    
    elif tool_name == "get_market_trends":
        days = arguments.get("days", 7)
        logger.info(f"Getting market trends for last {days} days")
        
        stats = db.get_db_stats()
        return format_trends_response(stats, days)
    
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def format_price_response(data: Dict[str, Any], source: str) -> str:
    """Format price data response"""
    return f"""🥬 **{data['vegetable'].title()} Prices in {data['city'].title()}**

💰 **Price**: ₹{data['price_per_kg']}/kg (₹{data['price']}/{data['price_per']})
🏪 **Market**: {data.get('market', 'N/A')}
🌱 **Variety**: {data.get('variety', 'N/A')}
📅 **Updated**: {data.get('timestamp', 'N/A')}
📊 **Source**: {source}

🔍 **Raw Data**: Min: ₹{data.get('min_price', 'N/A')}, Max: ₹{data.get('max_price', 'N/A')}, Modal: ₹{data['price']}
"""

def format_city_prices_response(city: str, prices: List[Dict[str, Any]]) -> str:
    """Format city prices overview"""
    response = f"🏙️ **Vegetable Prices in {city.title()}**\n\n"
    
    for price in prices:
        response += f"🥬 **{price['vegetable'].title()}**: ₹{price['price']}/{price.get('price_per', 'kg')}\n"
        response += f"   Market: {price.get('market', 'N/A')} | Updated: {price.get('scraped_at', 'N/A')}\n\n"
    
    return response

def format_comparison_response(vegetable: str, comparison_data: List[Dict[str, Any]]) -> str:
    """Format price comparison response"""
    response = f"📊 **{vegetable.title()} Price Comparison Across Cities**\n\n"
    
    # Sort by price (database stores price per kg)
    sorted_data = sorted(comparison_data, key=lambda x: x['price'])
    
    for i, data in enumerate(sorted_data, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📍"
        response += f"{emoji} **{data['city'].title()}**: ₹{data['price']}/{data.get('price_per', 'kg')}\n"
        response += f"   Market: {data.get('market', 'N/A')} | Updated: {data.get('scraped_at', 'N/A')}\n\n"
    
    if sorted_data:
        cheapest = sorted_data[0]
        response += f"💡 **Best Deal**: {cheapest['city'].title()} at ₹{cheapest['price']}/{cheapest.get('price_per', 'kg')}"
    
    return response

def format_trends_response(stats: Dict[str, Any], days: int) -> str:
    """Format market trends response"""
    return f"""📈 **Market Trends & Database Stats**

📊 **Database Overview**:
- Total Records: {stats.get('total_records', 0)}
- Cities Covered: {stats.get('cities_count', 0)}
- Vegetables Tracked: {stats.get('vegetables_count', 0)}
- Last Updated: {stats.get('latest_update', 'N/A')}

🔍 **Data Period**: Last {days} days
🌱 **Supported Vegetables**: {', '.join(list_supported_vegetables())}
🏙️ **Supported Cities**: {', '.join(list_supported_cities())}

💡 **Tip**: Use get_vegetable_price to fetch fresh data or compare_vegetable_prices to find the best deals!
"""

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "auth_configured": bool(AUTH_TOKEN),
        "database_connected": True,  # Simple check
        "tools_available": len(TOOLS)
    }

# Root endpoint with MCP info
@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": "SabjiGPT MCP Server",
        "version": "1.0.0", 
        "description": "MCP server for Indian vegetable price data from agricultural markets",
        "protocol": "mcp",
        "authentication": "bearer_token",
        "tools_count": len(TOOLS),
        "supported_vegetables": list_supported_vegetables(),
        "supported_cities": list_supported_cities(),
        "connect_command": f"/mcp connect https://your-domain.ngrok.app/mcp {AUTH_TOKEN}",
        "documentation": "https://puch.ai/mcp",
        "github": "https://github.com/TurboML-Inc/mcp-starter"
    }

# Start server
if __name__ == "__main__":
    print("🚀 Starting SabjiGPT MCP Server...")
    print(f"🔑 Auth Token: {AUTH_TOKEN}")
    print(f"🌐 Available at: http://0.0.0.0:{MCP_PORT}")
    print(f"📚 Connect with Puch: /mcp connect https://your-domain.ngrok.app/mcp {AUTH_TOKEN}")
    print(f"🛠️ Available tools: {len(TOOLS)}")
    
    uvicorn.run(
        "src.mcp.sabji_mcp_server:app",
        host="0.0.0.0", 
        port=MCP_PORT,
        reload=False,  # Disable reload for production use
        log_level=log_level.lower()
    )
