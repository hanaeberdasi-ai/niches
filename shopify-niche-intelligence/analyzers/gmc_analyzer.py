"""
Google Merchant Center suitability analyzer
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from config.settings import GMC_RESTRICTED_CATEGORIES, GMC_HIGH_RISK_KEYWORDS


class GMCSuitability(Enum):
    SUITABLE = "suitable"
    POTENTIALLY_SUITABLE = "potentially_suitable"
    HIGH_RISK = "high_risk"
    NOT_SUITABLE = "not_suitable"


@dataclass
class GMCAnalysisResult:
    """Result of GMC analysis"""
    suitability: GMCSuitability
    score: int  # 0-100
    reasons: List[str]
    warnings: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "suitability": self.suitability.value,
            "score": self.score,
            "reasons": self.reasons,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


class GMCAnalyzer:
    """Analyzes Google Merchant Center suitability"""
    
    # Categories generally suitable for GMC
    SUITABLE_CATEGORIES = [
        "fashion", "clothing", "shoes", "jewelry", "watches",
        "home", "garden", "furniture", "kitchen", "decor",
        "electronics", "computers", "phones", "audio",
        "sports", "fitness", "outdoor", "camping",
        "baby", "kids", "toys",
        "office", "supplies",
        "automotive", "car accessories",
        "pet supplies", "pet food",
        "arts", "crafts",
    ]
    
    # Categories requiring extra caution
    HIGH_RISK_CATEGORIES = [
        "supplements", "vitamins", "health", "wellness",
        "beauty", "skincare", "cosmetics",
        "weight loss", "diet",
        "cbd", "hemp",
        "medical", "devices",
    ]
    
    # Prohibited categories
    PROHIBITED_CATEGORIES = [
        "weapons", "firearms", "ammunition",
        "drugs", "tobacco", "vaping", "smoking",
        "adult", "gambling",
        "counterfeit", "replica",
    ]
    
    def analyze_niche(
        self,
        niche_name: str,
        category: str = "",
        product_names: List[str] = None,
    ) -> Dict[str, Any]:
        """Analyze GMC suitability for a niche"""
        
        product_names = product_names or []
        
        # Combine all text for analysis
        all_text = f"{niche_name} {category} {' '.join(product_names)}".lower()
        
        # Check for prohibited content
        prohibited_matches = self._check_prohibited(all_text)
        if prohibited_matches:
            return GMCAnalysisResult(
                suitability=GMCSuitability.NOT_SUITABLE,
                score=10,
                reasons=[f"Contains prohibited content: {', '.join(prohibited_matches)}"],
                warnings=["Products in this category are typically not allowed on Google Shopping"],
                recommendations=["Consider alternative advertising channels"],
            ).to_dict()
        
        # Check for high-risk content
        high_risk_matches = self._check_high_risk(all_text)
        
        # Check for suitable categories
        suitable_matches = self._check_suitable(all_text)
        
        # Calculate suitability
        if high_risk_matches and not suitable_matches:
            return GMCAnalysisResult(
                suitability=GMCSuitability.HIGH_RISK,
                score=40,
                reasons=["Category may face additional scrutiny"],
                warnings=[
                    f"Potential policy concerns: {', '.join(high_risk_matches[:3])}",
                    "Products may require additional verification",
                ],
                recommendations=[
                    "Ensure all product claims are accurate and substantiated",
                    "Avoid making medical or health claims",
                    "Review Google Merchant Center policies before listing",
                ],
            ).to_dict()
        
        if suitable_matches:
            return GMCAnalysisResult(
                suitability=GMCSuitability.SUITABLE,
                score=80,
                reasons=[
                    f"Category appears generally suitable for Google Shopping",
                    f"Matches suitable categories: {', '.join(suitable_matches[:3])}",
                ],
                warnings=high_risk_matches[:2] if high_risk_matches else [],
                recommendations=[
                    "Ensure accurate product data (title, description, images)",
                    "Maintain competitive pricing",
                    "Keep product availability up to date",
                ],
            ).to_dict()
        
        # Default to potentially suitable
        return GMCAnalysisResult(
            suitability=GMCSuitability.POTENTIALLY_SUITABLE,
            score=60,
            reasons=["Category may be suitable with proper product data"],
            warnings=[
                "Suitability depends on specific products and claims",
                "Some products in this category may face restrictions",
            ],
            recommendations=[
                "Review Google Merchant Center policies",
                "Ensure product data meets Google's requirements",
                "Start with a small product selection to test approval",
            ],
        ).to_dict()
    
    def analyze_product(
        self,
        product_title: str,
        product_description: str = "",
        product_type: str = "",
    ) -> Dict[str, Any]:
        """Analyze GMC suitability for a specific product"""
        
        all_text = f"{product_title} {product_description} {product_type}".lower()
        
        # Check for prohibited content
        prohibited = self._check_prohibited(all_text)
        if prohibited:
            return {
                "suitability": "not_suitable",
                "score": 10,
                "issues": [f"Prohibited content detected: {', '.join(prohibited)}"],
                "recommendation": "This product likely cannot be listed on Google Shopping",
            }
        
        # Check for high-risk keywords
        high_risk = self._check_high_risk_keywords(all_text)
        if high_risk:
            return {
                "suitability": "high_risk",
                "score": 40,
                "issues": [f"High-risk keywords detected: {', '.join(high_risk)}"],
                "recommendation": "Product may face rejection - review and modify claims",
            }
        
        return {
            "suitability": "potentially_suitable",
            "score": 70,
            "issues": [],
            "recommendation": "Product appears suitable - ensure accurate data",
        }
    
    def _check_prohibited(self, text: str) -> List[str]:
        """Check for prohibited categories"""
        matches = []
        for category in self.PROHIBITED_CATEGORIES:
            if category in text:
                matches.append(category)
        return matches
    
    def _check_high_risk(self, text: str) -> List[str]:
        """Check for high-risk categories"""
        matches = []
        for category in self.HIGH_RISK_CATEGORIES:
            if category in text:
                matches.append(category)
        return matches
    
    def _check_suitable(self, text: str) -> List[str]:
        """Check for suitable categories"""
        matches = []
        for category in self.SUITABLE_CATEGORIES:
            if category in text:
                matches.append(category)
        return matches
    
    def _check_high_risk_keywords(self, text: str) -> List[str]:
        """Check for high-risk keywords in product content"""
        matches = []
        for keyword in GMC_HIGH_RISK_KEYWORDS:
            if keyword.lower() in text:
                matches.append(keyword)
        return matches


# Global instance
gmc_analyzer = GMCAnalyzer()
