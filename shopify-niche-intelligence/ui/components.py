"""
Reusable UI components
"""
import streamlit as st
from typing import Dict, Any, List, Optional
import plotly.express as px
import plotly.graph_objects as go


def render_score_badge(score: int, label: str = "Score") -> None:
    """Render a score badge with color coding"""
    if score >= 75:
        color = "#10B981"  # Green
        bg_color = "#D1FAE5"
    elif score >= 60:
        color = "#3B82F6"  # Blue
        bg_color = "#DBEAFE"
    elif score >= 45:
        color = "#F59E0B"  # Yellow
        bg_color = "#FEF3C7"
    else:
        color = "#EF4444"  # Red
        bg_color = "#FEE2E2"
    
    st.markdown(f"""
    <div style="
        display: inline-block;
        background-color: {bg_color};
        color: {color};
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.2em;
        border: 2px solid {color};
    ">
        {label}: {score}/100
    </div>
    """, unsafe_allow_html=True)


def render_score_breakdown(components: Dict[str, Any]) -> None:
    """Render score breakdown as a bar chart"""
    if not components:
        return
    
    names = []
    values = []
    colors = []
    
    for key, component in components.items():
        if isinstance(component, dict):
            names.append(component.get("name", key))
            val = component.get("value", 0)
            values.append(val)
            
            if val >= 70:
                colors.append("#10B981")
            elif val >= 50:
                colors.append("#3B82F6")
            elif val >= 30:
                colors.append("#F59E0B")
            else:
                colors.append("#EF4444")
    
    fig = go.Figure(go.Bar(
        x=values,
        y=names,
        orientation='h',
        marker_color=colors,
        text=values,
        textposition='outside',
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_title="Score",
        xaxis_range=[0, 100],
        showlegend=False,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_metric_card(
    title: str,
    value: Any,
    subtitle: str = "",
    icon: str = "",
    is_estimated: bool = False,
) -> None:
    """Render a metric card"""
    estimated_badge = ' <span style="font-size: 0.7em; color: #888;">(estimated)</span>' if is_estimated else ''
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
    ">
        <div style="font-size: 2em;">{icon}</div>
        <div style="font-size: 1.8em; font-weight: bold;">{value}{estimated_badge}</div>
        <div style="font-size: 1em; opacity: 0.9;">{title}</div>
        <div style="font-size: 0.8em; opacity: 0.7;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def render_store_card(store: Dict[str, Any], show_score: bool = True) -> None:
    """Render a store info card"""
    name = store.get("name", store.get("domain", "Unknown"))
    domain = store.get("domain", "")
    currency = store.get("currency", "N/A")
    verified = store.get("shopify_verified", False)
    
    verified_badge = "✅ Shopify Verified" if verified else ""
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### 🏪 {name}")
            st.markdown(f"**Domain:** [{domain}](https://{domain})")
            st.markdown(f"**Currency:** {currency} | {verified_badge}")
            
            social = store.get("social_links", {})
            if social:
                social_text = " | ".join([f"[{k.title()}]({v})" for k, v in list(social.items())[:3]])
                st.markdown(f"**Social:** {social_text}")
        
        with col2:
            if show_score and store.get("score"):
                score = store["score"]
                if isinstance(score, dict):
                    render_score_badge(score.get("overall_score", 0), "Score")


def render_product_card(product: Dict[str, Any]) -> None:
    """Render a product card"""
    title = product.get("title", "Unknown Product")
    price = product.get("price")
    url = product.get("url", "#")
    image = product.get("image_url")
    store = product.get("store_domain", "")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if image:
            st.image(image, width=100)
        else:
            st.markdown("📦")
    
    with col2:
        st.markdown(f"**{title[:60]}{'...' if len(title) > 60 else ''}**")
        if price:
            st.markdown(f"💰 ${price:.2f}")
        if store:
            st.markdown(f"🏪 {store}")
        st.markdown(f"[View Product]({url})")


def render_niche_card(niche_result: Dict[str, Any]) -> None:
    """Render a niche analysis card"""
    niche = niche_result.get("niche", {})
    score = niche_result.get("score", {})
    
    name = niche.get("name", "Unknown")
    category = niche.get("category", "")
    overall_score = score.get("overall_score", 0)
    summary = score.get("summary", "")
    
    # GMC suitability
    gmc = niche_result.get("gmc_analysis", {})
    gmc_status = gmc.get("suitability", "unknown")
    
    gmc_colors = {
        "suitable": ("✅", "#10B981"),
        "potentially_suitable": ("⚠️", "#F59E0B"),
        "high_risk": ("⚠️", "#EF4444"),
        "not_suitable": ("❌", "#EF4444"),
    }
    gmc_icon, gmc_color = gmc_colors.get(gmc_status, ("❓", "#888"))
    
    with st.container():
        st.markdown(f"""
        <div style="
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            background: white;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0;">{name}</h3>
                    <p style="color: #666; margin: 5px 0;">{category}</p>
                </div>
                <div style="
                    background: {'#D1FAE5' if overall_score >= 60 else '#FEF3C7' if overall_score >= 45 else '#FEE2E2'};
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 1.3em;
                ">
                    {overall_score}/100
                </div>
            </div>
            <p style="margin-top: 10px;">{summary}</p>
            <div style="display: flex; gap: 20px; margin-top: 10px;">
                <span>🏪 {niche_result.get('stores_found', 0)} stores</span>
                <span>📦 {niche_result.get('products_found', 0)} products</span>
                <span style="color: {gmc_color};">{gmc_icon} GMC: {gmc_status.replace('_', ' ').title()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_gmc_analysis(gmc_data: Dict[str, Any]) -> None:
    """Render GMC analysis section"""
    suitability = gmc_data.get("suitability", "unknown")
    score = gmc_data.get("score", 0)
    reasons = gmc_data.get("reasons", [])
    warnings = gmc_data.get("warnings", [])
    recommendations = gmc_data.get("recommendations", [])
    
    status_config = {
        "suitable": ("✅", "Suitable", "#10B981", "#D1FAE5"),
        "potentially_suitable": ("⚠️", "Potentially Suitable", "#F59E0B", "#FEF3C7"),
        "high_risk": ("⚠️", "High Risk", "#EF4444", "#FEE2E2"),
        "not_suitable": ("❌", "Not Suitable", "#EF4444", "#FEE2E2"),
    }
    
    icon, label, color, bg = status_config.get(
        suitability,
        ("❓", "Unknown", "#888", "#f5f5f5")
    )
    
    st.markdown(f"""
    <div style="
        background: {bg};
        border: 2px solid {color};
        border-radius: 12px;
        padding: 20px;
    ">
        <h4 style="color: {color}; margin: 0;">
            {icon} Google Merchant Center: {label}
        </h4>
        <p style="margin-top: 10px;">Score: {score}/100</p>
    </div>
    """, unsafe_allow_html=True)
    
    if reasons:
        st.markdown("**Analysis:**")
        for reason in reasons:
            st.markdown(f"• {reason}")
    
    if warnings:
        st.warning("**Warnings:**\n" + "\n".join([f"• {w}" for w in warnings]))
    
    if recommendations:
        st.info("**Recommendations:**\n" + "\n".join([f"• {r}" for r in recommendations]))


def render_filter_sidebar() -> Dict[str, Any]:
    """Render filter controls in sidebar and return filter values"""
    st.sidebar.markdown("## 🔍 Filters")
    
    filters = {}
    
    # Score filter
    filters["min_score"] = st.sidebar.slider(
        "Minimum Score",
        0, 100, 0,
        help="Filter results by minimum opportunity score"
    )
    
    # Competition filter
    filters["competition"] = st.sidebar.selectbox(
        "Competition Level",
        ["All", "Low", "Medium", "High"],
        help="Filter by competition level"
    )
    
    # Price range
    st.sidebar.markdown("**Price Range**")
    col1, col2 = st.sidebar.columns(2)
    filters["min_price"] = col1.number_input("Min $", 0, 10000, 0)
    filters["max_price"] = col2.number_input("Max $", 0, 10000, 0)
    
    # GMC Suitability
    filters["gmc_filter"] = st.sidebar.multiselect(
        "GMC Suitability",
        ["Suitable", "Potentially Suitable", "High Risk", "Not Suitable"],
        default=["Suitable", "Potentially Suitable"],
    )
    
    # Sort options
    filters["sort_by"] = st.sidebar.selectbox(
        "Sort By",
        ["Score (High to Low)", "Score (Low to High)", "Stores Found", "Products Found"],
    )
    
    return filters


def render_export_buttons(
    data: List[Dict[str, Any]],
    prefix: str = "export",
) -> None:
    """Render export buttons"""
    from utils.export import export_to_csv, export_to_excel, export_to_json
    
    if not data:
        st.info("No data to export")
        return
    
    st.markdown("### 📥 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data, csv_name = export_to_csv(data, prefix)
        st.download_button(
            "📄 Download CSV",
            data=csv_data,
            file_name=csv_name,
            mime="text/csv",
        )
    
    with col2:
        excel_data, excel_name = export_to_excel(data, prefix)
        st.download_button(
            "📊 Download Excel",
            data=excel_data,
            file_name=excel_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    
    with col3:
        json_data, json_name = export_to_json(data, prefix)
        st.download_button(
            "🔧 Download JSON",
            data=json_data,
            file_name=json_name,
            mime="application/json",
        )


def render_loading_animation(message: str = "Loading...") -> None:
    """Render a loading animation"""
    st.markdown(f"""
    <div style="text-align: center; padding: 40px;">
        <div style="font-size: 3em;">⏳</div>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)
