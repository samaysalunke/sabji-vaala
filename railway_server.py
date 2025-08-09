#!/usr/bin/env python3
"""
Railway-optimized server for SabjiGPT MCP
Simpler startup process to avoid deployment issues
"""

import os
import logging
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'sabji_gpt_secret_2025')
PORT = int(os.getenv('PORT', 8087))

# Initialize FastAPI app
app = FastAPI(
    title="SabjiGPT MCP Server", 
    version="1.0.0",
    description="MCP server for Indian vegetable price data"
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

# Authentication middleware
async def verify_auth_token(authorization: str = Header(None)):
    """Verify Bearer token authentication"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    return token

# MCP Tools (simplified for deployment)
TOOLS = [
    {
        "name": "get_vegetable_price",
        "description": "Get vegetable prices from Indian markets",
        "inputSchema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "enum": ["mumbai", "delhi", "pune"]},
                "vegetable": {"type": "string", "enum": ["tomato", "onion", "potato"]}
            },
            "required": ["city", "vegetable"]
        }
    },
    {
        "name": "get_market_trends", 
        "description": "Get market trends and insights",
        "inputSchema": {"type": "object", "properties": {}}
    }
]

@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": "SabjiGPT MCP Server",
        "version": "1.0.0",
        "status": "healthy",
        "tools_available": len(TOOLS),
        "connect_command": f"/mcp connect https://your-domain/mcp {AUTH_TOKEN}",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "auth_configured": bool(AUTH_TOKEN),
        "tools_count": len(TOOLS),
        "message": "SabjiGPT MCP Server is running"
    }

@app.post("/mcp")
async def mcp_handler(request: MCPRequest, authorization: str = Header(None)):
    """Main MCP protocol handler"""
    
    # Verify authentication
    await verify_auth_token(authorization)
    
    logger.info(f"MCP request: {request.method}")
    
    try:
        if request.method == "tools/list":
            return MCPResponse(
                id=request.id,
                result={"tools": TOOLS}
            )
        
        elif request.method == "tools/call":
            tool_name = request.params.get("name") if request.params else None
            arguments = request.params.get("arguments", {}) if request.params else {}
            
            logger.info(f"Calling tool: {tool_name}")
            
            if tool_name == "get_vegetable_price":
                city = arguments.get("city", "mumbai")
                vegetable = arguments.get("vegetable", "onion")
                
                # Mock response for now (until scraper is working in Railway)
                result = f"""🥬 **{vegetable.title()} Prices in {city.title()}**

💰 **Price**: ₹2.5/kg (₹250/quintal)
🏪 **Market**: Local Market
📅 **Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
📊 **Source**: agmarknet.gov.in (cached)

⚠️ **Note**: Live scraping coming soon! This is demo data.
"""
                return MCPResponse(
                    id=request.id,
                    result={"content": [{"type": "text", "text": result}]}
                )
            
            elif tool_name == "get_market_trends":
                result = """📈 **Market Trends & Database Stats**

📊 **System Status**: 
- Server: ✅ Running on Railway
- MCP Protocol: ✅ Active
- Authentication: ✅ Secured

🌱 **Supported**: Tomato, Onion, Potato
🏙️ **Cities**: Mumbai, Delhi, Pune (more coming)

💡 **Note**: Full scraping system deploying soon!
"""
                return MCPResponse(
                    id=request.id,
                    result={"content": [{"type": "text", "text": result}]}
                )
            
            else:
                return MCPResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Unknown tool: {tool_name}"}
                )
        
        else:
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

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting SabjiGPT MCP Server on port {PORT}")
    print(f"🔑 Auth Token: {AUTH_TOKEN}")
    print(f"🌐 Health check: http://0.0.0.0:{PORT}/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
