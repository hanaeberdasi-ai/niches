"""
Product finder page
"""
import streamlit as st
from typing import List, Dict, Any

from data_sources.search import shopify_store_search
from data_sources.shopify import shopify_verifier
from analyzers.gmc_analyzer import gmc_analyzer
from ui.components import (
    render_product_card, render_gmc_analysis, render_export_buttons
)
from utils.normalization import normalize_domain


def render_product_finder():
    """Render the product finder page"""
    
    st.title("📦 Product Finder")
    st.markdown("Discover products from verified Shopify stores")
    
    # Search input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        keyword = st.text_input(
            "Search for products",
            placeholder="e.g., yoga mat, pet carrier, LED mirror...",
        )
    
    with col2:
        max_products = st.selectbox("Max products", [20, 50, 100], index=1)
    
    # Filters
    with st.expander("🔧 Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_price = st.number_input("Min Price ($)", 0, 10000, 0)
            max_price = st.number_input("Max Price ($)", 0, 10000, 0)
        
        with col2:
            sort_by = st.selectbox(
                "Sort By",
                ["Relevance", "Price (Low to High)", "Price (High to Low)"]
            )
        
        with col3:
            gmc_filter = st.checkbox("Show GMC-suitable only", value=False)
    
    if st.button("🔍 Find Products", type="primary", use_container_width=True):
        if keyword:
            with st.spinner("Searching for products..."):
                progress = st.progress(0)
                status = st.empty()
                
                # Search for stores first
                status.text("Finding stores...")
                store_results = shopify_store_search.search_stores(keyword, limit=20)
                progress.progress(20)
                
                # Get products from verified stores
                all_products = []
                verified_count = 0
                
                for i, store in enumerate(store_results):
                    if len(all_products) >= max_products:
                        break
                    
                    domain = store.get("domain", "")
                    if not domain:
                        continue
                    
                    status.text(f"Checking {domain}...")
                    
                    try:
                        # Verify Shopify
                        if not shopify_verifier.verify_shopify(domain):
                            continue
                        
                        verified_count += 1
                        
                        # Get products
                        products_result = shopify_verifier.get_products(domain, limit=20)
                        
                        if products_result.success:
                            for product in products_result.data:
                                # Filter by keyword relevance
                                title = (product.get("title", "") or "").lower()
                                ptype = (product.get("product_type", "") or "").lower()
                                
                                if keyword.lower() in title or keyword.lower() in ptype:
                                    product["source_store"] = domain
                                    all_products.append(product)
                                    
                                    if len(all_products) >= max_products:
                                        break
                    
                    except Exception:
                        continue
                    
                    progress.progress(20 + int(70 * (i + 1) / len(store_results)))
                
                progress.progress(100)
                status.empty()
                
                # Apply price filters
                if min_price > 0:
                    all_products = [p for p in all_products if (p.get("price") or 0) >= min_price]
                
                if max_price > 0:
                    all_products = [p for p in all_products if (p.get("price") or float('inf')) <= max_price]
                
                # Sort
                if sort_by == "Price (Low to High)":
                    all_products.sort(key=lambda x: x.get("price") or float('inf'))
                elif sort_by == "Price (High to Low)":
                    all_products.sort(key=lambda x: x.get("price") or 0, reverse=True)
                
                st.session_state["product_results"] = all_products
                st.session_state["product_search_stats"] = {
                    "keyword": keyword,
                    "stores_checked": len(store_results),
                    "stores_verified": verified_count,
                    "products_found": len(all_products),
                }
        else:
            st.warning("Please enter a search keyword")
    
    # Display results
    if st.session_state.get("product_results"):
        products = st.session_state["product_results"]
        stats = st.session_state.get("product_search_stats", {})
        
        st.markdown("---")
        
        # Stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Products Found", len(products))
        col2.metric("Stores Verified", stats.get("stores_verified", 0))
        col3.metric("Stores Checked", stats.get("stores_checked", 0))
        
        st.markdown("---")
        st.markdown(f"## 📦 Products for '{stats.get('keyword', '')}'")
        
        # GMC filter
        if gmc_filter:
            products = [p for p in products if analyze_product_gmc(p)]
        
        # Display products
        if products:
            # Product grid
            cols = st.columns(3)
            
            for i, product in enumerate(products):
                with cols[i % 3]:
                    render_product_result(product)
            
            # Export
            st.markdown("---")
            render_export_buttons(products, "products")
        else:
            st.info("No products found matching your criteria")


def render_product_result(product: Dict[str, Any]):
    """Render a single product result"""
    
    title = product.get("title", "Unknown")
    price = product.get("price")
    compare_price = product.get("compare_at_price")
    url = product.get("url", "#")
    image = product.get("image_url")
    store = product.get("source_store", product.get("store_domain", ""))
    ptype = product.get("product_type", "")
    available = product.get("available", True)
    
    with st.container():
        st.markdown(f"""
        <div style="
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            background: white;
        ">
        """, unsafe_allow_html=True)
        
        # Image
        if image:
            st.image(image, use_container_width=True)
        
        # Title
        st.markdown(f"**{title[:50]}{'...' if len(title) > 50 else ''}**")
        
        # Price
        if price:
            if compare_price and compare_price > price:
                st.markdown(f"💰 **${price:.2f}** ~~${compare_price:.2f}~~")
            else:
                st.markdown(f"💰 **${price:.2f}**")
        
        # Meta info
        if ptype:
            st.markdown(f"📂 {ptype}")
        
        if store:
            st.markdown(f"🏪 {store}")
        
        # Availability
        if not available:
            st.markdown("❌ Out of Stock")
        
        # Actions
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"[View →]({url})")
        
        with col2:
            if st.button("📋 GMC Check", key=f"gmc_{product.get('id', title)}"):
                gmc_result = gmc_analyzer.analyze_product(
                    title,
                    product.get("description", ""),
                    ptype,
                )
                st.session_state[f"gmc_result_{product.get('id', title)}"] = gmc_result
        
        # Show GMC result if available
        gmc_key = f"gmc_result_{product.get('id', title)}"
        if st.session_state.get(gmc_key):
            gmc_result = st.session_state[gmc_key]
            status = gmc_result.get("suitability", "unknown")
            
            status_colors = {
                "suitable": "🟢",
                "potentially_suitable": "🟡",
                "high_risk": "🟠",
                "not_suitable": "🔴",
            }
            
            st.markdown(f"{status_colors.get(status, '⚪')} GMC: {status.replace('_', ' ').title()}")
        
        st.markdown("</div>", unsafe_allow_html=True)


def analyze_product_gmc(product: Dict[str, Any]) -> bool:
    """Quick GMC suitability check for filtering"""
    title = product.get("title", "")
    ptype = product.get("product_type", "")
    
    result = gmc_analyzer.analyze_product(title, "", ptype)
    return result.get("suitability") in ["suitable", "potentially_suitable"]
