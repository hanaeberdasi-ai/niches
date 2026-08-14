"""
Shopify Niche Intelligence Tool
A powerful research platform for discovering profitable Shopify niches, products, and stores.

Author: Shopify Niche Intelligence
Version: 1.0.0
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Shopify Niche Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """
        # Shopify Niche Intelligence
        
        A powerful tool for discovering profitable Shopify niches, products, and stores.
        
        **Features:**
        - Niche Discovery & Scoring
        - Shopify Store Verification
        - Product Analysis
        - Google Merchant Center Suitability
        - Export to CSV/Excel/JSON
        
        **Data Transparency:**
        All data marked as "estimated" is clearly labeled.
        We never fabricate sales, revenue, or traffic data.
        """
    }
)

# Import UI components
from ui.dashboard import render_dashboard
from ui.niche_page import render_niche_finder
from ui.store_page import render_store_finder
from ui.trending_page import render_trending
from ui.product_page import render_product_finder


def init_session_state():
    """Initialize session state variables"""
    defaults = {
        "active_page": "dashboard",
        "saved_niches": [],
        "saved_stores": [],
        "saved_products": [],
        "niche_results": [],
        "store_results": [],
        "product_results": [],
        "trending_results": [],
        "search_keyword": "",
        "auto_discover": False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    """Render the sidebar navigation"""
    
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 1.5em; margin: 0;">🎯 Shopify Niche</h1>
        <h2 style="font-size: 1em; margin: 0; color: #666;">Intelligence Tool</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Navigation
    pages = {
        "dashboard": ("🏠 Dashboard", "Home"),
        "trending": ("🔥 Trending", "Hot opportunities"),
        "niche_finder": ("🎯 Niche Finder", "Discover niches"),
        "product_finder": ("📦 Products", "Find products"),
        "stores": ("🏪 Stores", "Shopify stores"),
    }
    
    st.sidebar.markdown("### Navigation")
    
    for page_key, (label, description) in pages.items():
        if st.sidebar.button(
            label,
            key=f"nav_{page_key}",
            use_container_width=True,
            help=description,
        ):
            st.session_state["active_page"] = page_key
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Saved items count
    saved_niches = len(st.session_state.get("saved_niches", []))
    saved_stores = len(st.session_state.get("saved_stores", []))
    
    st.sidebar.markdown(f"""
    ### 📊 Saved Items
    - Niches: **{saved_niches}**
    - Stores: **{saved_stores}**
    """)
    
    if saved_niches > 0 or saved_stores > 0:
        if st.sidebar.button("📋 View Saved", use_container_width=True):
            st.session_state["active_page"] = "saved"
            st.rerun()
        
        if st.sidebar.button("🗑️ Clear All", use_container_width=True):
            st.session_state["saved_niches"] = []
            st.session_state["saved_stores"] = []
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Data source status
    st.sidebar.markdown("### 🔌 Data Sources")
    
    # Check for API keys
    import os
    has_serp = bool(os.getenv("SERP_API_KEY"))
    has_google = bool(os.getenv("GOOGLE_API_KEY"))
    
    st.sidebar.markdown(f"""
    - DuckDuckGo: ✅ Active
    - Shopify API: ✅ Active
    - SerpAPI: {'✅' if has_serp else '⚪'} {'Active' if has_serp else 'Not configured'}
    - Google API: {'✅' if has_google else '⚪'} {'Active' if has_google else 'Not configured'}
    """)
    
    st.sidebar.markdown("---")
    
    # Footer
    st.sidebar.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.8em;">
        <p>v1.0.0</p>
        <p>Only verified Shopify stores</p>
        <p>No fabricated data</p>
    </div>
    """, unsafe_allow_html=True)


def render_saved_items():
    """Render saved items page"""
    
    st.title("📋 Saved Items")
    
    tab1, tab2 = st.tabs(["⭐ Saved Niches", "🏪 Saved Stores"])
    
    with tab1:
        saved_niches = st.session_state.get("saved_niches", [])
        
        if saved_niches:
            for i, niche in enumerate(saved_niches):
                with st.expander(f"🎯 {niche.get('name')} - Score: {niche.get('score')}"):
                    st.markdown(f"**Category:** {niche.get('category')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔍 Analyze", key=f"analyze_saved_{i}"):
                            st.session_state["search_keyword"] = niche.get("name")
                            st.session_state["active_page"] = "niche_finder"
                            st.rerun()
                    
                    with col2:
                        if st.button("🗑️ Remove", key=f"remove_niche_{i}"):
                            st.session_state["saved_niches"].pop(i)
                            st.rerun()
        else:
            st.info("No saved niches yet. Use the ⭐ button on any niche to save it.")
    
    with tab2:
        saved_stores = st.session_state.get("saved_stores", [])
        
        if saved_stores:
            for i, store in enumerate(saved_stores):
                with st.expander(f"🏪 {store.get('name', store.get('domain'))}"):
                    st.markdown(f"**Domain:** {store.get('domain')}")
                    st.markdown(f"**Score:** {store.get('score', 'N/A')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        domain = store.get('domain', '')
                        st.markdown(f"[Visit Store](https://{domain})")
                    
                    with col2:
                        if st.button("🗑️ Remove", key=f"remove_store_{i}"):
                            st.session_state["saved_stores"].pop(i)
                            st.rerun()
        else:
            st.info("No saved stores yet. Use the ⭐ button on any store to bookmark it.")


def render_settings():
    """Render settings page"""
    
    st.title("⚙️ Settings")
    
    st.markdown("### API Configuration")
    st.info("""
    To enable additional data sources, add API keys to your environment variables
    or Streamlit secrets.
    
    **For local development:**
    Create a `.env` file with your keys.
    
    **For Streamlit Cloud:**
    Add keys to your app's Secrets in the dashboard.
    """)
    
    st.markdown("### Available APIs")
    
    st.markdown("""
    | API | Purpose | Status |
    |-----|---------|--------|
    | DuckDuckGo | Store search | ✅ Active (no key needed) |
    | Shopify Public | Store verification | ✅ Active (no key needed) |
    | SerpAPI | Enhanced search | Requires `SERP_API_KEY` |
    | Google Custom Search | Search results | Requires `GOOGLE_API_KEY` + `GOOGLE_CSE_ID` |
    """)
    
    st.markdown("### Cache Settings")
    
    if st.button("🗑️ Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")
    
    st.markdown("### Data Transparency")
    st.markdown("""
    This tool is committed to data accuracy:
    
    - ✅ Only verified Shopify stores are shown
    - ✅ Estimated data is clearly marked
    - ✅ "N/A" is shown when data is unavailable
    - ❌ We never fabricate sales, revenue, or traffic
    - ❌ We never show unverified store metrics
    """)


def main():
    """Main application entry point"""
    
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render active page
    active_page = st.session_state.get("active_page", "dashboard")
    
    if active_page == "dashboard":
        render_dashboard()
    elif active_page == "trending":
        render_trending()
    elif active_page == "niche_finder":
        render_niche_finder()
    elif active_page == "product_finder":
        render_product_finder()
    elif active_page == "stores":
        render_store_finder()
    elif active_page == "saved":
        render_saved_items()
    elif active_page == "settings":
        render_settings()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
