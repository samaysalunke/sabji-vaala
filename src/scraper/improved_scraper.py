"""
Improved scraper that tries multiple markets and handles data availability better
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import json
from datetime import datetime, timedelta
import time
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedAgmarknetScraper:
    """
    Improved scraper that tries multiple markets and date ranges
    """
    
    def __init__(self):
        self.base_url = "https://agmarknet.gov.in"
        self.search_url = f"{self.base_url}/SearchCmmMkt.aspx"
        
        # Priority order for Mumbai markets (most likely to have vegetable data)
        self.mumbai_market_priorities = [
            "Mumbai",  # Basic Mumbai market
            "Mumbai- Fruit Market",  # Fruit market might have vegetables too
            "Vashi New Mumbai",  # New Mumbai wholesale market
            "Mumbai- Thane Market"  # Thane is nearby
        ]
        
    def get_vegetable_price(self, city="Mumbai", vegetable="tomato", headless=True):
        """
        Get vegetable price with fallback logic
        """
        logger.info(f"🥬 Getting {vegetable} price for {city}...")
        
        # Map vegetables to their commodity values (from exploration)
        commodity_mapping = {
            "tomato": "78",
            "potato": "23",  # Need to verify
            "onion": "71"    # Need to verify
        }
        
        commodity_value = commodity_mapping.get(vegetable.lower())
        if not commodity_value:
            logger.error(f"❌ Unknown vegetable: {vegetable}")
            return None
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless, slow_mo=500)
            page = browser.new_page()
            
            try:
                # Navigate to search page
                page.goto(self.search_url, timeout=30000)
                page.wait_for_load_state('networkidle')
                
                # Select commodity
                logger.info(f"🥬 Selecting {vegetable} (value: {commodity_value})...")
                page.select_option('select#ddlCommodity', value=commodity_value)
                time.sleep(1)
                
                # Select state (Maharashtra for Mumbai)
                logger.info("🏛️ Selecting Maharashtra...")
                page.select_option('select#ddlState', value='MH')
                time.sleep(3)  # Wait for AJAX district loading
                
                # Select Mumbai district
                logger.info("🏙️ Selecting Mumbai district...")
                page.select_option('select#ddlDistrict', value='10')
                time.sleep(3)  # Wait for AJAX market loading
                
                # Try different markets in priority order
                market_options = page.query_selector_all('select#ddlMarket option')
                available_markets = []
                
                for option in market_options:
                    value = option.get_attribute('value')
                    text = option.inner_text().strip()
                    if value and value != "0":
                        available_markets.append((value, text))
                
                logger.info(f"📍 Found {len(available_markets)} markets in Mumbai")
                
                # Try markets in priority order
                for priority_market in self.mumbai_market_priorities:
                    for market_value, market_text in available_markets:
                        if priority_market.lower() in market_text.lower():
                            logger.info(f"🎯 Trying market: {market_text}")
                            
                            result = self._try_market(page, market_value, market_text, vegetable, city)
                            if result:
                                return result
                            break
                
                # If priority markets don't work, try all others
                logger.info("🔄 Trying all other markets...")
                for market_value, market_text in available_markets:
                    if not any(priority.lower() in market_text.lower() for priority in self.mumbai_market_priorities):
                        logger.info(f"🎯 Trying market: {market_text}")
                        
                        result = self._try_market(page, market_value, market_text, vegetable, city)
                        if result:
                            return result
                
                logger.warning(f"❌ No {vegetable} price data found in any Mumbai market")
                return None
                
            except Exception as e:
                logger.error(f"❌ Scraping failed: {e}")
                page.screenshot(path=f"error_{vegetable}_{city}.png")
                return None
                
            finally:
                browser.close()
    
    def _try_market(self, page, market_value, market_text, vegetable, city):
        """
        Try getting data from a specific market
        """
        try:
            # Select market
            page.select_option('select#ddlMarket', value=market_value)
            time.sleep(1)
            
            # Set date range (try last 7 days)
            self._set_date_range(page, days_back=7)
            
            # Click search
            page.click('input#btnGo')
            time.sleep(3)
            
            # Extract price data
            price_data = self._extract_price_data(page, market_text, vegetable, city)
            
            if price_data:
                logger.info(f"✅ Found data in {market_text}: ₹{price_data['price']}")
                return price_data
            else:
                logger.info(f"📭 No data in {market_text}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Error with market {market_text}: {e}")
            return None
    
    def _set_date_range(self, page, days_back=7):
        """
        Set date range for price search
        """
        try:
            today = datetime.now()
            start_date = today - timedelta(days=days_back)
            
            date_from = page.query_selector('input#txtDateFrom')
            date_to = page.query_selector('input#txtDateTo')
            
            if date_from:
                date_from.fill(start_date.strftime('%d/%m/%Y'))
                logger.info(f"📅 Set start date: {start_date.strftime('%d/%m/%Y')}")
            
            if date_to:
                date_to.fill(today.strftime('%d/%m/%Y'))
                logger.info(f"📅 Set end date: {today.strftime('%d/%m/%Y')}")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not set date range: {e}")
    
    def _extract_price_data(self, page, market_name, vegetable, city):
        """
        Extract price data from results table
        """
        try:
            # Look for the main results table
            tables = page.query_selector_all('table')
            
            for table in tables:
                rows = table.query_selector_all('tr')
                
                if len(rows) < 2:
                    continue
                
                # Check if this is a price table by looking at headers
                header_row = rows[0]
                header_cells = header_row.query_selector_all('td, th')
                header_texts = [cell.inner_text().strip().lower() for cell in header_cells]
                
                # Look for price-related headers
                if any(keyword in ' '.join(header_texts) for keyword in ['price', 'modal', 'min', 'max']):
                    logger.info(f"📊 Found price table with headers: {header_texts}")
                    
                    # Process data rows
                    for row in rows[1:]:
                        cells = row.query_selector_all('td')
                        cell_texts = [cell.inner_text().strip() for cell in cells]
                        
                        # Skip "No Data Found" rows
                        if len(cell_texts) == 1 and 'no data' in cell_texts[0].lower():
                            continue
                        
                        # Look for price data
                        if len(cell_texts) >= 8:  # Typical price table has many columns
                            # Try to find price columns (usually last few columns)
                            for i, cell_text in enumerate(cell_texts[-5:], len(cell_texts)-5):
                                if self._is_price_value(cell_text):
                                    price = self._clean_price(cell_text)
                                    if 10 <= price <= 10000:  # Reasonable range
                                        return {
                                            "city": city,
                                            "vegetable": vegetable,
                                            "price": price,
                                            "price_per": "quintal",  # Agmarknet uses quintal
                                            "price_per_kg": round(price / 100, 2),  # Convert to per kg
                                            "currency": "INR",
                                            "market": market_name,
                                            "timestamp": datetime.now().isoformat(),
                                            "source": "agmarknet.gov.in",
                                            "raw_data": cell_texts
                                        }
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting price data: {e}")
            return None
    
    def _is_price_value(self, text):
        """
        Check if text looks like a price value
        """
        if not text or text == '-':
            return False
        
        # Look for number patterns
        price_pattern = r'^\d+(?:,\d+)*(?:\.\d+)?$'
        return bool(re.match(price_pattern, text.replace(' ', '')))
    
    def _clean_price(self, text):
        """
        Clean and convert price text to float
        """
        try:
            # Remove commas and spaces
            cleaned = text.replace(',', '').replace(' ', '')
            return float(cleaned)
        except ValueError:
            return 0

def test_improved_scraper():
    """
    Test the improved scraper
    """
    print("🧪 Testing ImprovedAgmarknetScraper...")
    
    scraper = ImprovedAgmarknetScraper()
    
    # Test with Mumbai tomato
    result = scraper.get_vegetable_price("Mumbai", "tomato", headless=False)
    
    if result:
        print("✅ Success!")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Failed to get price data")
        print("This might be normal if there's no current data available")

if __name__ == "__main__":
    test_improved_scraper()
