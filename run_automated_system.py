#!/usr/bin/env python3
"""
Complete automation system for SabjiGPT
Runs both the scheduler and MCP server simultaneously

Usage:
    python run_automated_system.py                 # Run both scheduler and MCP server
    python run_automated_system.py --mcp-only      # Run only MCP server
    python run_automated_system.py --scheduler-only # Run only scheduler
    python run_automated_system.py --test-scrape   # Test scraping once
"""

import asyncio
import threading
import time
import logging
import sys
import os
import signal
from typing import Optional
from dotenv import load_dotenv

# Load environment before importing our modules
load_dotenv()

# Import our components
from src.scheduler.automated_scraper import AutomatedScraper
import uvicorn

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SabjiGPTSystem:
    """
    Main system coordinator that runs both scheduler and MCP server
    """
    
    def __init__(self):
        self.scheduler_thread: Optional[threading.Thread] = None
        self.mcp_server: Optional[uvicorn.Server] = None
        self.running = False
        
        # Configuration
        self.mcp_port = int(os.getenv('MCP_PORT', 8087))
        self.auth_token = os.getenv('AUTH_TOKEN', 'sabji_gpt_secret_2025')
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def run_scheduler_thread(self):
        """Run the automated scraper in a separate thread"""
        try:
            logger.info("🕒 Starting automated scheduler thread...")
            scraper = AutomatedScraper()
            scraper.run_scheduler()
        except Exception as e:
            logger.error(f"❌ Scheduler thread error: {e}")
    
    def run_mcp_server(self):
        """Run the MCP server"""
        logger.info(f"🚀 Starting MCP server on port {self.mcp_port}...")
        
        config = uvicorn.Config(
            "src.mcp.sabji_mcp_server:app",
            host="0.0.0.0",
            port=self.mcp_port,
            reload=False,  # Don't reload when running with threads
            log_level=log_level.lower(),
            access_log=False  # Reduce log noise
        )
        
        server = uvicorn.Server(config)
        server.run()
    
    def run_scheduler_only(self):
        """Run only the scheduler"""
        print("⏰ Starting SCHEDULER ONLY mode")
        print("=" * 50)
        print("📅 Automated Scraping: 9:00 AM & 6:00 PM daily")
        print("🔄 Press Ctrl+C to stop")
        print("=" * 50)
        
        self.running = True
        self.run_scheduler_thread()
    
    def run_mcp_only(self):
        """Run only the MCP server"""
        print("🔌 Starting MCP SERVER ONLY mode")
        print("=" * 50)
        print(f"🌐 MCP Server: http://0.0.0.0:{self.mcp_port}")
        print(f"🔑 Auth Token: {self.auth_token}")
        print("🔗 Connect with: /mcp connect https://your-domain.ngrok.app/mcp {token}")
        print("=" * 50)
        
        self.running = True
        self.run_mcp_server()
    
    def run_both(self):
        """Run both scheduler and MCP server"""
        print("🌟 Starting COMPLETE SYSTEM")
        print("=" * 60)
        print("📅 Automated Scraping: 9:00 AM & 6:00 PM daily")
        print(f"🔌 MCP Server: http://0.0.0.0:{self.mcp_port}")
        print(f"🔑 Auth Token: {self.auth_token}")
        print("🔗 Connect with: /mcp connect https://your-domain.ngrok.app/mcp {token}")
        print("🔄 Press Ctrl+C to stop both services")
        print("=" * 60)
        
        self.running = True
        
        # Start scheduler in background thread
        self.scheduler_thread = threading.Thread(
            target=self.run_scheduler_thread, 
            daemon=True,
            name="SchedulerThread"
        )
        self.scheduler_thread.start()
        logger.info("✅ Scheduler thread started")
        
        # Small delay to let scheduler initialize
        time.sleep(2)
        
        # Run MCP server in main thread (blocking)
        try:
            self.run_mcp_server()
        except KeyboardInterrupt:
            logger.info("👋 Shutting down...")
            self.shutdown()
    
    def test_scrape(self):
        """Run a test scrape to verify everything works"""
        print("🧪 TESTING SCRAPER")
        print("=" * 40)
        
        scraper = AutomatedScraper()
        
        # Test with a known working combination
        print("Testing: Onion in Pune (known to have data)")
        result = scraper.scrape_single_target("pune", "onion")
        
        if result:
            print("✅ Test SUCCESSFUL!")
            print(f"   Price: ₹{result['price_per_kg']}/kg")
            print(f"   Market: {result.get('market', 'N/A')}")
            print(f"   Source: {result['source']}")
        else:
            print("❌ Test FAILED - No data found")
            print("This might be normal if markets are closed")
        
        print("\n🏥 Health Check:")
        try:
            from src.database.price_db import PriceDatabase
            db = PriceDatabase()
            stats = db.get_db_stats()
            print(f"   Database: ✅ {stats.get('total_records', 0)} records")
        except Exception as e:
            print(f"   Database: ❌ Error: {e}")
    
    def shutdown(self):
        """Graceful shutdown"""
        if self.running:
            logger.info("🛑 Shutting down SabjiGPT system...")
            self.running = False
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                logger.info("⏰ Stopping scheduler...")
                # scheduler thread will stop when main process exits
            
            logger.info("👋 Shutdown complete")

def print_usage():
    """Print usage information"""
    print("🌟 SabjiGPT Automated System")
    print("=" * 50)
    print("Usage:")
    print("  python run_automated_system.py                 # Run both scheduler + MCP server")
    print("  python run_automated_system.py --mcp-only      # Run only MCP server")
    print("  python run_automated_system.py --scheduler-only # Run only scheduler")
    print("  python run_automated_system.py --test-scrape   # Test scraping once")
    print("  python run_automated_system.py --help          # Show this help")
    print("")
    print("Environment:")
    auth_token = os.getenv('AUTH_TOKEN', 'sabji_gpt_secret_2025')
    mcp_port = os.getenv('MCP_PORT', '8087')
    print(f"  🔑 Auth Token: {auth_token}")
    print(f"  🔌 MCP Port: {mcp_port}")
    print("=" * 50)

def main():
    """Main function"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h']:
            print_usage()
            return
        elif arg == '--test-scrape':
            system = SabjiGPTSystem()
            system.test_scrape()
            return
        elif arg == '--mcp-only':
            system = SabjiGPTSystem()
            system.run_mcp_only()
            return
        elif arg == '--scheduler-only':
            system = SabjiGPTSystem()
            system.run_scheduler_only()
            return
        else:
            print(f"❌ Unknown argument: {arg}")
            print_usage()
            return
    
    # Default: run both
    system = SabjiGPTSystem()
    system.run_both()

if __name__ == "__main__":
    main()
