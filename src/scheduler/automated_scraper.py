"""
Automated scraper that runs at scheduled times (9 AM and 6 PM daily)
Collects vegetable prices from multiple cities and stores in database
"""

import schedule
import time
import logging
import os
from datetime import datetime
from typing import List, Tuple
from dotenv import load_dotenv

# Import our existing components
from src.scraper.improved_scraper import ImprovedAgmarknetScraper
from src.database.price_db import PriceDatabase

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutomatedScraper:
    """
    Automated scraper that runs on schedule to collect vegetable prices
    """
    
    def __init__(self):
        """Initialize scraper components"""
        self.scraper = ImprovedAgmarknetScraper()
        self.db = PriceDatabase()
        
        # Pre-defined city/vegetable combinations to scrape
        self.scraping_targets: List[Tuple[str, str]] = [
            # Major cities with all 3 vegetables
            ("mumbai", "tomato"),
            ("mumbai", "onion"), 
            ("mumbai", "potato"),
            ("delhi", "tomato"),
            ("delhi", "onion"),
            ("delhi", "potato"),
            ("pune", "tomato"),
            ("pune", "onion"),
            ("pune", "potato"),
            ("bengaluru", "tomato"),
            ("bengaluru", "onion"),
            ("bengaluru", "potato"),
            ("hyderabad", "tomato"),
            ("hyderabad", "onion"),
            ("hyderabad", "potato"),
            ("chennai", "tomato"),
            ("chennai", "onion"),
            ("chennai", "potato"),
            ("kolkata", "tomato"),
            ("kolkata", "onion"),
            ("kolkata", "potato"),
            ("ahmedabad", "tomato"),
            ("ahmedabad", "onion"),
            ("ahmedabad", "potato"),
            ("jaipur", "tomato"),
            ("jaipur", "onion"),
            ("jaipur", "potato"),
            ("lucknow", "tomato"),
            ("lucknow", "onion"),
            ("lucknow", "potato"),
        ]
        
        logger.info(f"🎯 Initialized scraper with {len(self.scraping_targets)} targets")
    
    def scrape_all_targets(self):
        """
        Scrape all predefined city/vegetable combinations
        This runs twice daily at 9 AM and 6 PM
        """
        start_time = datetime.now()
        logger.info(f"🕒 Starting scheduled scraping at {start_time}")
        
        total_scraped = 0
        successful_scrapes = 0
        failed_scrapes = 0
        
        for city, vegetable in self.scraping_targets:
            try:
                logger.info(f"🥬 Scraping {vegetable} prices in {city}...")
                
                # Use headless mode for automated runs
                headless = os.getenv('SCRAPE_HEADLESS', 'true').lower() == 'true'
                result = self.scraper.get_vegetable_price(city, vegetable, headless=headless)
                
                if result:
                    # Store in database
                    self.db.insert_price(result)
                    successful_scrapes += 1
                    logger.info(f"✅ Stored {vegetable} price for {city}: ₹{result['price_per_kg']}/kg from {result.get('market', 'unknown market')}")
                else:
                    failed_scrapes += 1
                    logger.warning(f"❌ No data found for {vegetable} in {city}")
                
                total_scraped += 1
                
                # Small delay between scrapes to be respectful to the website
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Error scraping {vegetable} in {city}: {e}")
                failed_scrapes += 1
                total_scraped += 1
                
                # Continue with next target even if one fails
                continue
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Log summary
        logger.info(f"📊 Scraping completed in {duration:.1f} seconds:")
        logger.info(f"   ✅ Successful: {successful_scrapes}")
        logger.info(f"   ❌ Failed: {failed_scrapes}")
        logger.info(f"   📈 Total: {total_scraped}")
        
        # Log database stats
        try:
            stats = self.db.get_db_stats()
            logger.info(f"📈 Database now has {stats.get('total_records', 0)} total records")
        except Exception as e:
            logger.warning(f"⚠️ Could not get database stats: {e}")
    
    def scrape_single_target(self, city: str, vegetable: str):
        """
        Scrape a single city/vegetable combination (for testing)
        """
        logger.info(f"🎯 Manual scrape: {vegetable} in {city}")
        
        try:
            result = self.scraper.get_vegetable_price(city, vegetable, headless=True)
            
            if result:
                self.db.insert_price(result)
                logger.info(f"✅ Success: ₹{result['price_per_kg']}/kg")
                return result
            else:
                logger.warning(f"❌ No data found")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None
    
    def setup_schedule(self):
        """
        Set up daily schedule for 9 AM and 6 PM
        """
        # Schedule for 9:00 AM daily (morning market prices)
        schedule.every().day.at("09:00").do(self.scrape_all_targets)
        
        # Schedule for 6:00 PM daily (evening market updates)
        schedule.every().day.at("18:00").do(self.scrape_all_targets)
        
        logger.info("📅 Scheduled automated scraping:")
        logger.info("   🌅 Daily at 9:00 AM (morning market prices)")
        logger.info("   🌇 Daily at 6:00 PM (evening market updates)")
        
        # Show next run times
        next_runs = schedule.jobs
        for job in next_runs:
            logger.info(f"   ⏰ Next run: {job.next_run}")
    
    def run_scheduler(self):
        """
        Run the scheduler (blocking operation)
        This keeps the scheduler running continuously
        """
        self.setup_schedule()
        
        logger.info("🚀 Automated scraper is running...")
        logger.info("💡 Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for scheduled jobs
        except KeyboardInterrupt:
            logger.info("👋 Automated scraper stopped by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            raise

def main():
    """
    Main function to run automated scraper
    """
    print("🌟 SabjiGPT Automated Scraper")
    print("=" * 50)
    
    scraper = AutomatedScraper()
    
    # Check command line argument for immediate run
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--run-once":
        print("🔄 Running immediate scrape...")
        scraper.scrape_all_targets()
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 Testing with single target...")
        result = scraper.scrape_single_target("pune", "onion")
        if result:
            print(f"✅ Test successful: {result}")
        else:
            print("❌ Test failed")
    else:
        print("⏰ Starting scheduled runs (9 AM & 6 PM daily)")
        scraper.run_scheduler()

if __name__ == "__main__":
    main()
