"""
Minimal viable scraper - just get Mumbai tomato prices working
Built on findings from explore_agmarknet.py

Key findings:
- Tomato has value="78" in ddlCommodity dropdown
- Maharashtra (ddlState) -> Mumbai (ddlDistrict) 
- Form uses ASP.NET with ViewState
- Submit button is btnGo with validation
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import json
from datetime import datetime
import time
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgmarknetScraperV1:
    """
    Developer approach: Start with 1 city, 1 vegetable
    Make it work, then scale
    """
    
    def __init__(self):
        self.base_url = "https://agmarknet.gov.in"
        self.search_url = f"{self.base_url}/SearchCmmMkt.aspx"
        
        # Discovered mappings from exploration
        self.commodity_values = {
            "tomato": "78",  # Found: <option value="78">Tomato</option>
            "potato": "23",  # Likely value, need to verify
            "onion": "15"    # Likely value, need to verify
        }
        
        self.state_values = {
            "maharashtra": "MH",
            "delhi": "DL", 
            "karnataka": "KT"
        }
        
    def get_tomato_price_mumbai(self, headless=True):
        """
        Hardcoded first attempt - just prove we can get data
        """
        logger.info("🍅 Starting Mumbai tomato price scraping...")
        
        with sync_playwright() as p:
            # Use headless=False initially to see what's happening during development
            browser = p.chromium.launch(headless=headless, slow_mo=500)
            page = browser.new_page()
            
            try:
                # Navigate to price search
                logger.info(f"📍 Navigating to {self.search_url}")
                page.goto(self.search_url, timeout=30000)
                
                # Wait for page to load completely
                page.wait_for_load_state('networkidle')
                
                # Select commodity (Tomato = value 78)
                logger.info("🥬 Selecting Tomato commodity...")
                page.select_option('select#ddlCommodity', value='78')
                time.sleep(1)  # Let the page update
                
                # Select state (Maharashtra)
                logger.info("🏛️ Selecting Maharashtra state...")
                page.select_option('select#ddlState', value='MH')
                
                # Wait for district dropdown to populate (due to AJAX)
                logger.info("⏳ Waiting for district dropdown to load...")
                page.wait_for_timeout(2000)
                
                # Look for Mumbai/Bombay in district options
                logger.info("🏙️ Looking for Mumbai in district options...")
                district_options = page.query_selector_all('select#ddlDistrict option')
                mumbai_value = None
                
                for option in district_options:
                    text = option.inner_text().lower()
                    value = option.get_attribute('value')
                    if 'mumbai' in text or 'bombay' in text:
                        mumbai_value = value
                        logger.info(f"✅ Found Mumbai: {text} = {value}")
                        break
                
                if not mumbai_value:
                    logger.error("❌ Mumbai not found in district dropdown")
                    return None
                
                # Select Mumbai district
                page.select_option('select#ddlDistrict', value=mumbai_value)
                time.sleep(1)
                
                # Click search (Go button)
                logger.info("🔍 Clicking search button...")
                page.click('input#btnGo')
                
                # Wait for results to load
                logger.info("⏳ Waiting for results...")
                try:
                    # Look for price table or results
                    page.wait_for_selector('table', timeout=15000)
                    
                    # Give it more time to fully load
                    time.sleep(3)
                    
                    # Extract price data
                    price_data = self._extract_price_data(page)
                    
                    if price_data:
                        logger.info(f"✅ Successfully scraped price: ₹{price_data['price']}/kg")
                        return price_data
                    else:
                        logger.warning("⚠️ No price data found in results")
                        # Take screenshot for debugging
                        page.screenshot(path="no_data_screenshot.png")
                        return None
                        
                except PlaywrightTimeoutError:
                    logger.error("❌ Timeout waiting for results")
                    page.screenshot(path="timeout_screenshot.png")
                    return None
                
            except Exception as e:
                logger.error(f"❌ Scraping failed: {e}")
                # Take screenshot for debugging
                page.screenshot(path="error_screenshot.png")
                
                # Save page content for analysis
                with open("error_page_content.html", "w", encoding='utf-8') as f:
                    f.write(page.content())
                
                raise
                
            finally:
                browser.close()
    
    def _extract_price_data(self, page):
        """
        Extract price information from the results page
        """
        logger.info("📊 Extracting price data from page...")
        
        # Try different table selectors
        possible_selectors = [
            'table#gvDetails',
            'table[id*="grid"]',
            'table[id*="GridView"]',
            'table.table',
            'table'
        ]
        
        for selector in possible_selectors:
            tables = page.query_selector_all(selector)
            if tables:
                logger.info(f"📋 Found {len(tables)} tables with selector: {selector}")
                
                for i, table in enumerate(tables):
                    rows = table.query_selector_all('tr')
                    logger.info(f"  Table {i+1}: {len(rows)} rows")
                    
                    if len(rows) > 1:  # Has header + data
                        # Print table structure for debugging
                        for j, row in enumerate(rows[:3]):  # First 3 rows
                            cells = row.query_selector_all('td, th')
                            cell_texts = [cell.inner_text().strip() for cell in cells]
                            logger.info(f"    Row {j+1}: {cell_texts}")
                        
                        # Look for price data
                        for row_idx, row in enumerate(rows[1:], 1):  # Skip header
                            cells = row.query_selector_all('td')
                            cell_texts = [cell.inner_text().strip() for cell in cells]
                            
                            if len(cell_texts) >= 4:  # Assuming: Market, Variety, Min, Max, Modal
                                # Look for price patterns (numbers)
                                price_pattern = r'[\d,]+\.?\d*'
                                
                                for cell_text in cell_texts:
                                    if re.search(price_pattern, cell_text):
                                        try:
                                            # Clean price text and extract number
                                            price_str = re.findall(price_pattern, cell_text)[0]
                                            price = float(price_str.replace(',', ''))
                                            
                                            if 10 <= price <= 10000:  # Reasonable price range
                                                logger.info(f"💰 Found price: ₹{price}")
                                                
                                                return {
                                                    "city": "Mumbai",
                                                    "vegetable": "tomato", 
                                                    "price": price,
                                                    "currency": "INR",
                                                    "unit": "kg",
                                                    "timestamp": datetime.now().isoformat(),
                                                    "source": "agmarknet.gov.in",
                                                    "raw_data": cell_texts
                                                }
                                        except (ValueError, IndexError):
                                            continue
        
        # If no structured data found, look for any price-like text
        page_text = page.content()
        price_matches = re.findall(r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)', page_text)
        
        if price_matches:
            logger.info(f"💡 Found price patterns in page text: {price_matches}")
            try:
                price = float(price_matches[0].replace(',', ''))
                return {
                    "city": "Mumbai",
                    "vegetable": "tomato",
                    "price": price,
                    "currency": "INR", 
                    "unit": "kg",
                    "timestamp": datetime.now().isoformat(),
                    "source": "agmarknet.gov.in",
                    "extraction_method": "text_pattern"
                }
            except ValueError:
                pass
        
        logger.warning("❌ Could not extract price data")
        return None

def test_scraper():
    """
    Quick test function
    """
    print("🧪 Testing AgmarknetScraper...")
    
    scraper = AgmarknetScraperV1()
    
    # Test with visible browser first for debugging
    result = scraper.get_tomato_price_mumbai(headless=False)
    
    if result:
        print("✅ Success!")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Failed to get price data")
        print("Check error_screenshot.png and error_page_content.html for debugging")

if __name__ == "__main__":
    test_scraper()
