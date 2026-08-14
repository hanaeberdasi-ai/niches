"""
Store analysis engine
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from data_sources.shopify import shopify_verifier
from scoring.store_score import store_scorer, StoreScore
from utils.normalization import normalize_domain


@dataclass
class StoreAnalysisResult:
    """Result of store analysis"""
    domain: str
    verified: bool
    store_info: Dict[str, Any] = field(default_factory=dict)
    products: List[Dict[str, Any]] = field(default_factory=list)
    collections: List[Dict[str, Any]] = field(default_factory=list)
    score: Optional[StoreScore] = None
    price_stats: Dict[str, float] = field(default_factory=dict)
    category_breakdown: Dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "verified": self.verified,
            "store_info": self.store_info,
            "products_count": len(self.products),
            "products_sample": self.products[:10],
            "collections": self.collections,
            "score": self.score.to_dict() if self.score else None,
            "price_stats": self.price_stats,
            "category_breakdown": self.category_breakdown,
            "error": self.error,
        }


class StoreAnalyzer:
    """Analyzes Shopify stores"""
    
    def __init__(self):
        self.shopify = shopify_verifier
        self.scorer = store_scorer
    
    def analyze_store(
        self,
        domain: str,
        target_niche: str = "",
        max_products: int = 100,
        progress_callback=None,
    ) -> StoreAnalysisResult:
        """Perform comprehensive store analysis"""
        
        domain = normalize_domain(domain)
        
        if progress_callback:
            progress_callback(f"Verifying Shopify: {domain}")
        
        # Verify Shopify
        is_shopify = self.shopify.verify_shopify(domain)
        
        if not is_shopify:
            return StoreAnalysisResult(
                domain=domain,
                verified=False,
                error="Domain does not appear to be a Shopify store",
            )
        
        # Get store info
        if progress_callback:
            progress_callback(f"Getting store information...")
        
        store_result = self.shopify.get_store_info(domain)
        
        if not store_result.success:
            return StoreAnalysisResult(
                domain=domain,
                verified=True,
                error=f"Could not retrieve store info: {store_result.error}",
            )
        
        store_info = store_result.data
        
        # Get products
        if progress_callback:
            progress_callback(f"Fetching products...")
        
        products_result = self.shopify.get_products(domain, limit=max_products)
        products = products_result.data if products_result.success else []
        
        # Get collections
        if progress_callback:
            progress_callback(f"Fetching collections...")
        
        collections_result = self.shopify.get_collections(domain)
        collections = collections_result.data if collections_result.success else []
        
        # Calculate price statistics
        prices = [p.get("price") for p in products if p.get("price")]
        price_stats = {}
        if prices:
            price_stats = {
                "min": min(prices),
                "max": max(prices),
                "avg": sum(prices) / len(prices),
                "median": sorted(prices)[len(prices) // 2],
            }
        
        # Category breakdown
        categories = {}
        for p in products:
            ptype = p.get("product_type") or "Uncategorized"
            categories[ptype] = categories.get(ptype, 0) + 1
        
        # Calculate score
        if progress_callback:
            progress_callback(f"Calculating score...")
        
        score = self.scorer.calculate_score(
            store_info=store_info,
            products=products,
            target_niche=target_niche,
        )
        
        return StoreAnalysisResult(
            domain=domain,
            verified=True,
            store_info=store_info,
            products=products,
            collections=collections,
            score=score,
            price_stats=price_stats,
            category_breakdown=categories,
        )
    
    def analyze_multiple(
        self,
        domains: List[str],
        target_niche: str = "",
        progress_callback=None,
    ) -> List[StoreAnalysisResult]:
        """Analyze multiple stores"""
        
        results = []
        
        for i, domain in enumerate(domains):
            if progress_callback:
                progress_callback(f"Analyzing store {i+1}/{len(domains)}: {domain}")
            
            try:
                result = self.analyze_store(
                    domain,
                    target_niche=target_niche,
                    max_products=50,
                )
                results.append(result)
            except Exception as e:
                results.append(StoreAnalysisResult(
                    domain=domain,
                    verified=False,
                    error=str(e),
                ))
        
        # Sort by score
        results.sort(
            key=lambda r: r.score.overall_score if r.score else 0,
            reverse=True
        )
        
        return results
    
    def quick_verify(self, domain: str) -> Dict[str, Any]:
        """Quick Shopify verification without full analysis"""
        domain = normalize_domain(domain)
        is_shopify = self.shopify.verify_shopify(domain)
        
        return {
            "domain": domain,
            "is_shopify": is_shopify,
        }
    
    def get_store_products(
        self,
        domain: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get products from a store"""
        domain = normalize_domain(domain)
        
        # Verify first
        if not self.shopify.verify_shopify(domain):
            return []
        
        result = self.shopify.get_products(domain, limit=limit)
        return result.data if result.success else []


# Global instance
store_analyzer = StoreAnalyzer()
