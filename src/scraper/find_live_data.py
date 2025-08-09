"""
Find any available live data from Agmarknet to prove our scraper works
"""

from src.scraper.improved_scraper import ImprovedAgmarknetScraper
from src.data.vegetables import VEGETABLE_MASTER, CITY_MAPPINGS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_any_live_data():
    """
    Try different combinations to find any available data
    """
    scraper = ImprovedAgmarknetScraper()
    
    # Try these combinations (most likely to have data)
    test_combinations = [
        # Major cities with common vegetables
        ("delhi", "tomato"),
        ("delhi", "potato"), 
        ("delhi", "onion"),
        ("bangalore", "tomato"),
        ("bangalore", "potato"),
        ("hyderabad", "tomato"),
        ("chennai", "tomato"),
        ("kolkata", "potato"),
        ("pune", "onion"),
        ("mumbai", "potato"),  # Try potato in Mumbai instead of tomato
        ("mumbai", "onion"),
    ]
    
    logger.info("🔍 Searching for live data across cities and vegetables...")
    
    found_data = []
    
    for city, vegetable in test_combinations:
        logger.info(f"\n🧪 Testing {vegetable} in {city}...")
        
        try:
            # Try with headless=True for faster testing
            result = scraper.get_vegetable_price(city, vegetable, headless=True)
            
            if result:
                logger.info(f"✅ SUCCESS! Found data: {city} {vegetable} = ₹{result['price_per_kg']}/kg")
                found_data.append(result)
                
                # Save to database
                from src.database.price_db import PriceDatabase
                db = PriceDatabase()
                db.insert_price(result)
                db.close()
                
                # Don't overwhelm the server - we found working data
                if len(found_data) >= 3:
                    logger.info("🎉 Found enough data samples, stopping search")
                    break
            else:
                logger.info(f"📭 No data for {vegetable} in {city}")
                
        except Exception as e:
            logger.error(f"❌ Error testing {city} {vegetable}: {e}")
            continue
    
    if found_data:
        logger.info(f"\n🎉 Successfully found {len(found_data)} live data points!")
        for data in found_data:
            logger.info(f"  📊 {data['city']} {data['vegetable']}: ₹{data.get('price_per_kg', data['price'])}/kg from {data.get('market', 'unknown market')}")
        return found_data
    else:
        logger.warning("❌ No live data found in any tested combinations")
        logger.info("This could mean:")
        logger.info("  - Markets are closed (weekend/holiday)")
        logger.info("  - Data hasn't been updated today")
        logger.info("  - Network issues")
        return []

if __name__ == "__main__":
    find_any_live_data()
