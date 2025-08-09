"""
Debug version of the scraper to understand form behavior better
"""

from playwright.sync_api import sync_playwright
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_agmarknet_form():
    """
    Interactive debugging to understand the form better
    """
    logger.info("🔍 Starting interactive debugging...")
    
    with sync_playwright() as p:
        # Use visible browser for debugging
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            # Navigate to price search
            page.goto("https://agmarknet.gov.in/SearchCmmMkt.aspx", timeout=30000)
            page.wait_for_load_state('networkidle')
            
            # First, let's see what commodities are available
            logger.info("📋 Available commodities:")
            commodity_options = page.query_selector_all('select#ddlCommodity option')
            tomato_found = False
            for option in commodity_options[:20]:  # Show first 20
                value = option.get_attribute('value')
                text = option.inner_text()
                logger.info(f"  {value}: {text}")
                if 'tomato' in text.lower():
                    tomato_found = True
                    logger.info(f"  🍅 TOMATO FOUND: {value}: {text}")
            
            if not tomato_found:
                logger.warning("❌ Tomato not found in first 20 options")
            
            # Select tomato
            logger.info("🍅 Selecting Tomato...")
            page.select_option('select#ddlCommodity', value='78')
            time.sleep(2)
            
            # Check states
            logger.info("🏛️ Available states:")
            state_options = page.query_selector_all('select#ddlState option')
            for option in state_options[:10]:
                value = option.get_attribute('value')
                text = option.inner_text()
                logger.info(f"  {value}: {text}")
            
            # Select Maharashtra
            logger.info("🏛️ Selecting Maharashtra...")
            page.select_option('select#ddlState', value='MH')
            time.sleep(3)  # Wait for AJAX
            
            # Check districts after state selection
            logger.info("🏙️ Available districts in Maharashtra:")
            district_options = page.query_selector_all('select#ddlDistrict option')
            mumbai_options = []
            for option in district_options:
                value = option.get_attribute('value')
                text = option.inner_text()
                logger.info(f"  {value}: {text}")
                if 'mumbai' in text.lower() or 'bombay' in text.lower():
                    mumbai_options.append((value, text))
            
            if mumbai_options:
                mumbai_value, mumbai_text = mumbai_options[0]
                logger.info(f"🎯 Using Mumbai: {mumbai_value} = {mumbai_text}")
                page.select_option('select#ddlDistrict', value=mumbai_value)
                time.sleep(3)
            
            # Check if there's a market dropdown
            market_dropdown = page.query_selector('select#ddlMarket')
            if market_dropdown:
                logger.info("🏪 Market dropdown found! Available markets:")
                market_options = page.query_selector_all('select#ddlMarket option')
                for option in market_options:
                    value = option.get_attribute('value')
                    text = option.inner_text()
                    logger.info(f"  {value}: {text}")
                
                # Select first available market (not "Select")
                for option in market_options:
                    value = option.get_attribute('value')
                    text = option.inner_text()
                    if value and value != "0":
                        logger.info(f"🎯 Selecting market: {text}")
                        page.select_option('select#ddlMarket', value=value)
                        break
            else:
                logger.info("ℹ️ No market dropdown found")
            
            # Check date inputs
            date_from = page.query_selector('input#txtDateFrom')
            date_to = page.query_selector('input#txtDateTo')
            
            if date_from:
                current_date_from = date_from.input_value()
                logger.info(f"📅 Date From: {current_date_from}")
            
            if date_to:
                current_date_to = date_to.input_value()
                logger.info(f"📅 Date To: {current_date_to}")
            
            # Try setting recent dates
            from datetime import datetime, timedelta
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            
            if date_from:
                date_from.fill(yesterday.strftime('%d/%m/%Y'))
                logger.info(f"📅 Set Date From to: {yesterday.strftime('%d/%m/%Y')}")
            
            if date_to:
                date_to.fill(today.strftime('%d/%m/%Y'))
                logger.info(f"📅 Set Date To to: {today.strftime('%d/%m/%Y')}")
            
            time.sleep(1)
            
            # Click search
            logger.info("🔍 Clicking Go button...")
            page.click('input#btnGo')
            
            # Wait and see what happens
            time.sleep(5)
            
            # Check for any results
            logger.info("📊 Checking for results...")
            tables = page.query_selector_all('table')
            logger.info(f"Found {len(tables)} tables")
            
            for i, table in enumerate(tables):
                rows = table.query_selector_all('tr')
                if len(rows) > 1:
                    logger.info(f"Table {i+1} has {len(rows)} rows:")
                    for j, row in enumerate(rows[:5]):  # First 5 rows
                        cells = row.query_selector_all('td, th')
                        cell_texts = [cell.inner_text().strip() for cell in cells]
                        logger.info(f"  Row {j+1}: {cell_texts}")
            
            # Keep browser open for manual inspection
            logger.info("🔍 Browser will stay open for 30 seconds for manual inspection...")
            time.sleep(30)
            
        finally:
            browser.close()

if __name__ == "__main__":
    debug_agmarknet_form()
