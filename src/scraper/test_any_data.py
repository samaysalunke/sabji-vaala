"""
Test scraper by finding ANY available data to prove it works
"""

from playwright.sync_api import sync_playwright
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_any_available_data():
    """
    Find any available price data to prove our scraper logic works
    """
    logger.info("🔍 Searching for ANY available price data...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            page.goto("https://agmarknet.gov.in/SearchCmmMkt.aspx", timeout=30000)
            page.wait_for_load_state('networkidle')
            
            # Test different state + commodity combinations
            test_combinations = [
                # Format: (state_code, state_name, commodity_value, commodity_name)
                ("DL", "Delhi", "78", "Tomato"),
                ("KT", "Karnataka", "78", "Tomato"),
                ("DL", "Delhi", "23", "Potato"),
                ("MH", "Maharashtra", "71", "Onion"),  # Assuming onion is 71
                ("DL", "Delhi", "17", "Apple"),  # We saw apple in the list
            ]
            
            for state_code, state_name, commodity_value, commodity_name in test_combinations:
                logger.info(f"\n🧪 Testing {commodity_name} in {state_name}...")
                
                # Reset form
                page.reload()
                page.wait_for_load_state('networkidle')
                
                # Select commodity
                page.select_option('select#ddlCommodity', value=commodity_value)
                time.sleep(1)
                
                # Select state
                page.select_option('select#ddlState', value=state_code)
                time.sleep(3)
                
                # Get first available district
                district_options = page.query_selector_all('select#ddlDistrict option')
                first_district = None
                for option in district_options:
                    value = option.get_attribute('value')
                    text = option.inner_text()
                    if value and value != "0":
                        first_district = (value, text)
                        break
                
                if first_district:
                    district_value, district_name = first_district
                    logger.info(f"📍 Trying district: {district_name}")
                    
                    page.select_option('select#ddlDistrict', value=district_value)
                    time.sleep(2)
                    
                    # Check if market dropdown exists and select first market
                    market_dropdown = page.query_selector('select#ddlMarket')
                    if market_dropdown:
                        market_options = page.query_selector_all('select#ddlMarket option')
                        for option in market_options:
                            value = option.get_attribute('value')
                            text = option.inner_text()
                            if value and value != "0":
                                logger.info(f"🏪 Selecting market: {text}")
                                page.select_option('select#ddlMarket', value=value)
                                break
                    
                    # Set recent date range
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    week_ago = today - timedelta(days=7)
                    
                    date_to = page.query_selector('input#txtDateTo')
                    if date_to:
                        date_to.fill(today.strftime('%d/%m/%Y'))
                    
                    # Click search
                    logger.info("🔍 Searching...")
                    page.click('input#btnGo')
                    time.sleep(5)
                    
                    # Check for data
                    tables = page.query_selector_all('table')
                    data_found = False
                    
                    for table in tables:
                        rows = table.query_selector_all('tr')
                        if len(rows) > 1:
                            for row in rows[1:]:
                                cells = row.query_selector_all('td')
                                cell_texts = [cell.inner_text().strip() for cell in cells]
                                
                                # Check if this row has actual data (not "No Data Found")
                                if len(cell_texts) > 5 and not any('no data' in text.lower() for text in cell_texts):
                                    logger.info(f"✅ FOUND DATA! {state_name} {district_name} {commodity_name}")
                                    logger.info(f"📊 Data: {cell_texts}")
                                    data_found = True
                                    break
                    
                    if data_found:
                        logger.info("🎉 SUCCESS! Found working data combination")
                        logger.info("🔍 Keeping browser open for 30 seconds...")
                        time.sleep(30)
                        return True
                    else:
                        logger.info(f"📭 No data for {commodity_name} in {state_name}")
            
            logger.info("❌ No data found in any tested combinations")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    find_any_available_data()
