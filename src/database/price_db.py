"""
Simple SQLite database for storing vegetable price data
Developer approach: SQLite first, PostgreSQL later if needed
"""

import sqlite3
from datetime import datetime, date
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PriceDatabase:
    """
    Simple database for storing and retrieving vegetable prices
    """
    
    def __init__(self, db_path="mandi_prices.db"):
        """
        Initialize database with tables
        """
        self.db_path = db_path
        self.conn = None
        self.setup_database()
        
    def setup_database(self):
        """
        Create database tables if they don't exist
        """
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Create prices table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    vegetable TEXT NOT NULL,
                    price REAL NOT NULL,
                    price_per TEXT DEFAULT 'kg',
                    min_price REAL,
                    max_price REAL,
                    market TEXT,
                    currency TEXT DEFAULT 'INR',
                    data_date DATE,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT DEFAULT 'agmarknet.gov.in',
                    raw_data TEXT,
                    UNIQUE(city, vegetable, market, data_date) ON CONFLICT REPLACE
                )
            """)
            
            # Create index for fast lookups
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_city_veg_date 
                ON prices(city, vegetable, scraped_at DESC)
            """)
            
            # Create index for market lookups
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_market_date
                ON prices(market, data_date DESC)
            """)
            
            self.conn.commit()
            logger.info(f"✅ Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise
    
    def insert_price(self, data: Dict) -> bool:
        """
        Insert price data into database
        
        Args:
            data: Dictionary with price information
            
        Returns:
            bool: Success status
        """
        try:
            # Prepare data for insertion
            insert_data = {
                'city': data.get('city', '').lower(),
                'vegetable': data.get('vegetable', '').lower(),
                'price': float(data.get('price', 0)),
                'price_per': data.get('price_per', 'kg'),
                'min_price': data.get('min_price'),
                'max_price': data.get('max_price'),
                'market': data.get('market', ''),
                'currency': data.get('currency', 'INR'),
                'data_date': data.get('data_date', date.today()),
                'source': data.get('source', 'agmarknet.gov.in'),
                'raw_data': json.dumps(data.get('raw_data', {}))
            }
            
            # Convert price_per_kg to price if needed
            if 'price_per_kg' in data and data.get('price_per') == 'quintal':
                insert_data['price'] = data['price_per_kg']
                insert_data['price_per'] = 'kg'
            
            self.conn.execute("""
                INSERT INTO prices 
                (city, vegetable, price, price_per, min_price, max_price, 
                 market, currency, data_date, source, raw_data)
                VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insert_data['city'],
                insert_data['vegetable'],
                insert_data['price'],
                insert_data['price_per'],
                insert_data['min_price'],
                insert_data['max_price'],
                insert_data['market'],
                insert_data['currency'],
                insert_data['data_date'],
                insert_data['source'],
                insert_data['raw_data']
            ))
            
            self.conn.commit()
            logger.info(f"💾 Saved: {insert_data['city']} {insert_data['vegetable']} ₹{insert_data['price']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Insert failed: {e}")
            return False
    
    def get_latest_price(self, city: str, vegetable: str) -> Optional[Dict]:
        """
        Get the most recent price for a vegetable in a city
        """
        try:
            cursor = self.conn.execute("""
                SELECT * FROM prices 
                WHERE city = ? AND vegetable = ?
                ORDER BY scraped_at DESC 
                LIMIT 1
            """, (city.lower(), vegetable.lower()))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return None
    
    def get_price_history(self, city: str, vegetable: str, days: int = 7) -> List[Dict]:
        """
        Get price history for the last N days
        """
        try:
            cursor = self.conn.execute("""
                SELECT * FROM prices 
                WHERE city = ? AND vegetable = ?
                AND scraped_at >= datetime('now', '-{} days')
                ORDER BY scraped_at DESC
            """.format(days), (city.lower(), vegetable.lower()))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"❌ History query failed: {e}")
            return []
    
    def get_city_prices(self, city: str) -> List[Dict]:
        """
        Get latest prices for all vegetables in a city
        """
        try:
            cursor = self.conn.execute("""
                SELECT DISTINCT 
                    vegetable,
                    price,
                    price_per,
                    market,
                    scraped_at
                FROM prices p1
                WHERE city = ? 
                AND scraped_at = (
                    SELECT MAX(scraped_at) 
                    FROM prices p2 
                    WHERE p2.city = p1.city 
                    AND p2.vegetable = p1.vegetable
                )
                ORDER BY vegetable
            """, (city.lower(),))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"❌ City prices query failed: {e}")
            return []
    
    def get_vegetable_prices_across_cities(self, vegetable: str) -> List[Dict]:
        """
        Get latest prices for a vegetable across all cities
        """
        try:
            cursor = self.conn.execute("""
                SELECT DISTINCT 
                    city,
                    price,
                    price_per,
                    market,
                    scraped_at
                FROM prices p1
                WHERE vegetable = ? 
                AND scraped_at = (
                    SELECT MAX(scraped_at) 
                    FROM prices p2 
                    WHERE p2.city = p1.city 
                    AND p2.vegetable = p1.vegetable
                )
                ORDER BY city
            """, (vegetable.lower(),))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"❌ Vegetable prices query failed: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """
        Get database statistics
        """
        try:
            cursor = self.conn.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT city) as unique_cities,
                    COUNT(DISTINCT vegetable) as unique_vegetables,
                    MAX(scraped_at) as latest_update
                FROM prices
            """)
            
            row = cursor.fetchone()
            return dict(row) if row else {}
            
        except Exception as e:
            logger.error(f"❌ Stats query failed: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30):
        """
        Clean up data older than N days to keep database size manageable
        """
        try:
            cursor = self.conn.execute("""
                DELETE FROM prices 
                WHERE scraped_at < datetime('now', '-{} days')
            """.format(days))
            
            deleted_count = cursor.rowcount
            self.conn.commit()
            
            logger.info(f"🗑️ Cleaned up {deleted_count} old records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return 0
    
    def close(self):
        """
        Close database connection
        """
        if self.conn:
            self.conn.close()
            self.conn = None

def test_database():
    """
    Test database functionality with sample data
    """
    print("🧪 Testing PriceDatabase...")
    
    # Use temporary database for testing
    db = PriceDatabase("test_prices.db")
    
    # Test data
    sample_data = {
        "city": "Mumbai",
        "vegetable": "tomato",
        "price": 25.50,
        "price_per": "kg",
        "min_price": 20.0,
        "max_price": 30.0,
        "market": "Mumbai Central Market",
        "currency": "INR",
        "data_date": date.today(),
        "source": "agmarknet.gov.in",
        "raw_data": {"test": "data"}
    }
    
    # Test insert
    success = db.insert_price(sample_data)
    print(f"✅ Insert: {success}")
    
    # Test retrieval
    latest = db.get_latest_price("mumbai", "tomato")
    print(f"✅ Latest price: {latest}")
    
    # Test city prices
    city_prices = db.get_city_prices("mumbai")
    print(f"✅ City prices: {len(city_prices)} items")
    
    # Test stats
    stats = db.get_stats()
    print(f"✅ Stats: {stats}")
    
    # Cleanup
    db.close()
    Path("test_prices.db").unlink()  # Delete test file
    
    print("✅ Database tests completed!")

if __name__ == "__main__":
    test_database()
