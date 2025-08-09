"""
Developer exploration script - understand the site before coding
This is the FIRST script to run - helps us understand Agmarknet structure
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json

def explore_agmarknet():
    """
    My first code - just understand what we're dealing with
    """
    print("🔍 Exploring Agmarknet.gov.in...")
    
    # Step 1: Hit the main page
    base_url = "https://agmarknet.gov.in"
    
    # Try different URL patterns that might exist
    test_urls = [
        f"{base_url}",
        f"{base_url}/SearchCmmMkt.aspx",
        f"{base_url}/PriceTrends/SA_Pri_Month.aspx", 
        f"{base_url}/wcm/Portal/Home.aspx",
        f"{base_url}/SearchCmmMkt.aspx?Tx_Commodity=23&Tx_State=MH&Tx_District=11&Tx_Market=56",
        f"{base_url}/PriceAndArrivalReport.aspx"
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    for i, url in enumerate(test_urls):
        try:
            print(f"\n📋 Testing URL {i+1}: {url}")
            resp = session.get(url, timeout=15)
            print(f"✅ Status: {resp.status_code}")
            print(f"📄 Content Length: {len(resp.text)} chars")
            
            # Save HTML for manual inspection
            filename = f"sample_{i+1}_{url.split('/')[-1].replace('?', '_').replace('=', '_')}.html"
            with open(filename, "w", encoding='utf-8') as f:
                f.write(resp.text)
            print(f"💾 Saved to: {filename}")
            
            # Quick analysis
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Look for forms (price search forms)
            forms = soup.find_all('form')
            print(f"📝 Found {len(forms)} forms")
            
            # Look for dropdowns (commodity, state, district selectors)
            selects = soup.find_all('select')
            if selects:
                print(f"📊 Found {len(selects)} dropdown menus:")
                for select in selects[:3]:  # Show first 3
                    select_id = select.get('id', 'no-id')
                    options = select.find_all('option')
                    print(f"  - {select_id}: {len(options)} options")
                    
                    # Show some option values for commodity dropdown
                    if 'commodity' in select_id.lower() or 'cmm' in select_id.lower():
                        print(f"    Sample options: {[opt.text.strip() for opt in options[:5]]}")
            
            # Look for price tables
            tables = soup.find_all('table')
            print(f"📊 Found {len(tables)} tables")
            
            # Look for JavaScript that might handle AJAX
            scripts = soup.find_all('script')
            js_with_ajax = [s for s in scripts if s.string and ('ajax' in s.string.lower() or 'xhr' in s.string.lower())]
            if js_with_ajax:
                print(f"⚡ Found {len(js_with_ajax)} scripts with AJAX")
            
            print("-" * 50)
            time.sleep(1)  # Be nice to the server
                
        except Exception as e:
            print(f"❌ Error with {url}: {e}")
            continue
    
    print("\n🎯 Next Steps:")
    print("1. Check the saved HTML files to understand form structure")
    print("2. Look for commodity/state/district dropdown IDs")
    print("3. Identify the search button and result table structure")
    print("4. Note any VIEWSTATE or other ASP.NET specific fields")

def analyze_search_form():
    """
    Deeper analysis of the search form structure
    """
    print("\n🔍 Analyzing search form structure...")
    
    # This will be based on what we find in the HTML files
    # For now, let's make educated guesses about common patterns
    common_form_patterns = {
        "commodity_dropdown": ["ddlCommodity", "cmbCommodity", "selectCommodity"],
        "state_dropdown": ["ddlState", "cmbState", "selectState"], 
        "district_dropdown": ["ddlDistrict", "cmbDistrict", "selectDistrict"],
        "market_dropdown": ["ddlMarket", "cmbMarket", "selectMarket"],
        "submit_button": ["btnSubmit", "btnSearch", "btnGo", "btnFind"]
    }
    
    print("🎯 Looking for these common patterns:")
    for element_type, possible_ids in common_form_patterns.items():
        print(f"  {element_type}: {possible_ids}")

def test_basic_request():
    """
    Test if we can make a basic request to get commodity list
    """
    print("\n🧪 Testing basic request...")
    
    try:
        # Try to get the main search page
        url = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        resp = session.get(url, timeout=10)
        
        if resp.status_code == 200:
            print("✅ Successfully connected to Agmarknet!")
            print(f"📄 Response size: {len(resp.text)} characters")
            
            # Check if it's an ASP.NET page (common for government sites)
            if 'viewstate' in resp.text.lower():
                print("🔍 Detected ASP.NET application (ViewState found)")
                print("   This means we'll need to handle ViewState in form submissions")
            
            return True
        else:
            print(f"❌ Unexpected status code: {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Agmarknet exploration...")
    print("=" * 60)
    
    # Step 1: Test basic connectivity
    if test_basic_request():
        # Step 2: Explore different endpoints
        explore_agmarknet()
        
        # Step 3: Analyze form patterns
        analyze_search_form()
        
        print("\n✅ Exploration complete!")
        print("📁 Check the generated HTML files for detailed structure analysis")
        print("📋 Next: Build the minimal scraper based on findings")
    else:
        print("❌ Could not connect to Agmarknet. Check internet connection.")
