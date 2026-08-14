"""
Validation utilities
"""
import re
from urllib.parse import urlparse
from typing import Optional, List


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid"""
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


def is_valid_domain(domain: str) -> bool:
    """Check if a domain is valid"""
    if not domain:
        return False
    
    # Basic domain pattern
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
    return bool(re.match(pattern, domain))


def is_shopify_domain(domain: str, indicators: List[str] = None) -> bool:
    """
    Check if domain appears to be a Shopify store.
    Uses various indicators to verify.
    """
    if not domain:
        return False
    
    # Known Shopify domain patterns
    shopify_patterns = [
        r'\.myshopify\.com$',
        r'shopify\.com',
    ]
    
    for pattern in shopify_patterns:
        if re.search(pattern, domain.lower()):
            return True
    
    # Check additional indicators if provided
    if indicators:
        shopify_indicators = [
            'cdn.shopify.com',
            'shopify-assets',
            'shopifycdn',
            '/cart.js',
            '/products.json',
            'Shopify.theme',
            'shopify-section',
        ]
        for indicator in shopify_indicators:
            if any(indicator.lower() in str(ind).lower() for ind in indicators):
                return True
    
    return False


def is_excluded_domain(domain: str) -> bool:
    """Check if domain should be excluded (not a Shopify store)"""
    excluded_patterns = [
        # Marketplaces
        r'amazon\.',
        r'ebay\.',
        r'etsy\.',
        r'aliexpress\.',
        r'alibaba\.',
        r'walmart\.',
        r'target\.',
        r'temu\.',
        r'wish\.',
        
        # Other platforms
        r'woocommerce\.',
        r'bigcommerce\.',
        r'squarespace\.',
        r'wix\.',
        r'weebly\.',
        r'magento\.',
        r'wordpress\.',
        
        # Social media
        r'facebook\.',
        r'instagram\.',
        r'twitter\.',
        r'tiktok\.',
        r'youtube\.',
        r'pinterest\.',
        r'linkedin\.',
        
        # Search engines
        r'google\.',
        r'bing\.',
        r'yahoo\.',
        
        # Other
        r'wikipedia\.',
        r'reddit\.',
        r'quora\.',
        r'medium\.',
        r'github\.',
    ]
    
    domain_lower = domain.lower()
    for pattern in excluded_patterns:
        if re.search(pattern, domain_lower):
            return True
    
    return False


def validate_keyword(keyword: str) -> tuple[bool, Optional[str]]:
    """
    Validate a search keyword.
    Returns (is_valid, error_message)
    """
    if not keyword:
        return True, None  # Empty keyword is valid (auto-discovery mode)
    
    keyword = keyword.strip()
    
    if len(keyword) < 2:
        return False, "Keyword must be at least 2 characters"
    
    if len(keyword) > 100:
        return False, "Keyword must be less than 100 characters"
    
    # Check for potentially harmful characters
    if re.search(r'[<>{}|\[\]\\]', keyword):
        return False, "Keyword contains invalid characters"
    
    return True, None


def validate_price_range(min_price: Optional[float], max_price: Optional[float]) -> tuple[bool, Optional[str]]:
    """Validate price range"""
    if min_price is not None and min_price < 0:
        return False, "Minimum price cannot be negative"
    
    if max_price is not None and max_price < 0:
        return False, "Maximum price cannot be negative"
    
    if min_price is not None and max_price is not None and min_price > max_price:
        return False, "Minimum price cannot be greater than maximum price"
    
    return True, None


def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>{}|\[\]\\`]', '', text)
    
    # Remove multiple spaces
    text = ' '.join(text.split())
    
    return text.strip()
