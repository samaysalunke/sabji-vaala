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
        
        # Import city mappings
        from src.data.vegetables import normalize_city_name
        
        # Get state and district for the city
        city_mapping = normalize_city_name(city)
        if not city_mapping:
            logger.error(f"❌ Unsupported city: {city}")
            return None
        
        state_name, district_name = city_mapping
        
        # Map vegetables to their commodity values (from exploration)
        commodity_mapping = {
            "tomato": "78",
            "potato": "24",  # Verified from HTML
            "onion": "23"    # Verified from HTML
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
                
                # Select state based on city mapping
                logger.info(f"🏛️ Selecting {state_name} state...")
                page.select_option('select#ddlState', value=state_name)
                time.sleep(3)  # Wait for AJAX district loading
                
                # Find and select the correct district
                logger.info(f"🏙️ Looking for {district_name} district...")
                district_options = page.query_selector_all('select#ddlDistrict option')
                district_value = None
                
                for option in district_options:
                    value = option.get_attribute('value')
                    text = option.inner_text().strip()
                    if district_name.lower() in text.lower() or text.lower() in district_name.lower():
                        district_value = value
                        logger.info(f"✅ Found district: {text} = {value}")
                        break
                
                if not district_value:
                    logger.error(f"❌ District {district_name} not found")
                    return None
                
                page.select_option('select#ddlDistrict', value=district_value)
                time.sleep(3)  # Wait for AJAX market loading
                
                # Try different markets in priority order
                market_options = page.query_selector_all('select#ddlMarket option')
                available_markets = []
                
                for option in market_options:
                    value = option.get_attribute('value')
                    text = option.inner_text().strip()
                    if value and value != "0":
                        available_markets.append((value, text))
                
                logger.info(f"📍 Found {len(available_markets)} markets in {city}")
                
                # Try all markets for this city
                for market_value, market_text in available_markets:
                    logger.info(f"🎯 Trying market: {market_text}")
                    
                    result = self._try_market(page, market_value, market_text, vegetable, city)
                    if result:
                        return result
                
                logger.warning(f"❌ No {vegetable} price data found in any {city} market")
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
            self._set_date_range(page, "02-Aug-2025", "08-Aug-2025")
            
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
    
    def _set_date_range(self, page, from_date="02-Aug-2025", to_date="08-Aug-2025"):
        """
        Set date range for price search using DD-MMM-YYYY format
        FIXED: Use correct field IDs - txtDate (not txtDateFrom) and txtDateTo
        """
        try:
            # Use the correct field IDs found from HTML inspection
            logger.info(f"📅 Setting date range: {from_date} to {to_date}")
            
            # Clear and set the FROM date (txtDate)
            page.evaluate(f'document.getElementById("txtDate").value = "{from_date}"')
            
            # Clear and set the TO date (txtDateTo) 
            page.evaluate(f'document.getElementById("txtDateTo").value = "{to_date}"')
            
            # Verify the dates were set
            actual_from = page.evaluate('document.getElementById("txtDate").value')
            actual_to = page.evaluate('document.getElementById("txtDateTo").value')
            
            logger.info(f"✅ Verified dates - From: {actual_from}, To: {actual_to}")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not set date range: {e}")
    
    def _extract_price_data(self, page, market_name, vegetable, city):
        """
        Extract price data from results table - improved for live data
        """
        try:
            # Look for ALL tables and analyze them thoroughly
            tables = page.query_selector_all('table')
            logger.info(f"📊 Analyzing {len(tables)} tables for price data...")
            
            for table_idx, table in enumerate(tables):
                rows = table.query_selector_all('tr')
                
                if len(rows) < 2:
                    continue
                
                logger.info(f"📋 Table {table_idx + 1}: {len(rows)} rows")
                
                # Check header row
                header_row = rows[0]
                header_cells = header_row.query_selector_all('td, th')
                header_texts = [cell.inner_text().strip() for cell in header_cells]
                
                # Log the headers for debugging
                if header_texts:
                    logger.info(f"  Headers: {header_texts}")
                
                # Look for price table indicators
                header_text_lower = ' '.join(header_texts).lower()
                is_price_table = any(keyword in header_text_lower for keyword in [
                    'price', 'modal', 'min', 'max', 'quintal', 'commodity', 'variety'
                ])
                
                if not is_price_table:
                    continue
                
                logger.info(f"✅ Price table detected in table {table_idx + 1}")
                
                # Process ALL data rows (not just checking for "No Data Found")
                data_rows_found = 0
                for row_idx, row in enumerate(rows[1:], 1):
                    cells = row.query_selector_all('td')
                    cell_texts = [cell.inner_text().strip() for cell in cells]
                    
                    if not cell_texts:
                        continue
                    
                    logger.info(f"  Row {row_idx}: {cell_texts}")
                    
                    # Skip explicit "No Data Found" messages
                    if len(cell_texts) == 1 and 'no data' in cell_texts[0].lower():
                        logger.info("    ↳ No data message - skipping")
                        continue
                    
                    # Look for rows with actual data (multiple columns)
                    if len(cell_texts) >= 6:  # At least 6 columns for price data
                        data_rows_found += 1
                        logger.info(f"    ↳ Data row {data_rows_found} detected")
                        
                        # Look for numeric price values
                        price_found = None
                        for cell_text in cell_texts:
                            if self._is_price_value(cell_text):
                                price = self._clean_price(cell_text)
                                # Reasonable price range for vegetable (₹100-₹10000 per quintal)
                                if 100 <= price <= 10000:
                                    price_found = price
                                    logger.info(f"    ↳ Found price: ₹{price}")
                                    break
                        
                        if price_found:
                            # Extract other data from the row
                            market_from_row = cell_texts[3] if len(cell_texts) > 3 else market_name
                            variety = cell_texts[5] if len(cell_texts) > 5 else "Local"
                            
                            result = {
                                "city": city,
                                "vegetable": vegetable,
                                "price": price_found,
                                "price_per": "quintal",  # Agmarknet uses quintal
                                "price_per_kg": round(price_found / 100, 2),  # Convert to per kg
                                "currency": "INR",
                                "market": market_from_row,
                                "variety": variety,
                                "timestamp": datetime.now().isoformat(),
                                "source": "agmarknet.gov.in",
                                "raw_data": cell_texts
                            }
                            
                            logger.info(f"🎉 SUCCESS: Extracted price data ₹{price_found}")
                            return result
                
                if data_rows_found > 0:
                    logger.info(f"  Found {data_rows_found} data rows but no valid prices")
                else:
                    logger.info("  No data rows found in this table")
            
            logger.warning("❌ No price data found in any table")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting price data: {e}")
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
