"""
Store discovery and analysis page
"""
import streamlit as st
from typing import List, Dict, Any

from data_sources.search import shopify_store_search
from data_sources.shopify import shopify_verifier
from analyzers.store_analyzer import store_analyzer
from ui.components import (
    render_score_badge, render_store_card, render_product_card,
    render_score_breakdown, render_export_buttons
)
from utils.normalization import normalize_domain


def render_store_finder():
    """Render the store finder page"""
    
    st.title("🏪 Shopify Store Discovery")
    st.markdown("Find and analyze verified Shopify stores in any niche")
    
    # Search options
    search_type = st.radio(
        "Search Type",
        ["Search by Keyword", "Analyze Specific Store"],
        horizontal=True,
    )
    
    if search_type == "Search by Keyword":
        render_keyword_search()
    else:
        render_specific_store()


def render_keyword_search():
    """Render keyword-based store search"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        keyword = st.text_input(
            "Search keyword",
            placeholder="e.g., fitness equipment, skincare, pet supplies...",
        )
    
    with col2:
        max_stores = st.selectbox("Max stores", [10, 20, 30, 50], index=1)
    
    if st.button("🔍 Find Shopify Stores", type="primary", use_container_width=True):
        if keyword:
            with st.spinner("Searching for Shopify stores..."):
                progress = st.progress(0)
                status = st.empty()
                
                # Search for stores
                status.text("Searching...")
                search_results = shopify_store_search.search_stores(keyword, limit=max_stores * 2)
                progress.progress(30)
                
                # Verify and analyze stores
                verified_stores = []
                
                for i, result in enumerate(search_results):
                    if len(verified_stores) >= max_stores:
                        break
                    
                    domain = result.get("domain", "")
                    if not domain:
                        continue
                    
                    status.text(f"Verifying {domain}...")
                    
                    try:
                        # Analyze store
                        analysis = store_analyzer.analyze_store(
                            domain,
                            target_niche=keyword,
                            max_products=30,
                        )
                        
                        if analysis.verified:
                            verified_stores.append(analysis.to_dict())
                    except Exception:
                        continue
                    
                    progress.progress(30 + int(60 * len(verified_stores) / max_stores))
                
                progress.progress(100)
                status.empty()
                
                st.session_state["store_results"] = verified_stores
        else:
            st.warning("Please enter a keyword")
    
    # Display results
    if st.session_state.get("store_results"):
        results = st.session_state["store_results"]
        
        st.markdown("---")
        st.markdown(f"## ✅ Verified Shopify Stores ({len(results)})")
        st.info("All stores below have been verified as Shopify stores")
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            min_score = st.slider("Minimum Score", 0, 100, 0, key="store_min_score")
        
        with col2:
            sort_by = st.selectbox(
                "Sort By",
                ["Score", "Product Count", "Domain"],
                key="store_sort"
            )
        
        # Filter and sort
        filtered = [r for r in results if (r.get("score", {}) or {}).get("overall_score", 0) >= min_score]
        
        if sort_by == "Score":
            filtered.sort(key=lambda x: (x.get("score", {}) or {}).get("overall_score", 0), reverse=True)
        elif sort_by == "Product Count":
            filtered.sort(key=lambda x: x.get("products_count", 0), reverse=True)
        elif sort_by == "Domain":
            filtered.sort(key=lambda x: x.get("domain", ""))
        
        # Display stores
        for store in filtered:
            render_store_result(store)
        
        # Export
        st.markdown("---")
        render_export_buttons(filtered, "stores")


def render_specific_store():
    """Render specific store analysis"""
    
    domain = st.text_input(
        "Enter store domain",
        placeholder="e.g., example.com or https://example.com",
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_niche = st.text_input(
            "Target niche (optional)",
            placeholder="e.g., fitness, beauty",
            help="Used for relevance scoring"
        )
    
    with col2:
        max_products = st.selectbox("Products to analyze", [50, 100, 200], index=0)
    
    if st.button("📊 Analyze Store", type="primary", use_container_width=True):
        if domain:
            with st.spinner("Analyzing store..."):
                progress = st.progress(0)
                status = st.empty()
                
                def update_status(msg):
                    status.text(msg)
                
                analysis = store_analyzer.analyze_store(
                    domain,
                    target_niche=target_niche,
                    max_products=max_products,
                    progress_callback=update_status,
                )
                
                progress.progress(100)
                status.empty()
                
                if analysis.error:
                    st.error(f"Error: {analysis.error}")
                else:
                    st.session_state["current_store"] = analysis.to_dict()
        else:
            st.warning("Please enter a domain")
    
    # Display analysis
    if st.session_state.get("current_store"):
        render_store_detail(st.session_state["current_store"])


def render_store_result(store: Dict[str, Any]):
    """Render a store result card"""
    
    domain = store.get("domain", "Unknown")
    info = store.get("store_info", {})
    score = store.get("score", {})
    
    name = info.get("name", domain)
    overall_score = score.get("overall_score", 0) if score else 0
    products_count = store.get("products_count", 0)
    
    with st.expander(f"🏪 {name} ({domain}) - Score: {overall_score}/100"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Domain:** [{domain}](https://{domain})")
            st.markdown(f"**Products:** {products_count}")
            
            if info.get("currency"):
                st.markdown(f"**Currency:** {info.get('currency')}")
            
            if info.get("description"):
                st.markdown(f"**Description:** {info.get('description')[:200]}...")
            
            # Social links
            social = info.get("social_links", {})
            if social:
                links = " | ".join([f"[{k.title()}]({v})" for k, v in list(social.items())[:4]])
                st.markdown(f"**Social:** {links}")
            
            # Apps detected
            apps = info.get("detected_apps", [])
            if apps:
                st.markdown(f"**Apps:** {', '.join(apps[:5])}")
        
        with col2:
            render_score_badge(overall_score, "Score")
            
            price_stats = store.get("price_stats", {})
            if price_stats:
                st.markdown(f"**Avg Price:** ${price_stats.get('avg', 0):.2f}")
                st.markdown(f"**Price Range:** ${price_stats.get('min', 0):.2f} - ${price_stats.get('max', 0):.2f}")
        
        # Score breakdown
        if score.get("components"):
            st.markdown("### Score Breakdown")
            render_score_breakdown(score.get("components", {}))
        
        # Sample products
        products = store.get("products_sample", [])
        if products:
            st.markdown(f"### Sample Products ({len(products)})")
            cols = st.columns(3)
            for i, product in enumerate(products[:6]):
                with cols[i % 3]:
                    render_product_card(product)
        
        # Actions
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"📊 Full Analysis", key=f"analyze_{domain}"):
                st.session_state["current_store"] = store
                st.session_state["show_store_detail"] = True
        
        with col2:
            if st.button(f"⭐ Save Store", key=f"save_{domain}"):
                if "saved_stores" not in st.session_state:
                    st.session_state["saved_stores"] = []
                
                save_data = {
                    "domain": domain,
                    "name": name,
                    "score": overall_score,
                }
                
                if save_data not in st.session_state["saved_stores"]:
                    st.session_state["saved_stores"].append(save_data)
                    st.success(f"Saved {name}!")


def render_store_detail(store: Dict[str, Any]):
    """Render detailed store analysis"""
    
    st.markdown("---")
    
    domain = store.get("domain", "Unknown")
    info = store.get("store_info", {})
    score = store.get("score", {})
    
    # Header
    st.markdown(f"## 🏪 {info.get('name', domain)}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Domain:** [{domain}](https://{domain})")
        st.markdown("**Status:** ✅ Shopify Verified")
    
    with col2:
        st.markdown(f"**Currency:** {info.get('currency', 'N/A')}")
        st.markdown(f"**Language:** {info.get('language', 'N/A')}")
    
    with col3:
        if score:
            render_score_badge(score.get("overall_score", 0), "Store Score")
    
    # Tabs for different sections
    tabs = st.tabs(["📊 Overview", "📦 Products", "🔧 Technology", "📈 Analysis"])
    
    with tabs[0]:  # Overview
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Store Information")
            
            if info.get("description"):
                st.markdown(f"**Description:** {info.get('description')}")
            
            if info.get("contact_email"):
                st.markdown(f"**Contact:** {info.get('contact_email')}")
            
            social = info.get("social_links", {})
            if social:
                st.markdown("**Social Links:**")
                for platform, url in social.items():
                    st.markdown(f"• [{platform.title()}]({url})")
        
        with col2:
            st.markdown("### Score Breakdown")
            if score and score.get("components"):
                render_score_breakdown(score.get("components", {}))
            
            # Insights
            insights = score.get("insights", []) if score else []
            if insights:
                st.markdown("### Insights")
                for insight in insights:
                    st.markdown(f"• {insight}")
    
    with tabs[1]:  # Products
        products = store.get("products_sample", [])
        products_count = store.get("products_count", 0)
        
        st.markdown(f"### Products ({products_count} total)")
        
        price_stats = store.get("price_stats", {})
        if price_stats:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Min Price", f"${price_stats.get('min', 0):.2f}")
            col2.metric("Max Price", f"${price_stats.get('max', 0):.2f}")
            col3.metric("Avg Price", f"${price_stats.get('avg', 0):.2f}")
            col4.metric("Median", f"${price_stats.get('median', 0):.2f}")
        
        # Category breakdown
        categories = store.get("category_breakdown", {})
        if categories:
            st.markdown("### Product Categories")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
                st.markdown(f"• {cat}: {count} products")
        
        # Product grid
        if products:
            st.markdown("### Sample Products")
            cols = st.columns(3)
            for i, product in enumerate(products[:12]):
                with cols[i % 3]:
                    render_product_card(product)
    
    with tabs[2]:  # Technology
        st.markdown("### Detected Technology")
        
        if info.get("theme"):
            st.markdown(f"**Shopify Theme:** {info.get('theme')}")
        
        apps = info.get("detected_apps", [])
        if apps:
            st.markdown("**Detected Apps:**")
            cols = st.columns(3)
            for i, app in enumerate(apps):
                with cols[i % 3]:
                    st.markdown(f"✓ {app}")
        else:
            st.info("No specific apps detected")
    
    with tabs[3]:  # Analysis
        st.markdown("### Market Analysis")
        
        if score:
            summary = score.get("summary", "")
            if summary:
                st.markdown(f"**Summary:** {summary}")
            
            insights = score.get("insights", [])
            if insights:
                st.markdown("**Key Insights:**")
                for insight in insights:
                    st.markdown(f"• {insight}")
        
        # Collections
        collections = store.get("collections", [])
        if collections:
            st.markdown("### Store Collections")
            for collection in collections[:10]:
                st.markdown(f"• [{collection.get('title')}]({collection.get('url')})")
