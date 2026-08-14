"""
Search data sources for discovering Shopify stores and products
"""
import re
from typing import List, Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import SearchDataSource, DataSourceResult, DataSourceStatus
from config.settings import config
from utils.normalization import normalize_domain
from utils.validators import is_excluded_domain


class DuckDuckGoSearch(SearchDataSource):
    """Search using DuckDuckGo HTML (no API key required)"""
    
    name = "DuckDuckGo Search"
    
    def __init__(self):
        self._client = None
    
    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=config.request.timeout,
                headers={
                    **config.request.headers,
                    "Accept": "text/html",
                },
                follow_redirects=True,
            )
        return self._client
    
    def is_available(self) -> bool:
        return True
    
    def get_status(self) -> DataSourceStatus:
        return DataSourceStatus.AVAILABLE
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=3))
    def search(self, query: str, num_results: int = 20, **kwargs) -> DataSourceResult:
        """Search DuckDuckGo for results"""
        try:
            client = self._get_client()
            
            # Use DuckDuckGo HTML search
            url = "https://html.duckduckgo.com/html/"
            data = {"q": query}
            
            response = client.post(url, data=data)
            
            if response.status_code != 200:
                return DataSourceResult.error_result(f"HTTP {response.status_code}", self.name)
            
            # Parse results using regex (avoid lxml dependency)
            results = self._parse_results(response.text, num_results)
            
            return DataSourceResult.success_result(results, self.name)
            
        except Exception as e:
            return DataSourceResult.error_result(str(e), self.name)
    
    def _parse_results(self, html: str, max_results: int) -> List[Dict[str, Any]]:
        """Parse search results from DuckDuckGo HTML"""
        results = []
        
        # Pattern to match result links
        link_pattern = r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>'
        snippet_pattern = r'<a[^>]+class="result__snippet"[^>]*>([^<]+)'
        
        # Find all matches
        links = re.findall(link_pattern, html, re.IGNORECASE | re.DOTALL)
        snippets = re.findall(snippet_pattern, html, re.IGNORECASE | re.DOTALL)
        
        for i, (url, title) in enumerate(links[:max_results]):
            domain = normalize_domain(url)
            
            # Skip excluded domains
            if is_excluded_domain(domain):
                continue
            
            snippet = snippets[i] if i < len(snippets) else ""
            
            results.append({
                "url": url,
                "title": title.strip(),
                "domain": domain,
                "snippet": snippet.strip(),
                "source": self.name,
            })
        
        return results
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None


class ShopifyStoreSearch:
    """Search specifically for Shopify stores"""
    
    def __init__(self):
        self.search_engine = DuckDuckGoSearch()
    
    def search_stores(self, keyword: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Search for Shopify stores related to a keyword"""
        queries = [
            f'"{keyword}" site:myshopify.com',
            f'"{keyword}" "powered by Shopify"',
            f'"{keyword}" shopify store',
            f'{keyword} shop online store',
        ]
        
        all_results = []
        seen_domains = set()
        
        for query in queries:
            result = self.search_engine.search(query, num_results=20)
            
            if result.success and result.data:
                for item in result.data:
                    domain = item.get('domain', '')
                    if domain and domain not in seen_domains:
                        seen_domains.add(domain)
                        all_results.append(item)
                        
                        if len(all_results) >= limit:
                            break
            
            if len(all_results) >= limit:
                break
        
        return all_results[:limit]
    
    def search_products(self, keyword: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Search for products related to a keyword"""
        queries = [
            f'"{keyword}" site:*.myshopify.com/products/',
            f'"{keyword}" "add to cart" shop',
            f'{keyword} buy online shop',
        ]
        
        all_results = []
        seen_urls = set()
        
        for query in queries:
            result = self.search_engine.search(query, num_results=20)
            
            if result.success and result.data:
                for item in result.data:
                    url = item.get('url', '')
                    if url and url not in seen_urls:
                        # Check if it's a product URL
                        if '/products/' in url or '/product/' in url:
                            seen_urls.add(url)
                            all_results.append(item)
                            
                            if len(all_results) >= limit:
                                break
            
            if len(all_results) >= limit:
                break
        
        return all_results[:limit]
    
    def close(self):
        self.search_engine.close()


# Optional: SerpAPI integration for better results
class SerpAPISearch(SearchDataSource):
    """Search using SerpAPI (requires API key)"""
    
    name = "SerpAPI"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.api.serp_api_key
        self._client = None
    
    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=config.request.timeout,
                follow_redirects=True,
            )
        return self._client
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def get_status(self) -> DataSourceStatus:
        if not self.api_key:
            return DataSourceStatus.UNAVAILABLE
        return DataSourceStatus.AVAILABLE
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=3))
    def search(self, query: str, num_results: int = 20, **kwargs) -> DataSourceResult:
        """Search using SerpAPI"""
        if not self.api_key:
            return DataSourceResult.error_result("API key not configured", self.name)
        
        try:
            client = self._get_client()
            
            params = {
                "api_key": self.api_key,
                "q": query,
                "num": min(num_results, 100),
                "engine": "google",
            }
            
            response = client.get("https://serpapi.com/search", params=params)
            
            if response.status_code != 200:
                return DataSourceResult.error_result(f"HTTP {response.status_code}", self.name)
            
            data = response.json()
            results = []
            
            for item in data.get("organic_results", []):
                domain = normalize_domain(item.get("link", ""))
                
                if is_excluded_domain(domain):
                    continue
                
                results.append({
                    "url": item.get("link"),
                    "title": item.get("title"),
                    "domain": domain,
                    "snippet": item.get("snippet", ""),
                    "source": self.name,
                })
            
            return DataSourceResult.success_result(results, self.name)
            
        except Exception as e:
            return DataSourceResult.error_result(str(e), self.name)
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None


# Global instances
duckduckgo_search = DuckDuckGoSearch()
shopify_store_search = ShopifyStoreSearch()
