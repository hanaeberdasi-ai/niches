"""
Shopify store discovery and verification
"""
import re
import json
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import ShopifyDataSource, DataSourceResult, DataSourceStatus
from config.settings import config
from utils.normalization import normalize_domain, normalize_url, normalize_price


class ShopifyVerifier(ShopifyDataSource):
    """Verifies and extracts data from Shopify stores"""
    
    name = "Shopify Verifier"
    
    # Shopify indicators in HTML/headers
    SHOPIFY_INDICATORS = [
        'cdn.shopify.com',
        'shopify-section',
        'Shopify.theme',
        'shopify-payment-button',
        '/cart.js',
        '/products.json',
        'shopify-buy',
        'myshopify.com',
        'shopifycloud',
        'checkout.shopify.com',
    ]
    
    def __init__(self):
        self._client = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.Client(
                timeout=config.request.timeout,
                headers=config.request.headers,
                follow_redirects=True,
            )
        return self._client
    
    def is_available(self) -> bool:
        return True
    
    def get_status(self) -> DataSourceStatus:
        return DataSourceStatus.AVAILABLE
    
    def _check_shopify_indicators(self, content: str, headers: dict) -> Dict[str, bool]:
        """Check for various Shopify indicators"""
        indicators = {}
        
        content_lower = content.lower() if content else ""
        
        for indicator in self.SHOPIFY_INDICATORS:
            indicators[indicator] = indicator.lower() in content_lower
        
        # Check headers
        if 'x-shopify-stage' in headers:
            indicators['x-shopify-stage'] = True
        
        if any(indicators.values()):
            indicators['is_shopify'] = True
        else:
            indicators['is_shopify'] = False
        
        return indicators
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    def verify_shopify(self, domain: str) -> bool:
        """Verify if a domain is a Shopify store"""
        domain = normalize_domain(domain)
        if not domain:
            return False
        
        # Check if it's a myshopify.com domain
        if '.myshopify.com' in domain:
            return True
        
        try:
            client = self._get_client()
            url = f"https://{domain}"
            
            # Try to access the store
            response = client.get(url)
            
            if response.status_code != 200:
                return False
            
            # Check indicators
            indicators = self._check_shopify_indicators(
                response.text,
                dict(response.headers)
            )
            
            if indicators.get('is_shopify'):
                return True
            
            # Try products.json endpoint
            try:
                products_url = f"https://{domain}/products.json?limit=1"
                products_response = client.get(products_url)
                if products_response.status_code == 200:
                    data = products_response.json()
                    if 'products' in data:
                        return True
            except Exception:
                pass
            
            return False
            
        except Exception:
            return False
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    def get_store_info(self, domain: str) -> DataSourceResult:
        """Get information about a Shopify store"""
        domain = normalize_domain(domain)
        if not domain:
            return DataSourceResult.error_result("Invalid domain", self.name)
        
        try:
            client = self._get_client()
            url = f"https://{domain}"
            
            response = client.get(url)
            if response.status_code != 200:
                return DataSourceResult.error_result(f"HTTP {response.status_code}", self.name)
            
            soup = BeautifulSoup(response.text, 'html5lib')
            
            # Extract store information
            store_info = {
                "domain": domain,
                "url": url,
                "shopify_verified": True,
                "name": self._extract_store_name(soup, domain),
                "title": soup.title.string if soup.title else None,
                "description": self._extract_meta_description(soup),
                "currency": self._extract_currency(response.text),
                "language": self._extract_language(soup),
                "social_links": self._extract_social_links(soup),
                "contact_email": self._extract_email(response.text),
                "theme": self._extract_theme(response.text),
                "detected_apps": self._extract_apps(response.text),
            }
            
            return DataSourceResult.success_result(store_info, self.name)
            
        except Exception as e:
            return DataSourceResult.error_result(str(e), self.name)
    
    def _extract_store_name(self, soup: BeautifulSoup, domain: str) -> str:
        """Extract store name from page"""
        # Try og:site_name
        og_site = soup.find('meta', property='og:site_name')
        if og_site and og_site.get('content'):
            return og_site['content']
        
        # Try title
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            # Remove common suffixes
            for suffix in [' – ', ' - ', ' | ', ' — ']:
                if suffix in title:
                    return title.split(suffix)[0].strip()
            return title
        
        # Use domain as fallback
        return domain.split('.')[0].title()
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract meta description"""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            return meta.get('content')
        
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content')
        
        return None
    
    def _extract_currency(self, content: str) -> Optional[str]:
        """Extract currency from page content"""
        patterns = [
            r'"currency"\s*:\s*"([A-Z]{3})"',
            r'Shopify\.currency\s*=\s*"([A-Z]{3})"',
            r'currency:\s*["\']([A-Z]{3})["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_language(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract language from page"""
        html_tag = soup.find('html')
        if html_tag:
            return html_tag.get('lang')
        return None
    
    def _extract_social_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links"""
        social_patterns = {
            'facebook': r'facebook\.com/[\w.-]+',
            'instagram': r'instagram\.com/[\w.-]+',
            'twitter': r'twitter\.com/[\w.-]+',
            'tiktok': r'tiktok\.com/@[\w.-]+',
            'youtube': r'youtube\.com/(c/|channel/|@)?[\w.-]+',
            'pinterest': r'pinterest\.com/[\w.-]+',
        }
        
        links = {}
        content = str(soup)
        
        for platform, pattern in social_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                links[platform] = f"https://{match.group(0)}"
        
        return links
    
    def _extract_email(self, content: str) -> Optional[str]:
        """Extract contact email from page"""
        # Common mailto patterns
        pattern = r'mailto:([\w.-]+@[\w.-]+\.[a-z]{2,})'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _extract_theme(self, content: str) -> Optional[str]:
        """Extract Shopify theme name"""
        patterns = [
            r'Shopify\.theme\s*=\s*{[^}]*"name"\s*:\s*"([^"]+)"',
            r'"theme_name"\s*:\s*"([^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_apps(self, content: str) -> List[str]:
        """Detect common Shopify apps"""
        app_indicators = {
            'Klaviyo': ['klaviyo'],
            'Loox': ['loox'],
            'Yotpo': ['yotpo'],
            'Judge.me': ['judge.me', 'judgeme'],
            'Stamped.io': ['stamped.io'],
            'Privy': ['privy'],
            'Smile.io': ['smile.io'],
            'Afterpay': ['afterpay'],
            'Klarna': ['klarna'],
            'ReCharge': ['recharge'],
            'Bold': ['bold-'],
            'Shogun': ['shogun'],
            'PageFly': ['pagefly'],
            'GemPages': ['gempages'],
            'Omnisend': ['omnisend'],
            'Mailchimp': ['mailchimp'],
            'Hotjar': ['hotjar'],
            'Google Analytics': ['google-analytics', 'gtag'],
            'Facebook Pixel': ['fbevents', 'facebook-pixel'],
            'TikTok Pixel': ['tiktok-analytics'],
        }
        
        detected = []
        content_lower = content.lower()
        
        for app_name, indicators in app_indicators.items():
            if any(ind in content_lower for ind in indicators):
                detected.append(app_name)
        
        return detected
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    def get_products(self, domain: str, limit: int = 50) -> DataSourceResult:
        """Get products from a Shopify store"""
        domain = normalize_domain(domain)
        if not domain:
            return DataSourceResult.error_result("Invalid domain", self.name)
        
        try:
            client = self._get_client()
            
            products = []
            page = 1
            
            while len(products) < limit:
                url = f"https://{domain}/products.json?limit=250&page={page}"
                response = client.get(url)
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                page_products = data.get('products', [])
                
                if not page_products:
                    break
                
                for p in page_products:
                    product = self._parse_product(p, domain)
                    products.append(product)
                    
                    if len(products) >= limit:
                        break
                
                page += 1
                if page > 10:  # Safety limit
                    break
            
            return DataSourceResult.success_result(products, self.name)
            
        except Exception as e:
            return DataSourceResult.error_result(str(e), self.name)
    
    def _parse_product(self, product_data: dict, domain: str) -> Dict[str, Any]:
        """Parse a product from Shopify JSON"""
        variants = product_data.get('variants', [])
        
        # Get price range
        prices = [float(v.get('price', 0)) for v in variants if v.get('price')]
        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None
        
        # Get compare at price
        compare_prices = [float(v.get('compare_at_price', 0)) for v in variants if v.get('compare_at_price')]
        compare_at_price = max(compare_prices) if compare_prices else None
        
        # Get image
        images = product_data.get('images', [])
        image_url = images[0].get('src') if images else None
        
        return {
            "id": product_data.get('id'),
            "title": product_data.get('title'),
            "handle": product_data.get('handle'),
            "url": f"https://{domain}/products/{product_data.get('handle')}",
            "description": product_data.get('body_html', ''),
            "vendor": product_data.get('vendor'),
            "product_type": product_data.get('product_type'),
            "tags": product_data.get('tags', []),
            "price": min_price,
            "price_max": max_price,
            "compare_at_price": compare_at_price,
            "image_url": image_url,
            "variants_count": len(variants),
            "available": any(v.get('available', False) for v in variants),
            "created_at": product_data.get('created_at'),
            "updated_at": product_data.get('updated_at'),
            "store_domain": domain,
        }
    
    def get_collections(self, domain: str) -> DataSourceResult:
        """Get collections from a Shopify store"""
        domain = normalize_domain(domain)
        if not domain:
            return DataSourceResult.error_result("Invalid domain", self.name)
        
        try:
            client = self._get_client()
            url = f"https://{domain}/collections.json"
            response = client.get(url)
            
            if response.status_code != 200:
                return DataSourceResult.error_result(f"HTTP {response.status_code}", self.name)
            
            data = response.json()
            collections = []
            
            for c in data.get('collections', []):
                collections.append({
                    "id": c.get('id'),
                    "title": c.get('title'),
                    "handle": c.get('handle'),
                    "url": f"https://{domain}/collections/{c.get('handle')}",
                    "description": c.get('body_html', ''),
                    "image_url": c.get('image', {}).get('src') if c.get('image') else None,
                })
            
            return DataSourceResult.success_result(collections, self.name)
            
        except Exception as e:
            return DataSourceResult.error_result(str(e), self.name)
    
    def close(self):
        """Close the HTTP client"""
        if self._client:
            self._client.close()
            self._client = None


# Global instance
shopify_verifier = ShopifyVerifier()
