"""
Trending opportunities page
"""
import streamlit as st
from typing import List, Dict, Any

from data_sources.categories import category_manager
from analyzers.niche_analyzer import niche_analyzer
from ui.components import (
    render_score_badge, render_niche_card, render_metric_card,
    render_export_buttons
)


def render_trending():
    """Render the trending opportunities page"""
    
    st.title("🔥 Trending Opportunities")
    st.markdown("Discover niches and products with strong current momentum")
    
    # Note about data limitations
    st.info("""
    **Note:** Without access to real-time trend APIs (Google Trends, etc.), 
    trending data is estimated based on category analysis and marketplace signals.
    Consider adding API keys for more accurate trend data.
    """)
    
    # Category tabs
    st.markdown("## 📊 Top Opportunities by Category")
    
    categories = category_manager.get_all_categories()
    selected_categories = st.multiselect(
        "Select categories to analyze",
        categories,
        default=categories[:3],
    )
    
    if st.button("🔥 Find Trending Opportunities", type="primary", use_container_width=True):
        if selected_categories:
            all_results = []
            
            with st.spinner("Analyzing trends..."):
                progress = st.progress(0)
                status = st.empty()
                
                for i, category in enumerate(selected_categories):
                    status.text(f"Analyzing {category}...")
                    
                    try:
                        results = niche_analyzer.get_category_analysis(
                            category,
                            progress_callback=lambda msg: status.text(msg),
                        )
                        
                        for result in results:
                            result_dict = result.to_dict()
                            result_dict["source_category"] = category
                            all_results.append(result_dict)
                    
                    except Exception as e:
                        st.warning(f"Error analyzing {category}: {str(e)}")
                    
                    progress.progress((i + 1) / len(selected_categories))
                
                status.empty()
            
            # Sort by score
            all_results.sort(key=lambda x: x["score"]["overall_score"], reverse=True)
            st.session_state["trending_results"] = all_results
        else:
            st.warning("Please select at least one category")
    
    # Display results
    if st.session_state.get("trending_results"):
        results = st.session_state["trending_results"]
        
        st.markdown("---")
        
        # Top opportunities summary
        st.markdown("## 🏆 Top Opportunities")
        
        # Top 3 cards
        top_3 = results[:3]
        cols = st.columns(3)
        
        for i, result in enumerate(top_3):
            with cols[i]:
                niche = result.get("niche", {})
                score = result.get("score", {})
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, 
                        {'#10B981' if i == 0 else '#3B82F6' if i == 1 else '#8B5CF6'} 0%, 
                        {'#059669' if i == 0 else '#2563EB' if i == 1 else '#7C3AED'} 100%);
                    padding: 20px;
                    border-radius: 12px;
                    color: white;
                    text-align: center;
                ">
                    <div style="font-size: 2em;">{'🥇' if i == 0 else '🥈' if i == 1 else '🥉'}</div>
                    <h3 style="margin: 10px 0;">{niche.get('name', 'Unknown')}</h3>
                    <div style="font-size: 2em; font-weight: bold;">{score.get('overall_score', 0)}/100</div>
                    <p>{niche.get('category', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detailed results
        st.markdown("## 📋 All Opportunities")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_score = st.slider("Minimum Score", 0, 100, 50, key="trending_min")
        
        with col2:
            category_filter = st.multiselect(
                "Filter by Category",
                list(set(r.get("source_category", "") for r in results)),
                key="trending_cat"
            )
        
        with col3:
            sort_option = st.selectbox(
                "Sort By",
                ["Score", "Category", "Stores Found"],
                key="trending_sort"
            )
        
        # Apply filters
        filtered = results
        
        if min_score > 0:
            filtered = [r for r in filtered if r["score"]["overall_score"] >= min_score]
        
        if category_filter:
            filtered = [r for r in filtered if r.get("source_category") in category_filter]
        
        # Apply sort
        if sort_option == "Score":
            filtered.sort(key=lambda x: x["score"]["overall_score"], reverse=True)
        elif sort_option == "Category":
            filtered.sort(key=lambda x: x.get("source_category", ""))
        elif sort_option == "Stores Found":
            filtered.sort(key=lambda x: x.get("stores_found", 0), reverse=True)
        
        # Display results
        for result in filtered:
            render_trending_result(result)
        
        # Export
        st.markdown("---")
        render_export_buttons(filtered, "trending")


def render_trending_result(result: Dict[str, Any]):
    """Render a trending result"""
    
    niche = result.get("niche", {})
    score = result.get("score", {})
    
    name = niche.get("name", "Unknown")
    category = result.get("source_category", niche.get("category", ""))
    overall_score = score.get("overall_score", 0)
    
    # Determine trend indicator
    if overall_score >= 75:
        trend_icon = "🔥"
        trend_text = "Hot"
    elif overall_score >= 60:
        trend_icon = "📈"
        trend_text = "Rising"
    else:
        trend_icon = "➡️"
        trend_text = "Stable"
    
    with st.expander(f"{trend_icon} {name} - {overall_score}/100 ({trend_text})"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Category:** {category}")
            st.markdown(f"**Stores Found:** {result.get('stores_found', 0)}")
            st.markdown(f"**Products Found:** {result.get('products_found', 0)}")
        
        with col2:
            price_range = result.get("price_range", {})
            if price_range:
                st.markdown(f"**Avg Price:** ${price_range.get('avg', 0):.2f}")
                st.markdown(f"**Price Range:** ${price_range.get('min', 0):.2f} - ${price_range.get('max', 0):.2f}")
            
            gmc = result.get("gmc_analysis", {})
            st.markdown(f"**GMC Status:** {gmc.get('suitability', 'Unknown').replace('_', ' ').title()}")
        
        with col3:
            render_score_badge(overall_score, "Score")
        
        # Summary
        st.markdown(f"**Summary:** {score.get('summary', 'N/A')}")
        
        # Strengths
        strengths = score.get("strengths", [])
        if strengths:
            st.success("**Why it's trending:**\n" + "\n".join([f"• {s}" for s in strengths]))
        
        # Recommendation
        st.info(f"**Recommendation:** {score.get('recommendation', 'N/A')}")
        
        # Actions
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"🔍 Deep Analyze", key=f"analyze_trend_{name}"):
                st.session_state["search_keyword"] = name
                st.session_state["active_page"] = "niche_finder"
                st.rerun()
        
        with col2:
            if st.button(f"⭐ Save", key=f"save_trend_{name}"):
                if "saved_niches" not in st.session_state:
                    st.session_state["saved_niches"] = []
                
                save_data = {
                    "name": name,
                    "category": category,
                    "score": overall_score,
                    "data": result,
                }
                
                st.session_state["saved_niches"].append(save_data)
                st.success(f"Saved {name}!")
