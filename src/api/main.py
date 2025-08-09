"""
FastAPI server for SabjiGPT - Mandi Price API
Developer approach: Start simple, add complexity as needed
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import logging

# Import our modules
from src.database.price_db import PriceDatabase
from src.cache.simple_cache import price_cache, market_cache
from src.scraper.improved_scraper import ImprovedAgmarknetScraper
from src.data.vegetables import (
    normalize_vegetable_name, 
    normalize_city_name,
    get_agmarknet_vegetable_name,
    list_supported_vegetables,
    list_supported_cities
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SabjiGPT API",
    description="Real-time vegetable price data from Indian mandi markets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and scraper
db = PriceDatabase()
scraper = ImprovedAgmarknetScraper()

# Pydantic models
class PriceRequest(BaseModel):
    city: str = Field(..., description="City name (e.g., Mumbai, Delhi)")
    vegetable: str = Field(..., description="Vegetable name (e.g., tomato, potato, onion)")
    language: Optional[str] = Field("en", description="Response language (en/hi)")

class PriceResponse(BaseModel):
    city: str
    vegetable: str
    price: float
    price_per: str = "kg"
    currency: str = "INR"
    market: Optional[str] = None
    updated_at: datetime
    source: str
    cache_status: str  # "hit", "database", "fresh_scrape"

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database_stats: Dict[str, Any]
    cache_stats: Dict[str, Any]
    uptime_seconds: float

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime

# Global state
app_start_time = datetime.now()

@app.get("/", response_model=Dict[str, str])
async def root():
    """
    Root endpoint with basic info
    """
    return {
        "service": "SabjiGPT API", 
        "version": "1.0.0",
        "description": "Real-time vegetable prices from Indian mandi markets",
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/price", response_model=PriceResponse)
async def get_price(request: PriceRequest, background_tasks: BackgroundTasks):
    """
    Get vegetable price for a specific city
    
    This endpoint implements a multi-tier strategy:
    1. Check cache (fastest)
    2. Check database (recent data)
    3. Scrape fresh data (last resort)
    """
    logger.info(f"📞 Price request: {request.city} {request.vegetable}")
    
    # Normalize inputs
    normalized_veg = normalize_vegetable_name(request.vegetable)
    if not normalized_veg:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown vegetable: {request.vegetable}. Supported: {list_supported_vegetables()}"
        )
    
    city_mapping = normalize_city_name(request.city)
    if not city_mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported city: {request.city}. Supported: {list_supported_cities()}"
        )
    
    city_normalized = request.city.lower()
    
    try:
        # Step 1: Check cache
        cached_data = price_cache.get(city_normalized, normalized_veg)
        if cached_data:
            logger.info(f"✅ Cache hit for {city_normalized} {normalized_veg}")
            return PriceResponse(
                **cached_data,
                cache_status="hit"
            )
        
        # Step 2: Check database for recent data
        db_result = db.get_latest_price(city_normalized, normalized_veg)
        if db_result and is_recent_enough(db_result['scraped_at']):
            logger.info(f"✅ Database hit for {city_normalized} {normalized_veg}")
            
            response_data = {
                "city": db_result['city'],
                "vegetable": db_result['vegetable'],
                "price": db_result['price'],
                "price_per": db_result['price_per'],
                "currency": db_result['currency'],
                "market": db_result['market'],
                "updated_at": datetime.fromisoformat(db_result['scraped_at']),
                "source": db_result['source'],
                "cache_status": "database"
            }
            
            # Cache the database result
            price_cache.set(city_normalized, normalized_veg, response_data, ttl_minutes=5)
            
            return PriceResponse(**response_data)
        
        # Step 3: Fresh scrape (background task for faster response)
        logger.info(f"🔄 Fresh scrape needed for {city_normalized} {normalized_veg}")
        
        # For MVP, we'll do a quick scrape attempt
        # In production, this would be a background job
        fresh_data = await scrape_with_timeout(city_normalized, normalized_veg)
        
        if fresh_data:
            # Save to database
            db.insert_price(fresh_data)
            
            response_data = {
                "city": fresh_data['city'],
                "vegetable": fresh_data['vegetable'],
                "price": fresh_data.get('price_per_kg', fresh_data['price']),
                "price_per": "kg",
                "currency": fresh_data['currency'],
                "market": fresh_data.get('market'),
                "updated_at": datetime.fromisoformat(fresh_data['timestamp']),
                "source": fresh_data['source'],
                "cache_status": "fresh_scrape"
            }
            
            # Cache the fresh data
            price_cache.set(city_normalized, normalized_veg, response_data, ttl_minutes=5)
            
            logger.info(f"✅ Fresh data scraped: ₹{response_data['price']}")
            return PriceResponse(**response_data)
        
        # No data available
        raise HTTPException(
            status_code=404,
            detail=f"Price data not available for {request.vegetable} in {request.city}. This may be temporary."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint with system statistics
    """
    uptime = (datetime.now() - app_start_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        database_stats=db.get_stats(),
        cache_stats=price_cache.get_stats(),
        uptime_seconds=uptime
    )

@app.get("/vegetables", response_model=List[str])
async def list_vegetables():
    """
    List all supported vegetables
    """
    return list_supported_vegetables()

@app.get("/cities", response_model=List[str])
async def list_cities():
    """
    List all supported cities
    """
    return list_supported_cities()

@app.get("/city/{city}/prices", response_model=List[Dict[str, Any]])
async def get_city_prices(city: str):
    """
    Get all available prices for a city
    """
    city_mapping = normalize_city_name(city)
    if not city_mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported city: {city}"
        )
    
    prices = db.get_city_prices(city.lower())
    return prices

@app.get("/vegetable/{vegetable}/prices", response_model=List[Dict[str, Any]])
async def get_vegetable_prices(vegetable: str):
    """
    Get prices for a vegetable across all cities
    """
    normalized_veg = normalize_vegetable_name(vegetable)
    if not normalized_veg:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown vegetable: {vegetable}"
        )
    
    prices = db.get_vegetable_prices_across_cities(normalized_veg)
    return prices

@app.post("/admin/cache/clear")
async def clear_cache():
    """
    Clear all cache (admin endpoint)
    """
    price_cache.clear()
    market_cache.clear()
    return {"message": "Cache cleared successfully"}

@app.post("/admin/database/cleanup")
async def cleanup_database(days: int = 30):
    """
    Clean up old database records (admin endpoint)
    """
    cleaned_count = db.cleanup_old_data(days)
    return {"message": f"Cleaned up {cleaned_count} old records"}

# Helper functions
def is_recent_enough(timestamp_str: str, max_age_hours: int = 6) -> bool:
    """
    Check if data is recent enough to serve from database
    """
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        age = datetime.now() - timestamp
        return age < timedelta(hours=max_age_hours)
    except:
        return False

async def scrape_with_timeout(city: str, vegetable: str, timeout_seconds: int = 30):
    """
    Scrape data with timeout to avoid hanging the API
    """
    try:
        # Run scraper with timeout
        task = asyncio.create_task(
            asyncio.to_thread(scraper.get_vegetable_price, city, vegetable, headless=True)
        )
        
        result = await asyncio.wait_for(task, timeout=timeout_seconds)
        return result
        
    except asyncio.TimeoutError:
        logger.warning(f"⏰ Scraping timeout for {city} {vegetable}")
        return None
    except Exception as e:
        logger.error(f"❌ Scraping error: {e}")
        return None

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not Found", "message": str(exc.detail), "timestamp": datetime.now()}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal Server Error", "message": "Something went wrong", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
