"""
Niche finder page
"""
import streamlit as st
from typing import List, Dict, Any

from data_sources.categories import category_manager
from analyzers.niche_analyzer import niche_analyzer
from ui.components import (
    render_score_badge, render_niche_card, render_score_breakdown,
    render_gmc_analysis, render_store_card, render_product_card,
    render_export_buttons
)


def render_niche_finder():
    """Render the niche finder page"""
    
    st.title("🎯 Niche Finder")
    st.markdown("Discover profitable Shopify niches with intelligent scoring")
    
    # Search mode selection
    search_mode = st.radio(
        "Search Mode",
        ["Keyword Search", "Auto-Discovery", "Category Browse"],
        horizontal=True,
    )
    
    results = []
    
    if search_mode == "Keyword Search":
        # Keyword search
        col1, col2 = st.columns([3, 1])
        
        with col1:
            keyword = st.text_input(
                "Enter keyword",
                value=st.session_state.get("search_keyword", ""),
                placeholder="e.g., beauty devices, pet products, home gym...",
            )
        
        with col2:
            max_stores = st.selectbox("Max stores per niche", [5, 10, 15, 20], index=1)
        
        if st.button("🔍 Search Niches", type="primary", use_container_width=True):
            if keyword:
                with st.spinner("Analyzing niches..."):
                    progress = st.progress(0)
                    status = st.empty()
                    
                    def update_progress(msg):
                        status.text(msg)
                    
                    results = niche_analyzer.analyze_keyword(
                        keyword,
                        max_stores=max_stores,
                        progress_callback=update_progress,
                    )
                    
                    progress.progress(100)
                    status.empty()
                    
                    st.session_state["niche_results"] = [r.to_dict() for r in results]
            else:
                st.warning("Please enter a keyword to search")
    
    elif search_mode == "Auto-Discovery":
        st.markdown("### 🤖 Automatic Opportunity Discovery")
        st.markdown("Let the system discover promising niches for you")
        
        num_niches = st.slider("Number of niches to analyze", 5, 20, 10)
        
        if st.button("🚀 Start Discovery", type="primary", use_container_width=True) or st.session_state.get("auto_discover"):
            st.session_state["auto_discover"] = False
            
            with st.spinner("Discovering opportunities..."):
                progress = st.progress(0)
                status = st.empty()
                
                def update_progress(msg):
                    status.text(msg)
                
                results = niche_analyzer.auto_discover(
                    num_niches=num_niches,
                    progress_callback=update_progress,
                )
                
                progress.progress(100)
                status.empty()
                
                st.session_state["niche_results"] = [r.to_dict() for r in results]
    
    else:  # Category Browse
        st.markdown("### 📂 Browse Categories")
        
        categories = category_manager.get_all_categories()
        selected_category = st.selectbox("Select Category", categories)
        
        if selected_category:
            if st.button("📊 Analyze Category", type="primary", use_container_width=True):
                with st.spinner(f"Analyzing {selected_category}..."):
                    progress = st.progress(0)
                    status = st.empty()
                    
                    def update_progress(msg):
                        status.text(msg)
                    
                    results = niche_analyzer.get_category_analysis(
                        selected_category,
                        progress_callback=update_progress,
                    )
                    
                    progress.progress(100)
                    status.empty()
                    
                    st.session_state["niche_results"] = [r.to_dict() for r in results]
    
    # Display results
    if st.session_state.get("niche_results"):
        results_data = st.session_state["niche_results"]
        
        st.markdown("---")
        st.markdown(f"## 📊 Results ({len(results_data)} niches found)")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_score = st.slider("Minimum Score", 0, 100, 0)
        
        with col2:
            sort_by = st.selectbox(
                "Sort By",
                ["Score (High to Low)", "Score (Low to High)", "Stores Found", "Products Found"]
            )
        
        with col3:
            gmc_filter = st.multiselect(
                "GMC Suitability",
                ["suitable", "potentially_suitable", "high_risk", "not_suitable"],
                default=["suitable", "potentially_suitable"]
            )
        
        # Apply filters
        filtered = [
            r for r in results_data
            if r["score"]["overall_score"] >= min_score
            and r.get("gmc_analysis", {}).get("suitability", "unknown") in gmc_filter
        ]
        
        # Apply sorting
        if sort_by == "Score (High to Low)":
            filtered.sort(key=lambda x: x["score"]["overall_score"], reverse=True)
        elif sort_by == "Score (Low to High)":
            filtered.sort(key=lambda x: x["score"]["overall_score"])
        elif sort_by == "Stores Found":
            filtered.sort(key=lambda x: x.get("stores_found", 0), reverse=True)
        elif sort_by == "Products Found":
            filtered.sort(key=lambda x: x.get("products_found", 0), reverse=True)
        
        st.markdown(f"Showing {len(filtered)} of {len(results_data)} results")
        
        # Display each niche
        for result in filtered:
            render_niche_result(result)
        
        # Export
        st.markdown("---")
        render_export_buttons(filtered, "niches")


