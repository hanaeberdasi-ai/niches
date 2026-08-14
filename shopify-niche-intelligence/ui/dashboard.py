"""
Dashboard page
"""
import streamlit as st
from typing import List, Dict, Any

from data_sources.categories import category_manager
from analyzers.niche_analyzer import niche_analyzer
from ui.components import (
    render_score_badge, render_niche_card, render_metric_card,
    render_export_buttons, render_filter_sidebar
)


def render_dashboard():
    """Render the main dashboard"""
    
    st.title("🏠 Shopify Niche Intelligence Dashboard")
    st.markdown("Discover profitable niches, products, and Shopify stores")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    categories = category_manager.get_all_categories()
    all_niches = category_manager.get_all_niches()
    
    with col1:
        render_metric_card(
            "Categories",
            len(categories),
            "Available to explore",
            "📂"
        )
    
    with col2:
        render_metric_card(
            "Niches",
            len(all_niches),
            "Ready to analyze",
            "🎯"
        )
    
    with col3:
        # Show saved items count from session
        saved_count = len(st.session_state.get("saved_niches", []))
        render_metric_card(
            "Saved Niches",
            saved_count,
            "In your list",
            "⭐"
        )
    
    with col4:
        saved_stores = len(st.session_state.get("saved_stores", []))
        render_metric_card(
            "Saved Stores",
            saved_stores,
            "Bookmarked",
            "🏪"
        )
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("## 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔥 Find Trending Niches", use_container_width=True):
            st.session_state["active_page"] = "trending"
            st.rerun()
    
    with col2:
        if st.button("🎯 Auto-Discover Opportunities", use_container_width=True):
            st.session_state["active_page"] = "niche_finder"
            st.session_state["auto_discover"] = True
            st.rerun()
    
    with col3:
        if st.button("🏪 Search Shopify Stores", use_container_width=True):
            st.session_state["active_page"] = "stores"
            st.rerun()
    
    st.markdown("---")
    
    # Category overview
    st.markdown("## 📂 Browse by Category")
    
    # Create tabs for categories
    tabs = st.tabs(categories[:8])  # Show first 8 categories
    
    for tab, category in zip(tabs, categories[:8]):
        with tab:
            subcategories = category_manager.get_subcategories(category)
            
            cols = st.columns(3)
            for i, subcat in enumerate(subcategories[:6]):
                with cols[i % 3]:
                    niches = category_manager.get_niches(category, subcat)
                    
                    with st.expander(f"📁 {subcat} ({len(niches)})"):
                        for niche in niches[:5]:
                            if st.button(f"🎯 {niche}", key=f"{category}_{subcat}_{niche}"):
                                st.session_state["active_page"] = "niche_finder"
                                st.session_state["search_keyword"] = niche
                                st.rerun()
    
    st.markdown("---")
    
    # Recent activity / saved items
    st.markdown("## ⭐ Saved Items")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Saved Niches")
        saved_niches = st.session_state.get("saved_niches", [])
        
        if saved_niches:
            for niche in saved_niches[:5]:
                st.markdown(f"• {niche.get('name', 'Unknown')} - Score: {niche.get('score', 'N/A')}")
            
            if st.button("View All Saved Niches"):
                st.session_state["active_page"] = "saved"
                st.rerun()
        else:
            st.info("No saved niches yet. Use the ⭐ button to save niches you find interesting.")
    
    with col2:
        st.markdown("### Saved Stores")
        saved_stores = st.session_state.get("saved_stores", [])
        
        if saved_stores:
            for store in saved_stores[:5]:
                st.markdown(f"• {store.get('name', store.get('domain', 'Unknown'))}")
            
            if st.button("View All Saved Stores"):
                st.session_state["active_page"] = "saved"
                st.rerun()
        else:
            st.info("No saved stores yet. Use the ⭐ button to bookmark stores.")
    
    st.markdown("---")
    
    # Help section
    with st.expander("ℹ️ How to Use This Tool"):
        st.markdown("""
        ### Getting Started
        
        1. **🔥 Trending**: View currently trending niches and opportunities
        2. **🎯 Niche Finder**: Search for specific niches or auto-discover opportunities
        3. **📦 Product Finder**: Search for products and analyze competition
        4. **🏪 Shopify Stores**: Discover and analyze verified Shopify stores
        5. **📊 Market Analysis**: Get detailed market insights
        
        ### Understanding Scores
        
        - **75-100**: Excellent opportunity - prioritize for research
        - **60-74**: Good opportunity - worth investigating
        - **45-59**: Moderate opportunity - proceed with caution
        - **Below 45**: Challenging opportunity - may need unique advantages
        
        ### Data Transparency
        
        This tool only shows verified Shopify stores and clearly marks:
        - **Estimated** data when exact figures aren't available
        - **N/A** when data cannot be determined
        - **Verified** when Shopify is confirmed
        
        We never fabricate sales, revenue, or traffic data.
        """)
