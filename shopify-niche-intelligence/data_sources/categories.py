"""
Category and niche data management
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import random

from config.settings import CATEGORIES


@dataclass
class Niche:
    """Represents a niche/sub-category"""
    name: str
    category: str
    subcategory: str
    keywords: List[str] = field(default_factory=list)
    related_niches: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "subcategory": self.subcategory,
            "keywords": self.keywords,
            "related_niches": self.related_niches,
        }


class CategoryManager:
    """Manages categories and niches"""
    
    def __init__(self):
        self.categories = CATEGORIES
        self._niche_cache = {}
    
    def get_all_categories(self) -> List[str]:
        """Get all top-level categories"""
        return list(self.categories.keys())
    
    def get_subcategories(self, category: str) -> List[str]:
        """Get subcategories for a category"""
        return list(self.categories.get(category, {}).keys())
    
    def get_niches(self, category: str, subcategory: str) -> List[str]:
        """Get niches for a subcategory"""
        return self.categories.get(category, {}).get(subcategory, [])
    
    def get_all_niches(self) -> List[Niche]:
        """Get all niches as Niche objects"""
        niches = []
        
        for category, subcats in self.categories.items():
            for subcategory, niche_list in subcats.items():
                for niche_name in niche_list:
                    niche = Niche(
                        name=niche_name,
                        category=category,
                        subcategory=subcategory,
                        keywords=self._generate_keywords(niche_name, subcategory),
                        related_niches=self._get_related_niches(niche_name, subcategory, niche_list)
                    )
                    niches.append(niche)
        
        return niches
    
    def _generate_keywords(self, niche: str, subcategory: str) -> List[str]:
        """Generate search keywords for a niche"""
        keywords = [
            niche.lower(),
            f"{niche.lower()} products",
            f"best {niche.lower()}",
            f"{subcategory.lower()} {niche.lower()}",
        ]
        return keywords
    
    def _get_related_niches(self, niche: str, subcategory: str, niche_list: List[str]) -> List[str]:
        """Get related niches"""
        return [n for n in niche_list if n != niche][:3]
    
    def search_niches(self, keyword: str) -> List[Niche]:
        """Search for niches matching a keyword"""
        keyword_lower = keyword.lower()
        matches = []
        
        for category, subcats in self.categories.items():
            cat_lower = category.lower()
            
            for subcategory, niche_list in subcats.items():
                subcat_lower = subcategory.lower()
                
                for niche_name in niche_list:
                    niche_lower = niche_name.lower()
                    
                    # Check if keyword matches
                    if (keyword_lower in niche_lower or
                        keyword_lower in subcat_lower or
                        keyword_lower in cat_lower):
                        
                        niche = Niche(
                            name=niche_name,
                            category=category,
                            subcategory=subcategory,
                            keywords=self._generate_keywords(niche_name, subcategory),
                            related_niches=self._get_related_niches(niche_name, subcategory, niche_list)
                        )
                        matches.append(niche)
        
        return matches
    
    def get_trending_niches(self, limit: int = 20) -> List[Niche]:
        """
        Get potentially trending niches.
        Note: Without external trend data, this returns a curated selection.
        """
        # Curated list of typically trending categories
        trending_areas = [
            ("Beauty & Personal Care", "Beauty Devices"),
            ("Health & Wellness", "Wellness Devices"),
            ("Electronics & Tech", "Wearables"),
            ("Home & Garden", "Smart Home"),
            ("Pets", "Pet Tech"),
            ("Sports & Outdoors", "Fitness"),
        ]
        
        trending = []
        
        for category, subcategory in trending_areas:
            niches = self.get_niches(category, subcategory)
            for niche_name in niches:
                niche = Niche(
                    name=niche_name,
                    category=category,
                    subcategory=subcategory,
                    keywords=self._generate_keywords(niche_name, subcategory),
                    related_niches=[]
                )
                trending.append(niche)
                
                if len(trending) >= limit:
                    break
            
            if len(trending) >= limit:
                break
        
        return trending[:limit]
    
    def get_random_niches(self, limit: int = 10) -> List[Niche]:
        """Get random selection of niches for auto-discovery"""
        all_niches = self.get_all_niches()
        return random.sample(all_niches, min(limit, len(all_niches)))
    
    def expand_keyword(self, keyword: str) -> List[str]:
        """Expand a keyword into related search terms"""
        keyword_lower = keyword.lower()
        
        expansions = [keyword]
        
        # Find matching niches and add their keywords
        matches = self.search_niches(keyword)
        for match in matches[:5]:
            expansions.extend(match.keywords)
        
        # Add common modifiers
        modifiers = ["best", "top", "premium", "professional", "affordable"]
        for mod in modifiers[:2]:
            expansions.append(f"{mod} {keyword}")
        
        # Deduplicate
        return list(dict.fromkeys(expansions))
    
    def get_category_hierarchy(self) -> Dict[str, Any]:
        """Get the full category hierarchy"""
        return self.categories
    
    def get_niche_path(self, niche_name: str) -> Optional[Tuple[str, str, str]]:
        """Get the category path for a niche (category, subcategory, niche)"""
        for category, subcats in self.categories.items():
            for subcategory, niches in subcats.items():
                if niche_name in niches:
                    return (category, subcategory, niche_name)
        return None


# Global instance
category_manager = CategoryManager()