def render_niche_result(result: Dict[str, Any]):
    """Render a single niche result with expandable details"""
    niche = result.get("niche", {})
    score = result.get("score", {})
    
    name = niche.get("name", "Unknown")
    category = niche.get("category", "")
    subcategory = niche.get("subcategory", "")
    overall_score = score.get("overall_score", 0)
    
    with st.expander(f"🎯 {name} - Score: {overall_score}/100", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Category:** {category} > {subcategory}")
            st.markdown(f"**Summary:** {score.get('summary', 'N/A')}")
            
            # Strengths and weaknesses
            strengths = score.get("strengths", [])
            weaknesses = score.get("weaknesses", [])
            
            if strengths:
                st.success("**Strengths:**\n" + "\n".join([f"• {s}" for s in strengths]))
            
            if weaknesses:
                st.warning("**Weaknesses:**\n" + "\n".join([f"• {w}" for w in weaknesses]))
            
            st.info(f"**Recommendation:** {score.get('recommendation', 'N/A')}")
        
        with col2:
            render_score_badge(overall_score, "Opportunity")
            st.markdown(f"**Stores Found:** {result.get('stores_found', 0)}")
            st.markdown(f"**Products Found:** {result.get('products_found', 0)}")
            
            price_range = result.get("price_range", {})
            if price_range:
                st.markdown(f"**Price Range:** ${price_range.get('min', 0):.2f} - ${price_range.get('max', 0):.2f}")
                st.markdown(f"**Avg Price:** ${price_range.get('avg', 0):.2f}")
        
        # Score breakdown
        st.markdown("### 📊 Score Breakdown")
        render_score_breakdown(score.get("components", {}))
        
        # GMC Analysis
        st.markdown("### 🛒 Google Merchant Center Analysis")
        render_gmc_analysis(result.get("gmc_analysis", {}))
        
        # Verified stores
        stores = result.get("verified_stores", [])
        if stores:
            st.markdown(f"### 🏪 Verified Shopify Stores ({len(stores)})")
            for store in stores[:5]:
                render_store_card(store, show_score=False)
        
        # Sample products
        products = result.get("sample_products", [])
        if products:
            st.markdown(f"### 📦 Sample Products ({len(products)})")
            cols = st.columns(3)
            for i, product in enumerate(products[:6]):
                with cols[i % 3]:
                    render_product_card(product)
        
        # Save button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(f"⭐ Save Niche", key=f"save_{name}"):
                if "saved_niches" not in st.session_state:
                    st.session_state["saved_niches"] = []
                
                save_data = {
                    "name": name,
                    "category": category,
                    "score": overall_score,
                    "data": result,
                }
                
                if save_data not in st.session_state["saved_niches"]:
                    st.session_state["saved_niches"].append(save_data)
                    st.success(f"Saved {name}!")
                else:
                    st.info("Already saved")
