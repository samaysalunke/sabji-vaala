#!/usr/bin/env python3
"""
SabjiGPT MCP Server for Puch AI
Based on TurboML-Inc/mcp-starter implementation
Provides vegetable price data through proper MCP protocol
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional
from pathlib import Path

# MCP imports (using same pattern as TurboML starter)
from mcp import McpError, types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.fastapi import FastAPIServer
from pydantic import Field
import uvicorn
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - Following TurboML pattern
AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'sabji_gpt_secret_2025')
MY_NUMBER = os.getenv('MY_NUMBER', '919998881729')  # Following TurboML pattern
PORT = int(os.getenv('PORT', 8086))  # Using same port as TurboML starter

# Initialize MCP server
app = FastAPI(
    title="SabjiGPT MCP Server",
    description="MCP server for Indian vegetable price data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MCP server instance
mcp_server = Server("SabjiGPT")

# Authentication middleware (following TurboML pattern)
async def verify_bearer_token(authorization: str = Header(None)):
    """Verify Bearer token following TurboML pattern"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    
    return token

# MCP Tools - Following TurboML @mcp.tool pattern
@mcp_server.call_tool()
async def get_vegetable_price(
    city: Annotated[str, Field(description="City name (mumbai, delhi, pune, bengaluru, hyderabad, chennai)")],
    vegetable: Annotated[str, Field(description="Vegetable name (tomato, onion, potato)")]
) -> str:
    """Get current vegetable prices from Indian agricultural markets"""
    
    logger.info(f"Getting {vegetable} price for {city}")
    
    # Mock data for now - following TurboML simple response pattern
    price_data = {
        "mumbai": {"tomato": 2.5, "onion": 2.0, "potato": 1.8},
        "delhi": {"tomato": 2.8, "onion": 2.2, "potato": 2.0},
        "pune": {"tomato": 2.2, "onion": 1.8, "potato": 1.5},
        "bengaluru": {"tomato": 2.6, "onion": 2.1, "potato": 1.9},
        "hyderabad": {"tomato": 2.4, "onion": 1.9, "potato": 1.7},
        "chennai": {"tomato": 2.7, "onion": 2.3, "potato": 2.1}
    }
    
    city_lower = city.lower()
    vegetable_lower = vegetable.lower()
    
    if city_lower not in price_data:
        return f"❌ Sorry, price data not available for {city}. Supported cities: Mumbai, Delhi, Pune, Bengaluru, Hyderabad, Chennai"
    
    if vegetable_lower not in price_data[city_lower]:
        return f"❌ Sorry, {vegetable} prices not available for {city}. Supported vegetables: Tomato, Onion, Potato"
    
    price = price_data[city_lower][vegetable_lower]
    
    result = f"""🥬 **{vegetable.title()} Prices in {city.title()}**

💰 **Price**: ₹{price}/kg
🏪 **Market**: Local Agricultural Market
📅 **Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')} IST
📊 **Source**: agmarknet.gov.in (demo data)

💡 **Note**: This is demonstration data. Live scraping system coming soon!
"""
    return result

@mcp_server.call_tool()
async def get_market_trends() -> str:
    """Get market trends and agricultural insights for Indian vegetables"""
    
    logger.info("Getting market trends")
    
    result = f"""📈 **Indian Vegetable Market Trends**

📊 **System Status**:
- MCP Server: ✅ Active on Puch AI
- Data Source: agmarknet.gov.in
- Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} IST
- Phone: {MY_NUMBER}

🥬 **Supported Vegetables**:
• Tomato - Average ₹2.5/kg across major cities
• Onion - Average ₹2.0/kg across major cities  
• Potato - Average ₹1.8/kg across major cities

🏙️ **Covered Cities**:
Mumbai, Delhi, Pune, Bengaluru, Hyderabad, Chennai

💡 **Market Insights**:
- Seasonal price variations typical
- Mumbai generally has higher prices
- Pune often offers competitive rates
- Live data collection system in development

📞 **Support**: Contact {MY_NUMBER} for assistance
"""
    return result

@mcp_server.call_tool() 
async def compare_vegetable_prices(
    vegetable: Annotated[str, Field(description="Vegetable to compare (tomato, onion, potato)")]
) -> str:
    """Compare vegetable prices across major Indian cities"""
    
    logger.info(f"Comparing {vegetable} prices across cities")
    
    # Mock comparison data
    comparison_data = {
        "tomato": [
            ("Pune", 2.2), ("Hyderabad", 2.4), ("Mumbai", 2.5), 
            ("Bengaluru", 2.6), ("Chennai", 2.7), ("Delhi", 2.8)
        ],
        "onion": [
            ("Pune", 1.8), ("Hyderabad", 1.9), ("Mumbai", 2.0),
            ("Bengaluru", 2.1), ("Delhi", 2.2), ("Chennai", 2.3)
        ],
        "potato": [
            ("Pune", 1.5), ("Hyderabad", 1.7), ("Mumbai", 1.8),
            ("Bengaluru", 1.9), ("Delhi", 2.0), ("Chennai", 2.1)
        ]
    }
    
    vegetable_lower = vegetable.lower()
    
    if vegetable_lower not in comparison_data:
        return f"❌ Sorry, comparison not available for {vegetable}. Supported: Tomato, Onion, Potato"
    
    prices = comparison_data[vegetable_lower]
    
    result = f"""📊 **{vegetable.title()} Price Comparison Across Indian Cities**

"""
    
    for i, (city, price) in enumerate(prices, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📍"
        result += f"{emoji} **{city}**: ₹{price}/kg\n"
    
    best_city, best_price = prices[0]
    worst_city, worst_price = prices[-1]
    
    result += f"""
💡 **Best Deal**: {best_city} at ₹{best_price}/kg
💸 **Highest**: {worst_city} at ₹{worst_price}/kg
📈 **Price Range**: ₹{best_price} - ₹{worst_price}/kg

📅 **Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')} IST
"""
    return result

# FastAPI endpoints (following TurboML pattern)
@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "name": "SabjiGPT MCP Server",
        "version": "1.0.0",
        "description": "Indian vegetable price data via MCP protocol",
        "status": "active",
        "tools": 3,
        "auth_method": "bearer_token",
        "contact": MY_NUMBER,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "server": "SabjiGPT MCP",
        "timestamp": datetime.now().isoformat(),
        "auth_configured": bool(AUTH_TOKEN),
        "contact": MY_NUMBER
    }

# MCP endpoint (following TurboML pattern)
@app.post("/mcp")
async def mcp_endpoint(request: Request, authorization: str = Header(None)):
    """MCP protocol endpoint following TurboML implementation pattern"""
    
    # Verify authentication
    await verify_bearer_token(authorization)
    
    # Get request body
    body = await request.body()
    
    # Handle MCP protocol via the server instance
    try:
        # Use the MCP server to handle the request
        response = await mcp_server.handle_request(body)
        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"MCP request error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    print("🌟 SabjiGPT MCP Server for Puch AI")
    print("=" * 50)
    print(f"🚀 Starting server on port {PORT}")
    print(f"🔑 Auth Token: {AUTH_TOKEN}")
    print(f"📞 Contact: {MY_NUMBER}")
    print(f"🌐 Server will be available at: http://0.0.0.0:{PORT}")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
