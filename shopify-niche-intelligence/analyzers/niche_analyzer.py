"""
Niche analysis engine
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import streamlit as st

from data_sources.categories import category_manager, Niche
from data_sources.search import shopify_store_search
from data_sources.shopify import shopify_verifier
from scoring.niche_score import niche_scorer, NicheScore
from analyzers.gmc_analyzer import gmc_analyzer
from utils.normalization import deduplicate_stores


@dataclass
class NicheAnalysisResult:
    """Result of niche analysis"""
    niche: Niche
    score: NicheScore
    stores_found: int = 0
    products_found: int = 0
    verified_stores: List[Dict[str, Any]] = field(default_factory=list)
    sample_products: List[Dict[str, Any]] = field(default_factory=list)
    gmc_analysis: Dict[str, Any] = field(default_factory=dict)
    price_range: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "niche": self.niche.to_dict(),
            "score": self.score.to_dict(),
            "stores_found": self.stores_found,
            "products_found": self.products_found,
            "verified_stores": self.verified_stores,
            "sample_products": self.sample_products[:10],
            "gmc_analysis": self.gmc_analysis,
            "price_range": self.price_range,
        }


class NicheAnalyzer:
    """Analyzes niches for Shopify opportunities"""
    
    def __init__(self):
        self.category_manager = category_manager
        self.store_search = shopify_store_search
        self.shopify = shopify_verifier
        self.scorer = niche_scorer
        self.gmc = gmc_analyzer
    
    def analyze_niche(
        self,
        niche: Niche,
        max_stores: int = 10,
        verify_stores: bool = True,
        progress_callback=None,
    ) -> NicheAnalysisResult:
        """Perform comprehensive niche analysis"""
        
        # Search for stores in this niche
        keyword = niche.name
        
        if progress_callback:
            progress_callback(f"Searching for {keyword} stores...")
        
        search_results = self.store_search.search_stores(keyword, limit=max_stores * 2)
        
        # Verify Shopify stores
        verified_stores = []
        all_products = []
        
        for i, result in enumerate(search_results[:max_stores * 2]):
            if len(verified_stores) >= max_stores:
                break
            
            domain = result.get("domain", "")
            if not domain:
                continue
            
            if progress_callback:
                progress_callback(f"Verifying {domain}...")
            
            try:
                if verify_stores:
                    is_shopify = self.shopify.verify_shopify(domain)
                    if not is_shopify:
                        continue
                
                # Get store info
                store_result = self.shopify.get_store_info(domain)
                if store_result.success:
                    store_info = store_result.data
                    store_info["search_result"] = result
                    verified_stores.append(store_info)
                    
                    # Get sample products
                    products_result = self.shopify.get_products(domain, limit=20)
                    if products_result.success:
                        all_products.extend(products_result.data)
            
            except Exception as e:
                continue
        
        # Deduplicate
        verified_stores = deduplicate_stores(verified_stores)
        
        # Calculate price statistics
        prices = [p.get("price") for p in all_products if p.get("price")]
        price_range = {}
        if prices:
            price_range = {
                "min": min(prices),
                "max": max(prices),
                "avg": sum(prices) / len(prices),
            }
        
        # GMC Analysis
        gmc_result = self.gmc.analyze_niche(niche.name, niche.category)
        
        # Calculate score
        score = self.scorer.calculate_score(
            niche_name=niche.name,
            category=niche.category,
            subcategory=niche.subcategory,
            stores_found=len(verified_stores),
            products_found=len(all_products),
            avg_price=price_range.get("avg"),
            gmc_suitability=gmc_result.get("suitability", "potentially_suitable"),
        )
        
        return NicheAnalysisResult(
            niche=niche,
            score=score,
            stores_found=len(verified_stores),
            products_found=len(all_products),
            verified_stores=verified_stores,
            sample_products=all_products[:20],
            gmc_analysis=gmc_result,
            price_range=price_range,
        )
    
    def analyze_keyword(
        self,
        keyword: str,
        max_stores: int = 10,
        progress_callback=None,
    ) -> List[NicheAnalysisResult]:
        """Analyze a keyword and find related niches"""
        
        # Find matching niches
        niches = self.category_manager.search_niches(keyword)
        
        if not niches:
            # Create a custom niche from keyword
            niches = [Niche(
                name=keyword.title(),
                category="Custom",
                subcategory="User Search",
                keywords=[keyword],
            )]
        
        results = []
        
        for niche in niches[:5]:  # Limit to top 5 matching niches
            if progress_callback:
                progress_callback(f"Analyzing: {niche.name}")
            
            try:
                result = self.analyze_niche(
                    niche,
                    max_stores=max_stores,
                    progress_callback=progress_callback,
                )
                results.append(result)
            except Exception as e:
                continue
        
        # Sort by score
        results.sort(key=lambda r: r.score.overall_score, reverse=True)
        
        return results
    
    def auto_discover(
        self,
        num_niches: int = 10,
        progress_callback=None,
    ) -> List[NicheAnalysisResult]:
        """Automatically discover promising niches"""
        
        # Get a mix of trending and random niches
        trending = self.category_manager.get_trending_niches(num_niches // 2)
        random_niches = self.category_manager.get_random_niches(num_niches // 2)
        
        all_niches = trending + random_niches
        
        results = []
        
        for i, niche in enumerate(all_niches[:num_niches]):
            if progress_callback:
                progress_callback(f"Discovering {i+1}/{num_niches}: {niche.name}")
            
            try:
                result = self.analyze_niche(
                    niche,
                    max_stores=5,  # Fewer stores for discovery
                    verify_stores=True,
                    progress_callback=progress_callback,
                )
                results.append(result)
            except Exception as e:
                continue
        
        # Sort by opportunity score
        results.sort(key=lambda r: r.score.overall_score, reverse=True)
        
        return results
    
    def get_category_analysis(
        self,
        category: str,
        progress_callback=None,
    ) -> List[NicheAnalysisResult]:
        """Analyze all niches in a category"""
        
        results = []
        subcategories = self.category_manager.get_subcategories(category)
        
        for subcat in subcategories:
            niches = self.category_manager.get_niches(category, subcat)
            
            for niche_name in niches[:3]:  # Limit per subcategory
                niche = Niche(
                    name=niche_name,
                    category=category,
                    subcategory=subcat,
                )
                
                if progress_callback:
                    progress_callback(f"Analyzing: {niche_name}")
                
                try:
                    result = self.analyze_niche(
                        niche,
                        max_stores=5,
                        progress_callback=progress_callback,
                    )
                    results.append(result)
                except Exception:
                    continue
        
        results.sort(key=lambda r: r.score.overall_score, reverse=True)
        return results


# Global instance
niche_analyzer = NicheAnalyzer()
