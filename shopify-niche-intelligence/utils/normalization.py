"""
Data normalization utilities
"""
import re
from urllib.parse import urlparse, urljoin
from typing import Optional, List, Dict, Any
import hashlib


def normalize_domain(url: str) -> str:
    """
    Normalize a domain/URL to a consistent format.
    
    Examples:
        https://www.example.com -> example.com
        http://example.com/page -> example.com
        www.example.com -> example.com
    """
    if not url:
        return ""
    
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Remove port
        if ':' in domain:
            domain = domain.split(':')[0]
        
        return domain
    except Exception:
        return url.lower().strip()


def normalize_url(url: str) -> str:
    """Normalize a URL to a consistent format"""
    if not url:
        return ""
    
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        # Reconstruct with https and normalized domain
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        
        path = parsed.path.rstrip('/')
        return f"https://{domain}{path}"
    except Exception:
        return url


def normalize_price(price_str: str) -> Optional[float]:
    """
    Extract numeric price from a price string.
    
    Examples:
        "$29.99" -> 29.99
        "€ 15,50" -> 15.50
        "29.99 USD" -> 29.99
    """
    if not price_str:
        return None
    
    # Remove currency symbols and whitespace
    price_str = str(price_str)
    
    # Extract numbers with decimal
    match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
    if match:
        try:
            return float(match.group().replace(',', ''))
        except ValueError:
            return None
    return None


def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters
    text = re.sub(r'[^\w\s-]', '', text)
    
    return text.strip()


def generate_id(*args) -> str:
    """Generate a unique ID from arguments"""
    combined = '|'.join(str(arg) for arg in args)
    return hashlib.md5(combined.encode()).hexdigest()[:12]


def deduplicate_stores(stores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate stores based on normalized domain"""
    seen_domains = set()
    unique_stores = []
    
    for store in stores:
        domain = normalize_domain(store.get('domain', '') or store.get('url', ''))
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            unique_stores.append(store)
    
    return unique_stores


def deduplicate_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate products based on URL or title+store combination"""
    seen = set()
    unique_products = []
    
    for product in products:
        url = normalize_url(product.get('url', ''))
        if url:
            key = url
        else:
            # Use title + store as fallback
            title = normalize_text(product.get('title', ''))
            store = normalize_domain(product.get('store', ''))
            key = f"{title}|{store}"
        
        if key and key not in seen:
            seen.add(key)
            unique_products.append(product)
    
    return unique_products


def extract_currency(text: str) -> Optional[str]:
    """Extract currency code from text"""
    currency_map = {
        '$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY',
        '₹': 'INR', 'A$': 'AUD', 'C$': 'CAD', 'CHF': 'CHF',
        'kr': 'SEK', 'R$': 'BRL', '₽': 'RUB', '₩': 'KRW',
    }
    
    for symbol, code in currency_map.items():
        if symbol in text:
            return code
    
    # Check for currency codes
    codes = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'INR', 'CNY']
    for code in codes:
        if code in text.upper():
            return code
    
    return None


def clean_html(html: str) -> str:
    """Remove HTML tags from string"""
    if not html:
        return ""
    return re.sub(r'<[^>]+>', '', html).strip()


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max length with ellipsis"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3].rsplit(' ', 1)[0] + '...'
