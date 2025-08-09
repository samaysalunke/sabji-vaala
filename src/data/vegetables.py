"""
Vegetable name normalization - built incrementally as we test
This is critical for mapping user input to Agmarknet vegetable names
"""

VEGETABLE_MASTER = {
    # Start with top 3, expand as scraper works
    "tomato": {
        "agmarknet_name": "Tomato",  # Exact name on website
        "hindi": "टमाटर",
        "variants": ["tamatar", "tomatoes", "tamator", "टमाटर"],
        "category": "daily_essential"
    },
    "potato": {
        "agmarknet_name": "Potato",
        "hindi": "आलू", 
        "variants": ["aloo", "alu", "potatoes", "batata", "आलू"],
        "category": "daily_essential"
    },
    "onion": {
        "agmarknet_name": "Onion",
        "hindi": "प्याज",
        "variants": ["pyaz", "pyaaz", "kanda", "onions", "प्याज"],
        "category": "daily_essential"
    },
    # Additional vegetables - will add after testing core ones
    "cauliflower": {
        "agmarknet_name": "Cauliflower",
        "hindi": "फूलगोभी",
        "variants": ["phool gobhi", "gobi", "फूलगोभी"],
        "category": "regular"
    },
    "cabbage": {
        "agmarknet_name": "Cabbage",
        "hindi": "पत्तागोभी", 
        "variants": ["patta gobhi", "bandh gobhi", "पत्तागोभी"],
        "category": "regular"
    },
    "carrot": {
        "agmarknet_name": "Carrot",
        "hindi": "गाजर",
        "variants": ["gajar", "गाजर"],
        "category": "regular"
    },
    "green_peas": {
        "agmarknet_name": "Green Peas",
        "hindi": "हरी मटर",
        "variants": ["matar", "peas", "hari matar", "हरी मटर"],
        "category": "seasonal"
    },
    "spinach": {
        "agmarknet_name": "Spinach",
        "hindi": "पालक",
        "variants": ["palak", "पालक"],
        "category": "leafy"
    },
    "okra": {
        "agmarknet_name": "Okra (Bhindi)",
        "hindi": "भिंडी",
        "variants": ["bhindi", "lady finger", "भिंडी"],
        "category": "regular"
    },
    "brinjal": {
        "agmarknet_name": "Brinjal",
        "hindi": "बैंगन",
        "variants": ["baingan", "eggplant", "aubergine", "बैंगन"],
        "category": "regular"
    }
}

# City mappings for Agmarknet (state_code, district_name format)
CITY_MAPPINGS = {
    "mumbai": ("MH", "Mumbai"),      # Maharashtra
    "delhi": ("DL", "Delhi"),        # NCT of Delhi  
    "bengaluru": ("KK", "Bangalore"), # Karnataka
    "bangalore": ("KK", "Bangalore"), # Alternative spelling
    "hyderabad": ("TL", "Hyderabad"), # Telangana
    "chennai": ("TN", "Chennai"),     # Tamil Nadu
    "kolkata": ("WB", "Kolkata"),     # West Bengal
    "pune": ("MH", "Pune"),          # Maharashtra
    "ahmedabad": ("GJ", "Ahmedabad"), # Gujarat
    "jaipur": ("RJ", "Jaipur"),      # Rajasthan
    "lucknow": ("UP", "Lucknow")     # Uttar Pradesh
}

def normalize_vegetable_name(input_text: str) -> str:
    """
    First version - exact matching only
    TODO: Add fuzzy matching later
    """
    if not input_text:
        return None
        
    input_lower = input_text.lower().strip()
    
    # Check direct matches
    if input_lower in VEGETABLE_MASTER:
        return input_lower
    
    # Check variants
    for veg_key, veg_data in VEGETABLE_MASTER.items():
        if input_lower in [v.lower() for v in veg_data["variants"]]:
            return veg_key
            
    return None  # Not found

def normalize_city_name(input_text: str) -> tuple:
    """
    Normalize city name to (state, district) format for Agmarknet
    """
    if not input_text:
        return None
        
    input_lower = input_text.lower().strip()
    
    if input_lower in CITY_MAPPINGS:
        return CITY_MAPPINGS[input_lower]
    
    return None

def get_agmarknet_vegetable_name(normalized_name: str) -> str:
    """
    Get the exact vegetable name as it appears on Agmarknet
    """
    if normalized_name in VEGETABLE_MASTER:
        return VEGETABLE_MASTER[normalized_name]["agmarknet_name"]
    return None

def list_supported_vegetables():
    """Helper for API documentation"""
    return list(VEGETABLE_MASTER.keys())

def list_supported_cities():
    """Helper for API documentation"""
    return list(CITY_MAPPINGS.keys())
