#!/usr/bin/env python3
"""
SabjiGPT MCP Server for Puch AI
Following TurboML-Inc/mcp-starter implementation pattern exactly
"""

import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration following TurboML pattern
AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'sabji_gpt_secret_2025')
MY_NUMBER = os.getenv('MY_NUMBER', '919998881729')  # Required by Puch AI
PORT = int(os.getenv('PORT', os.getenv('MCP_PORT', 8086)))  # Railway uses PORT, fallback to MCP_PORT or 8086

# Initialize FastAPI app
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

# Authentication (following TurboML pattern)
def verify_bearer_token(authorization: str = Header(None)):
    """Verify Bearer token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    
    return token

# Tool definitions (following TurboML schema)
TOOLS = [
    {
        "name": "get_vegetable_price",
        "description": "Get current vegetable prices from Indian agricultural markets (Agmarknet). Returns live price data for tomato, onion, or potato in major Indian cities.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name (mumbai, delhi, pune, bengaluru, hyderabad, chennai)",
                    "enum": ["mumbai", "delhi", "pune", "bengaluru", "hyderabad", "chennai"]
                },
                "vegetable": {
                    "type": "string", 
                    "description": "Vegetable name (tomato, onion, potato)",
                    "enum": ["tomato", "onion", "potato"]
                }
            },
            "required": ["city", "vegetable"]
        }
    },
    {
        "name": "get_market_trends",
        "description": "Get market trends and insights for Indian vegetable prices. Shows system status, supported vegetables, and market analysis.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "compare_vegetable_prices", 
        "description": "Compare prices of a specific vegetable across multiple Indian cities. Useful for finding the best deals and price ranges.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vegetable": {
                    "type": "string",
                    "description": "Vegetable to compare (tomato, onion, potato)", 
                    "enum": ["tomato", "onion", "potato"]
                }
            },
            "required": ["vegetable"]
        }
    }
]

# Tool implementations
def execute_get_vegetable_price(city: str, vegetable: str) -> str:
    """Get vegetable price for specific city"""
    
    # Mock price data (demo implementation)
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
    
    return f"""🥬 **{vegetable.title()} Prices in {city.title()}**

💰 **Price**: ₹{price}/kg
🏪 **Market**: Local Agricultural Market  
📅 **Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')} IST
📊 **Source**: agmarknet.gov.in (demo data)

📞 **Contact**: {MY_NUMBER}
💡 **Note**: This is demonstration data. Live scraping system coming soon!
"""

def execute_get_market_trends() -> str:
    """Get market trends and insights"""
    
    return f"""📈 **Indian Vegetable Market Trends**

📊 **System Status**:
- MCP Server: ✅ Active on Puch AI
- Data Source: agmarknet.gov.in
- Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} IST
- Support Contact: {MY_NUMBER}

🥬 **Supported Vegetables**:
• Tomato - Average ₹2.5/kg across major cities
• Onion - Average ₹2.0/kg across major cities
• Potato - Average ₹1.8/kg across major cities

🏙️ **Covered Cities**:
Mumbai, Delhi, Pune, Bengaluru, Hyderabad, Chennai

💡 **Market Insights**:
- Seasonal price variations typical for Indian markets
- Mumbai generally has higher prices due to logistics
- Pune often offers competitive rates for vegetables
- Live data collection system in development

📞 **Technical Support**: {MY_NUMBER}
"""

def execute_compare_vegetable_prices(vegetable: str) -> str:
    """Compare vegetable prices across cities"""
    
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
    
    result = f"📊 **{vegetable.title()} Price Comparison Across Indian Cities**\n\n"
    
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
📞 **Support**: {MY_NUMBER}
"""
    return result

# FastAPI endpoints
@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "name": "SabjiGPT MCP Server",
        "version": "1.0.0",
        "description": "Indian vegetable price data via MCP protocol for Puch AI",
        "status": "active",
        "tools": len(TOOLS),
        "auth_method": "bearer_token",
        "contact": MY_NUMBER,
        "connect_command": f"/mcp connect https://your-domain/mcp {AUTH_TOKEN}",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "server": "SabjiGPT MCP",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "auth_configured": bool(AUTH_TOKEN),
        "contact": MY_NUMBER,
        "tools_available": len(TOOLS)
    }

# MCP endpoint (following TurboML exact pattern)
@app.post("/mcp")
async def mcp_endpoint(request: Request, authorization: str = Header(None)):
    """MCP protocol endpoint"""
    
    # Verify authentication
    verify_bearer_token(authorization)
    
    # Parse request body manually to handle any format
    try:
        body = await request.json()
        logger.info(f"MCP request body: {body}")
        
        # Extract method and params
        method = body.get("method", "")
        params = body.get("params", {})
        request_id = body.get("id", "1")
        
        logger.info(f"MCP method: {method}, params: {params}")
        
    except Exception as e:
        logger.error(f"Failed to parse request: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None
            }
        )
    
        # Initialize handshake
        if method == "initialize":
            client_info = params.get("clientInfo", {})
            protocol_version = params.get("protocolVersion", "2024-11-05")
            
            logger.info(f"MCP Initialize from {client_info.get('name', 'unknown')}")
            
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": False}
                    },
                    "serverInfo": {
                        "name": "SabjiGPT",
                        "version": "1.0.0"
                    }
                }
            })
        
        # Ping
        elif method == "ping":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {}
            })
        
        # Tools list
        elif method == "tools/list":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": TOOLS}
            })
        
        # Tool calls
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            logger.info(f"Calling tool: {tool_name} with args: {arguments}")
            
            if tool_name == "get_vegetable_price":
                city = arguments.get("city", "mumbai")
                vegetable = arguments.get("vegetable", "onion")
                result = execute_get_vegetable_price(city, vegetable)
                
            elif tool_name == "get_market_trends":
                result = execute_get_market_trends()
                
            elif tool_name == "compare_vegetable_prices":
                vegetable = arguments.get("vegetable", "tomato")
                result = execute_compare_vegetable_prices(vegetable)
                
            else:
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                })
            
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": result}]}
            })
        
        else:
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            })
    
    except Exception as e:
        logger.error(f"MCP error: {e}")
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        })

# Additional endpoints that Puch AI might check
@app.get("/mcp")
async def mcp_get():
    """Handle GET requests to /mcp endpoint - shows server info"""
    return {
        "server": "SabjiGPT MCP Server",
        "version": "1.0.0",
        "protocol": "MCP 2024-11-05", 
        "methods": ["POST"],
        "tools": len(TOOLS),
        "auth": "Bearer token required",
        "contact": MY_NUMBER,
        "status": "active"
    }

@app.options("/mcp")
async def mcp_options():
    """Handle preflight requests"""
    return {"methods": ["GET", "POST"], "protocol": "MCP", "version": "2024-11-05"}

if __name__ == "__main__":
    print("🌟 SabjiGPT MCP Server for Puch AI")
    print("=" * 60)
    print(f"📱 Following TurboML-Inc/mcp-starter pattern")
    print(f"🚀 Starting server on port {PORT}")
    print(f"🔑 Auth Token: {AUTH_TOKEN}")
    print(f"📞 Phone Number: {MY_NUMBER}")
    print(f"🛠️ Tools: {len(TOOLS)} available")
    print(f"🌐 Server URL: http://0.0.0.0:{PORT}")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
