"""
Niche scoring system
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ScoreLevel(Enum):
    VERY_HIGH = "Very High"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    VERY_LOW = "Very Low"
    UNKNOWN = "Unknown"


@dataclass
class ScoreComponent:
    """Individual score component"""
    name: str
    value: int  # 0-100
    level: ScoreLevel
    explanation: str
    is_estimated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "level": self.level.value,
            "explanation": self.explanation,
            "is_estimated": self.is_estimated,
        }


@dataclass
class NicheScore:
    """Complete niche score with breakdown"""
    overall_score: int
    components: Dict[str, ScoreComponent] = field(default_factory=dict)
    summary: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "components": {k: v.to_dict() for k, v in self.components.items()},
            "summary": self.summary,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendation": self.recommendation,
        }


def value_to_level(value: int) -> ScoreLevel:
    """Convert numeric value to score level"""
    if value >= 80:
        return ScoreLevel.VERY_HIGH
    elif value >= 60:
        return ScoreLevel.HIGH
    elif value >= 40:
        return ScoreLevel.MEDIUM
    elif value >= 20:
        return ScoreLevel.LOW
    else:
        return ScoreLevel.VERY_LOW


class NicheScorer:
    """Calculates niche opportunity scores"""
    
    # Weights for different components
    WEIGHTS = {
        "demand": 0.20,
        "trend": 0.15,
        "competition": 0.15,
        "product_opportunity": 0.15,
        "shopify_opportunity": 0.10,
        "gmc_suitability": 0.10,
        "commercial_intent": 0.10,
        "saturation": 0.05,
    }
    
    def calculate_score(
        self,
        niche_name: str,
        category: str,
        subcategory: str,
        stores_found: int = 0,
        products_found: int = 0,
        avg_price: Optional[float] = None,
        has_trend_data: bool = False,
        trend_direction: str = "unknown",
        gmc_suitability: str = "potentially_suitable",
    ) -> NicheScore:
        """Calculate comprehensive niche score"""
        
        components = {}
        
        # Demand Score (estimated based on available signals)
        demand_score = self._calculate_demand_score(stores_found, products_found)
        components["demand"] = demand_score
        
        # Trend Score
        trend_score = self._calculate_trend_score(has_trend_data, trend_direction)
        components["trend"] = trend_score
        
        # Competition Score (higher is better = less competition)
        competition_score = self._calculate_competition_score(stores_found)
        components["competition"] = competition_score
        
        # Product Opportunity Score
        product_score = self._calculate_product_opportunity(products_found, avg_price)
        components["product_opportunity"] = product_score
        
        # Shopify Opportunity Score
        shopify_score = self._calculate_shopify_opportunity(stores_found, products_found)
        components["shopify_opportunity"] = shopify_score
        
        # GMC Suitability Score
        gmc_score = self._calculate_gmc_score(gmc_suitability, niche_name)
        components["gmc_suitability"] = gmc_score
        
        # Commercial Intent Score
        commercial_score = self._calculate_commercial_intent(avg_price, category)
        components["commercial_intent"] = commercial_score
        
        # Saturation Score (higher is better = less saturated)
        saturation_score = self._calculate_saturation(stores_found)
        components["saturation"] = saturation_score
        
        # Calculate weighted overall score
        overall = sum(
            components[key].value * self.WEIGHTS[key]
            for key in self.WEIGHTS
        )
        overall_score = int(overall)
        
        # Generate insights
        strengths, weaknesses = self._identify_strengths_weaknesses(components)
        summary = self._generate_summary(components, overall_score)
        recommendation = self._generate_recommendation(overall_score, components)
        
        return NicheScore(
            overall_score=overall_score,
            components=components,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation,
        )
    
    def _calculate_demand_score(self, stores: int, products: int) -> ScoreComponent:
        """Estimate demand based on store/product counts"""
        # Without actual search volume, estimate based on marketplace signals
        if stores > 20 and products > 100:
            value = 80
            explanation = "High marketplace presence suggests strong demand"
        elif stores > 10 or products > 50:
            value = 65
            explanation = "Moderate marketplace presence indicates decent demand"
        elif stores > 5 or products > 20:
            value = 50
            explanation = "Some marketplace presence, demand level unclear"
        else:
            value = 40
            explanation = "Limited data available to assess demand"
        
        return ScoreComponent(
            name="Demand",
            value=value,
            level=value_to_level(value),
            explanation=explanation,
            is_estimated=True,
        )
    
    def _calculate_trend_score(self, has_data: bool, direction: str) -> ScoreComponent:
        """Calculate trend score"""
        if not has_data:
            return ScoreComponent(
                name="Trend",
                value=50,
                level=ScoreLevel.UNKNOWN,
                explanation="Trend data not available - requires external API",
                is_estimated=True,
            )
        
        if direction == "rising":
            value = 85
            explanation = "Strong upward trend detected"
        elif direction == "stable":
            value = 60
            explanation = "Stable trend with consistent interest"
        elif direction == "declining":
            value = 30
            explanation = "Declining trend - proceed with caution"
        else:
            value = 50
            explanation = "Trend direction unclear"
        
        return ScoreComponent(
            name="Trend",
            value=value,
            level=value_to_level(value),
            explanation=explanation,
            is_estimated=not has_data,
        )
    
    def _calculate_competition_score(self, stores: int) -> ScoreComponent:
        """Calculate competition score (higher = less competition)"""
        # Inverse relationship - fewer stores = higher opportunity
        if stores < 5:
            value = 85
            explanation = "Low competition - potential first-mover advantage"
        elif stores < 15:
            value = 70
            explanation = "Moderate competition - room for differentiation"
        elif stores < 30:
            value = 50
            explanation = "Competitive market - requires strong positioning"
        else:
            value = 35
            explanation = "Highly competitive - may be difficult to enter"
        
        return ScoreComponent(
            name="Competition",
            value=value,
            level=value_to_level(value),
            explanation=explanation,
            is_estimated=True,
        )
    
    def _calculate_product_opportunity(self, products: int, avg_price: Optional[float]) -> ScoreComponent:
        """Calculate product opportunity score"""
        score = 50
        explanations = []
        
        if products > 50:
            score += 15
            explanations.append("Good product variety available")
        elif products > 20:
            score += 10
            explanations.append("Moderate product selection")
        
        if avg_price:
            if avg_price > 100:
                score += 15
                explanations.append("Higher-ticket products possible")
            elif avg_price > 30:
                score += 10
                explanations.append("Decent price point")
        
        explanation = " | ".join(explanations) if explanations else "Product opportunity unclear"
        
        return ScoreComponent(
            name="Product Opportunity",
            value=min(100, score),
            level=value_to_level(score),
            explanation=explanation,
            is_estimated=True,
        )
    
    def _calculate_shopify_opportunity(self, stores: int, products: int) -> ScoreComponent:
        """Calculate Shopify-specific opportunity"""
        if stores > 10 and products > 30:
            value = 75
            explanation = "Active Shopify presence indicates viable platform"
        elif stores > 5 or products > 15:
            value = 65
            explanation = "Some Shopify activity in this niche"
        else:
            value = 50
            explanation = "Limited Shopify data - may be unexplored opportunity"
        
        return ScoreComponent(
            name="Shopify Opportunity",
            value=value,
            level=value_to_level(value),
            explanation=explanation,
            is_estimated=True,
        )
    
    def _calculate_gmc_score(self, suitability: str, niche_name: str) -> ScoreComponent:
        """Calculate Google Merchant Center suitability score"""
        suitability_scores = {
            "suitable": (85, "Generally suitable for Google Shopping"),
            "potentially_suitable": (65, "Potentially suitable - review GMC policies"),
            "high_risk": (35, "May face policy restrictions - verify carefully"),
            "not_suitable": (10, "Likely restricted by GMC policies"),
        }
        
        value, explanation = suitability_scores.get(
            suitability,
            (50, "GMC suitability requires manual review")
        )
        
        return ScoreComponent(
            name="GMC Suitability",
            value=value,
            level=value_to_level(value),
            explanation=explanation,
            is_estimated=True,
        )
    
    def _calculate_commercial_intent(self, avg_price: Optional[float], category: str) -> ScoreComponent:
        """Calculate commercial intent score"""
        score = 50
        explanations = []
        
        # Price-based scoring
        if avg_price:
            if avg_price > 100:
                score += 20
                explanations.append("Higher margins possible")
            elif avg_price > 50:
                score += 10
                explanations.append("Moderate margin potential")
        
        # Category-based scoring
        high_intent_categories = [
            "Electronics", "Beauty", "Health", "Home", "Fashion"
        ]
        if any(cat in category for cat in high_intent_categories):
            score += 10
            explanations.append("Strong commercial category")
        
        explanation = " | ".join(explanations) if explanations else "Commercial potential unclear"
        
        return ScoreComponent(
            name="Commercial Intent",
            value=min(100, score),
            level=value_to_level(score),
            explanation=explanation,
            is_estimated=True,
        )
    
    def _calculate_saturation(self, stores: int) -> ScoreComponent:
        """Calculate market saturation (higher score = less saturated)"""
        if stores < 5:
            value = 85
            explanation = "Market appears unsaturated - potential opportunity"
        elif stores < 15:
            value = 65
            explanation = "Moderately saturated - differentiation needed"
        elif stores < 30:
            value = 45
            explanation = "Somewhat saturated market"
        else:
            value = 25
            explanation = "Highly saturated - difficult to stand out"
        
        return ScoreComponent(
            name="Saturation",
            value=value,
            level=value_to_level(value),
            explanation=explanation,
            is_estimated=True,
        )
    
    def _identify_strengths_weaknesses(
        self,
        components: Dict[str, ScoreComponent]
    ) -> Tuple[List[str], List[str]]:
        """Identify key strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        for name, component in components.items():
            if component.value >= 70:
                strengths.append(f"{component.name}: {component.explanation}")
            elif component.value < 40:
                weaknesses.append(f"{component.name}: {component.explanation}")
        
        return strengths[:3], weaknesses[:3]
    
    def _generate_summary(self, components: Dict[str, ScoreComponent], overall: int) -> str:
        """Generate human-readable summary"""
        high_scores = [c.name for c in components.values() if c.value >= 70]
        low_scores = [c.name for c in components.values() if c.value < 40]
        
        if overall >= 75:
            summary = "Strong opportunity"
        elif overall >= 60:
            summary = "Promising opportunity"
        elif overall >= 45:
            summary = "Moderate opportunity"
        else:
            summary = "Challenging opportunity"
        
        if high_scores:
            summary += f" with strong {', '.join(high_scores[:2]).lower()}"
        if low_scores:
            summary += f", but watch {', '.join(low_scores[:2]).lower()}"
        
        return summary
    
    def _generate_recommendation(
        self,
        overall: int,
        components: Dict[str, ScoreComponent]
    ) -> str:
        """Generate actionable recommendation"""
        if overall >= 75:
            return "Consider prioritizing this niche for further research and validation"
        elif overall >= 60:
            return "Worth investigating - validate demand and competition before committing"
        elif overall >= 45:
            return "Proceed with caution - address weaknesses before entering"
        else:
            return "Consider other niches unless you have unique competitive advantages"


# Global scorer instance
niche_scorer = NicheScorer()
