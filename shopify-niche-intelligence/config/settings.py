"""
Configuration settings for Shopify Niche Intelligence Tool
"""
import os
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path

# Try to load .env file if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class APIConfig:
    """API configuration settings"""
    serp_api_key: Optional[str] = field(default_factory=lambda: os.getenv("SERP_API_KEY"))
    google_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    google_cse_id: Optional[str] = field(default_factory=lambda: os.getenv("GOOGLE_CSE_ID"))
    
    @property
    def has_serp_api(self) -> bool:
        return bool(self.serp_api_key)
    
    @property
    def has_google_api(self) -> bool:
        return bool(self.google_api_key and self.google_cse_id)


@dataclass
class RequestConfig:
    """HTTP request configuration"""
    timeout: int = field(default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT", "30")))
    max_concurrent: int = field(default_factory=lambda: int(os.getenv("MAX_CONCURRENT_REQUESTS", "5")))
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # User agent for requests
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    @property
    def headers(self) -> dict:
        return {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }


@dataclass
class CacheConfig:
    """Cache configuration"""
    ttl: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL", "3600")))
    max_size: int = 1000


@dataclass
class AppConfig:
    """Main application configuration"""
    app_name: str = "Shopify Niche Intelligence"
    version: str = "1.0.0"
    
    api: APIConfig = field(default_factory=APIConfig)
    request: RequestConfig = field(default_factory=RequestConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    
    # Scoring weights
    scoring_weights: dict = field(default_factory=lambda: {
        "demand": 0.20,
        "trend": 0.15,
        "competition": 0.15,
        "product_opportunity": 0.15,
        "shopify_opportunity": 0.10,
        "gmc_suitability": 0.10,
        "commercial_intent": 0.10,
        "saturation": 0.05,
    })


# Global configuration instance
config = AppConfig()


# Category hierarchy
CATEGORIES = {
    "Beauty & Personal Care": {
        "Skincare": ["Face Care", "Body Care", "Anti-Aging", "Acne Treatment", "Sun Care"],
        "Makeup": ["Face Makeup", "Eye Makeup", "Lip Products", "Makeup Tools"],
        "Hair Care": ["Shampoo & Conditioner", "Hair Styling", "Hair Treatment", "Hair Tools"],
        "Beauty Devices": ["Facial Devices", "Hair Removal", "LED Therapy", "Microcurrent"],
        "Nail Care": ["Nail Polish", "Nail Tools", "Nail Art", "Nail Devices"],
        "Fragrance": ["Perfume", "Body Mist", "Essential Oils"],
    },
    "Health & Wellness": {
        "Supplements": ["Vitamins", "Protein", "Herbal", "Sports Nutrition"],
        "Fitness Equipment": ["Home Gym", "Yoga", "Resistance Training", "Cardio"],
        "Wellness Devices": ["Massage", "Recovery", "Sleep", "Monitoring"],
        "Personal Care": ["Oral Care", "Body Care", "Hygiene"],
    },
    "Home & Garden": {
        "Kitchen": ["Cookware", "Kitchen Gadgets", "Storage", "Small Appliances"],
        "Home Decor": ["Wall Art", "Lighting", "Textiles", "Decorative Items"],
        "Furniture": ["Living Room", "Bedroom", "Office", "Outdoor"],
        "Garden": ["Plants", "Garden Tools", "Outdoor Decor", "Planters"],
        "Cleaning": ["Cleaning Tools", "Organizers", "Laundry"],
        "Smart Home": ["Smart Lighting", "Security", "Climate", "Automation"],
    },
    "Electronics & Tech": {
        "Mobile Accessories": ["Phone Cases", "Chargers", "Screen Protectors", "Mounts"],
        "Computer Accessories": ["Keyboards", "Mice", "Monitors", "Storage"],
        "Audio": ["Headphones", "Speakers", "Microphones", "Earbuds"],
        "Wearables": ["Smartwatches", "Fitness Trackers", "Smart Glasses"],
        "Gaming": ["Controllers", "Gaming Accessories", "VR", "Gaming Furniture"],
        "Camera & Photo": ["Camera Accessories", "Lighting", "Tripods", "Storage"],
    },
    "Fashion & Accessories": {
        "Clothing": ["Tops", "Bottoms", "Dresses", "Outerwear", "Activewear"],
        "Shoes": ["Sneakers", "Boots", "Sandals", "Athletic"],
        "Jewelry": ["Necklaces", "Earrings", "Rings", "Bracelets"],
        "Watches": ["Smart Watches", "Fashion Watches", "Watch Accessories"],
        "Bags": ["Handbags", "Backpacks", "Travel Bags", "Wallets"],
        "Accessories": ["Sunglasses", "Hats", "Scarves", "Belts"],
    },
    "Sports & Outdoors": {
        "Outdoor Recreation": ["Camping", "Hiking", "Fishing", "Hunting"],
        "Sports Equipment": ["Team Sports", "Individual Sports", "Water Sports"],
        "Fitness": ["Gym Equipment", "Yoga", "Running", "Training"],
        "Cycling": ["Bikes", "Cycling Gear", "Accessories"],
    },
    "Pets": {
        "Dogs": ["Dog Food", "Dog Toys", "Dog Beds", "Dog Accessories"],
        "Cats": ["Cat Food", "Cat Toys", "Cat Furniture", "Cat Accessories"],
        "Pet Tech": ["Pet Cameras", "GPS Trackers", "Feeders", "Health Monitors"],
        "Pet Care": ["Grooming", "Health", "Training"],
    },
    "Baby & Kids": {
        "Baby Care": ["Feeding", "Diapering", "Bath", "Safety"],
        "Baby Gear": ["Strollers", "Car Seats", "Carriers", "Nursery"],
        "Kids Toys": ["Educational", "Outdoor", "Creative", "Games"],
        "Kids Fashion": ["Clothing", "Shoes", "Accessories"],
    },
    "Automotive": {
        "Car Accessories": ["Interior", "Exterior", "Electronics", "Organizers"],
        "Car Care": ["Cleaning", "Maintenance", "Protection"],
        "Motorcycle": ["Gear", "Parts", "Accessories"],
    },
    "Office & Business": {
        "Office Supplies": ["Desk Accessories", "Organization", "Writing"],
        "Office Furniture": ["Desks", "Chairs", "Storage"],
        "Office Electronics": ["Printers", "Accessories", "Networking"],
    },
    "Arts & Crafts": {
        "Art Supplies": ["Painting", "Drawing", "Crafting"],
        "DIY & Hobbies": ["Sewing", "Knitting", "Jewelry Making"],
        "Party Supplies": ["Decorations", "Tableware", "Party Favors"],
    },
    "Food & Beverage": {
        "Specialty Foods": ["Organic", "Gourmet", "Diet-Specific"],
        "Beverages": ["Coffee", "Tea", "Supplements"],
        "Kitchen Equipment": ["Coffee Makers", "Blenders", "Food Prep"],
    },
}


# GMC Policy categories
GMC_RESTRICTED_CATEGORIES = [
    "weapons", "firearms", "ammunition", "explosives",
    "drugs", "controlled substances", "tobacco", "vaping",
    "adult content", "gambling", "counterfeit",
    "dangerous products", "recalled products",
]

GMC_HIGH_RISK_KEYWORDS = [
    "cure", "miracle", "weight loss", "before after",
    "guaranteed results", "FDA approved", "medical grade",
    "prescription", "steroid", "CBD", "THC", "cannabis",
]

GMC_POTENTIALLY_SUITABLE_NOTES = [
    "Product appears to be in a generally acceptable category",
    "Requires accurate product data and clear policies",
    "May need additional verification for certain claims",
    "Review Google Merchant Center policies before listing",
]
