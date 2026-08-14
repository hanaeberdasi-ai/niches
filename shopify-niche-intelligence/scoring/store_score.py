"""
Store scoring system
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .niche_score import ScoreLevel, value_to_level


@dataclass
class StoreScoreComponent:
    """Individual store score component"""
    name: str
    value: int
    level: ScoreLevel
    explanation: str
    is_estimated: bool = False


@dataclass
class StoreScore:
    """Complete store score"""
    overall_score: int
    components: Dict[str, StoreScoreComponent] = field(default_factory=dict)
    summary: str = ""
    insights: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "components": {
                k: {
                    "name": v.name,
                    "value": v.value,
                    "level": v.level.value,
                    "explanation": v.explanation,
                    "is_estimated": v.is_estimated,
                }
                for k, v in self.components.items()
            },
            "summary": self.summary,
            "insights": self.insights,
        }


class StoreScorer:
    """Calculates Shopify store opportunity scores"""
    
    WEIGHTS = {
        "niche_relevance": 0.20,
        "catalog_depth": 0.15,
        "pricing": 0.15,
        "technology": 0.15,
        "professionalism": 0.15,
        "social_presence": 0.10,
        "market_position": 0.10,
    }
    
    def calculate_score(
        self,
        store_info: Dict[str, Any],
        products: List[Dict[str, Any]] = None,
        target_niche: str = "",
    ) -> StoreScore:
        """Calculate comprehensive store score"""
        
        products = products or []
        components = {}
        
        # Niche Relevance
        components["niche_relevance"] = self._score_niche_relevance(
            store_info, products, target_niche
        )
        
        # Catalog Depth
        components["catalog_depth"] = self._score_catalog_depth(products)
        
        # Pricing
        components["pricing"] = self._score_pricing(products)
        
        # Technology
        components["technology"] = self._score_technology(store_info)
        
        # Professionalism
        components["professionalism"] = self._score_professionalism(store_info)
        
        # Social Presence
        components["social_presence"] = self._score_social_presence(store_info)
        
        # Market Position
        components["market_position"] = self._score_market_position(store_info, products)
        
        # Calculate weighted overall score
        overall = sum(
            components[key].value * self.WEIGHTS[key]
            for key in self.WEIGHTS
        )
        overall_score = int(overall)
        
        # Generate insights
        insights = self._generate_insights(components, store_info, products)
        summary = self._generate_summary(overall_score, components)
        
        return StoreScore(
            overall_score=overall_score,
            components=components,
            summary=summary,
            insights=insights,
        )
    
    def _score_niche_relevance(
        self,
        store_info: Dict[str, Any],
        products: List[Dict[str, Any]],
        target_niche: str,
    ) -> StoreScoreComponent:
        """Score how relevant the store is to target niche"""
        if not target_niche:
            return StoreScoreComponent(
                name="Niche Relevance",
                value=50,
                level=ScoreLevel.MEDIUM,
                explanation="No target niche specified",
                is_estimated=True,
            )
        
        target_lower = target_niche.lower()
        
        # Check store name/description
        name = (store_info.get("name", "") or "").lower()
        description = (store_info.get("description", "") or "").lower()
        
        # Check products
        product_matches = sum(
            1 for p in products
            if target_lower in (p.get("title", "") or "").lower()
            or target_lower in (p.get("product_type", "") or "").lower()
        )
        
        score = 30  # Base score
        
        if target_lower in name:
            score += 30
        if target_lower in description:
            score += 20
        if product_matches > 5:
            score += 20
        elif product_matches > 0:
            score += 10
        
        score = min(100, score)
        
        return StoreScoreComponent(
            name="Niche Relevance",
            value=score,
            level=value_to_level(score),
            explanation=f"Found {product_matches} matching products",
            is_estimated=True,
        )
    
    def _score_catalog_depth(self, products: List[Dict[str, Any]]) -> StoreScoreComponent:
        """Score store catalog depth"""
        count = len(products)
        
        if count >= 100:
            score = 85
            explanation = f"Extensive catalog with {count}+ products"
        elif count >= 50:
            score = 70
            explanation = f"Good catalog size with {count} products"
        elif count >= 20:
            score = 55
            explanation = f"Moderate catalog with {count} products"
        elif count >= 5:
            score = 40
            explanation = f"Small catalog with {count} products"
        else:
            score = 25
            explanation = f"Very limited catalog ({count} products)"
        
        return StoreScoreComponent(
            name="Catalog Depth",
            value=score,
            level=value_to_level(score),
            explanation=explanation,
            is_estimated=False,
        )
    
    def _score_pricing(self, products: List[Dict[str, Any]]) -> StoreScoreComponent:
        """Score store pricing strategy"""
        if not products:
            return StoreScoreComponent(
                name="Pricing",
                value=50,
                level=ScoreLevel.UNKNOWN,
                explanation="No pricing data available",
                is_estimated=True,
            )
        
        prices = [p.get("price") for p in products if p.get("price")]
        if not prices:
            return StoreScoreComponent(
                name="Pricing",
                value=50,
                level=ScoreLevel.UNKNOWN,
                explanation="No pricing data available",
                is_estimated=True,
            )
        
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        # Score based on average price (higher prices = better margins potential)
        if avg_price >= 100:
            score = 80
            explanation = f"Premium pricing (${avg_price:.0f} avg)"
        elif avg_price >= 50:
            score = 65
            explanation = f"Mid-range pricing (${avg_price:.0f} avg)"
        elif avg_price >= 20:
            score = 50
            explanation = f"Budget-friendly pricing (${avg_price:.0f} avg)"
        else:
            score = 35
            explanation = f"Low pricing (${avg_price:.0f} avg)"
        
        return StoreScoreComponent(
            name="Pricing",
            value=score,
            level=value_to_level(score),
            explanation=explanation,
            is_estimated=False,
        )
    
    def _score_technology(self, store_info: Dict[str, Any]) -> StoreScoreComponent:
        """Score store technology/apps"""
        apps = store_info.get("detected_apps", [])
        theme = store_info.get("theme")
        
        score = 40  # Base score
        explanations = []
        
        if apps:
            score += min(30, len(apps) * 5)
            explanations.append(f"{len(apps)} apps detected")
        
        # Check for important app categories
        important_apps = ["Klaviyo", "Yotpo", "Judge.me", "Loox", "ReCharge"]
        found_important = [a for a in apps if any(i in a for i in important_apps)]
        if found_important:
            score += 15
            explanations.append("Marketing/review apps present")
        
        if theme:
            score += 10
            explanations.append(f"Theme: {theme}")
        
        score = min(100, score)
        explanation = " | ".join(explanations) if explanations else "Basic technology setup"
        
        return StoreScoreComponent(
            name="Technology",
            value=score,
            level=value_to_level(score),
            explanation=explanation,
            is_estimated=False,
        )
    
    def _score_professionalism(self, store_info: Dict[str, Any]) -> StoreScoreComponent:
        """Score store professionalism"""
        score = 40
        factors = []
        
        if store_info.get("description"):
            score += 15
            factors.append("Has description")
        
        if store_info.get("contact_email"):
            score += 15
            factors.append("Contact available")
        
        social = store_info.get("social_links", {})
        if social:
            score += 10
            factors.append(f"{len(social)} social links")
        
        if store_info.get("currency"):
            score += 10
            factors.append("Currency set")
        
        score = min(100, score)
        explanation = " | ".join(factors) if factors else "Basic setup"
        
        return StoreScoreComponent(
            name="Professionalism",
            value=score,
            level=value_to_level(score),
            explanation=explanation,
            is_estimated=True,
        )
    
    def _score_social_presence(self, store_info: Dict[str, Any]) -> StoreScoreComponent:
        """Score social media presence"""
        social = store_info.get("social_links", {})
        
        if not social:
            return StoreScoreComponent(
                name="Social Presence",
                value=30,
                level=ScoreLevel.LOW,
                explanation="No social links found",
                is_estimated=True,
            )
        
        count = len(social)
        score = min(100, 40 + (count * 15))
        platforms = list(social.keys())
        
        return StoreScoreComponent(
            name="Social Presence",
            value=score,
            level=value_to_level(score),
            explanation=f"Found: {', '.join(platforms[:3])}",
            is_estimated=False,
        )
    
    def _score_market_position(
        self,
        store_info: Dict[str, Any],
        products: List[Dict[str, Any]],
    ) -> StoreScoreComponent:
        """Score overall market position"""
        score = 50
        factors = []
        
        # Product variety
        if products:
            types = set(p.get("product_type") for p in products if p.get("product_type"))
            if len(types) >= 5:
                score += 15
                factors.append("Diverse product types")
            elif len(types) >= 2:
                score += 10
                factors.append("Multiple product types")
        
        # Brand indicators
        if store_info.get("name"):
            score += 10
            factors.append("Branded store")
        
        explanation = " | ".join(factors) if factors else "Standard market position"
        
        return StoreScoreComponent(
            name="Market Position",
            value=min(100, score),
            level=value_to_level(score),
            explanation=explanation,
            is_estimated=True,
        )
    
    def _generate_insights(
        self,
        components: Dict[str, StoreScoreComponent],
        store_info: Dict[str, Any],
        products: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        # High-scoring areas
        strong = [c for c in components.values() if c.value >= 70]
        if strong:
            insights.append(f"Strengths: {', '.join(c.name for c in strong)}")
        
        # Weak areas
        weak = [c for c in components.values() if c.value < 40]
        if weak:
            insights.append(f"Areas to watch: {', '.join(c.name for c in weak)}")
        
        # Product insights
        if products:
            prices = [p.get("price") for p in products if p.get("price")]
            if prices:
                insights.append(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        
        return insights[:5]
    
    def _generate_summary(
        self,
        overall: int,
        components: Dict[str, StoreScoreComponent],
    ) -> str:
        """Generate summary description"""
        if overall >= 75:
            return "Well-established store with strong presence"
        elif overall >= 60:
            return "Solid store with good fundamentals"
        elif overall >= 45:
            return "Developing store with growth potential"
        else:
            return "Early-stage or limited store"


# Global scorer instance
store_scorer = StoreScorer()
