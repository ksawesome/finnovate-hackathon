"""
Project Aura: AI-Powered Financial Statement Review Agent

Multi-page Streamlit application for GL account validation, consolidation, and reporting.
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Local imports
from src.analytics import calculate_gl_hygiene_score, get_pending_items_report
from src.auth import AuthService
from src.auth_ui import render_login_page, render_user_menu
from src.db import get_mongo_database
from src.db.mongodb import get_audit_trail_collection
from src.db.postgres import get_gl_accounts_by_period
from src.insights import (
    compare_multi_period,
    generate_drill_down_report,
    generate_executive_summary,
    generate_proactive_insights,
)
from src.visualizations import create_hygiene_gauge, create_trend_line_chart

# Page configuration
st.set_page_config(
    page_title="Project Aura - Financial Review Agent",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Authentication gate - must be logged in to access app
if not AuthService.is_authenticated():
    render_login_page()
    st.stop()

# Custom CSS - Enterprise Adani Design
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --primary: #004C97;
  --accent: #0097A9;
  --light: #f9fafb;
  --text: #1b1f23;
  --success: #2ECC71;
  --warning: #F39C12;
  --danger: #E74C3C;
  --bg-shift: 0;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    scroll-behavior: smooth;
}

section.main > div:first-child {
    background: linear-gradient(
        135deg,
        hsl(213, 100%, calc(95% - var(--bg-shift) * 0.1%)) 0%,
        hsl(0, 0%, calc(100% - var(--bg-shift) * 0.05%)) 100%
    );
    background-attachment: fixed;
    animation: fadein 0.8s ease-in;
    transition: background 0.3s ease-out;
}

@keyframes fadein {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Headers */
.main-header {
    font-size: 2.3rem;
    font-weight: 700;
    letter-spacing: -0.8px;
    color: var(--primary);
    margin-bottom: 0.5rem;
    margin-top: 0;
    background: linear-gradient(90deg, #004C97 0%, #0097A9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

h2 {
    font-weight: 600;
    color: var(--primary);
    margin-top: 2rem;
    margin-bottom: 1rem;
}

h3 {
    font-weight: 600;
    color: #374151;
    margin-top: 1.5rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #002952 0%, #004C97 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stRadio > div {
    background: rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 0.5rem;
    backdrop-filter: blur(10px);
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.2);
}

/* Metric cards with depth */
.metric-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,76,151,0.08), 0 1px 3px rgba(0,76,151,0.06);
    padding: 1.25rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(0,76,151,0.1);
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0,76,151,0.12), 0 4px 6px rgba(0,76,151,0.08);
}

/* Status items with modern design */
.critical-item {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    padding: 0.75rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 4px solid var(--danger);
}

.high-item {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    padding: 0.75rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 4px solid var(--warning);
}

.success-item {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    padding: 0.75rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 4px solid var(--success);
}

/* Tabs - Professional style */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: #f3f4f6;
    padding: 0.5rem;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    height: 3rem;
    padding: 0 1.5rem;
    background: transparent;
    border-radius: 8px;
    font-weight: 600;
    color: #6b7280;
    transition: all 0.2s;
}

.stTabs [data-baseweb="tab"]:hover {
    background: white;
    color: var(--primary);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: white;
    color: var(--primary);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Progress bars */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: white;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    font-weight: 600;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 2rem;
    font-weight: 600;
    transition: all 0.3s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,76,151,0.3);
}

/* Download buttons */
.stDownloadButton > button {
    background: white;
    color: var(--primary);
    border: 2px solid var(--primary);
    border-radius: 8px;
    font-weight: 600;
}

/* Parallax hero banner */
.parallax {
    background: linear-gradient(135deg, rgba(0,76,151,0.95) 0%, rgba(0,151,169,0.95) 100%),
                url('https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200');
    height: 200px;
    background-attachment: fixed;
    background-position: center;
    background-repeat: no-repeat;
    background-size: cover;
    border-radius: 12px;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 2.2rem;
    text-shadow: 0px 2px 12px rgba(0,0,0,0.4);
    letter-spacing: -0.5px;
}

/* Floating action button */
.fab {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 1000;
}

.fab button {
    background: var(--primary);
    color: white;
    border: none;
    padding: 14px 20px;
    border-radius: 50px;
    box-shadow: 0 4px 12px rgba(0,76,151,0.3);
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s;
}

.fab button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(0,76,151,0.4);
}

/* Data frames */
.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
}

/* Metrics */
[data-testid="stMetric"] {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Footer */
.app-footer {
    text-align: center;
    color: #6b7280;
    font-size: 0.875rem;
    padding: 2rem 0;
    margin-top: 4rem;
    border-top: 1px solid #e5e7eb;
}

/* Loading spinner color */
.stSpinner > div {
    border-top-color: var(--primary) !important;
}

/* Task 1: Fix components block color */
.components-block, .components-block * {
    color: #1b1f23 !important;
}

/* Task 2: User profile card */
.user-card {
    background: linear-gradient(135deg, #004C97 0%, #0097A9 100%);
    padding: 1.2rem;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    margin-bottom: 1rem;
}

.user-card .avatar {
    width: 54px;
    height: 54px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255,255,255,0.2);
    font-size: 1.4rem;
    font-weight: 600;
    color: #fff;
    margin: 0 auto 0.75rem auto;
    border: 3px solid rgba(255,255,255,0.3);
}

.user-card .info {
    text-align: center;
}

.user-card .name {
    font-weight: 700;
    font-size: 1.1rem;
    color: white;
    margin-bottom: 0.5rem;
}

.user-card .role-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.65rem;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    background: rgba(255,255,255,0.3);
    color: #fff;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.user-card .role-badge.role-admin {
    background: #E74C3C;
}

.user-card .role-badge.role-manager {
    background: #0097A9;
}

.user-card .role-badge.role-reviewer {
    background: #004C97;
}

.user-card .dept, .user-card .email, .user-card .login-time {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.9);
    margin: 0.25rem 0;
}

.user-card .logout-btn {
    width: 100%;
    margin-top: 0.75rem;
    padding: 0.5rem;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 8px;
    color: white;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s;
}

.user-card .logout-btn:hover {
    background: rgba(255,255,255,0.3);
}

/* Task 16: Button animations */
.ripple-btn {
    position: relative;
    overflow: hidden;
}

.ripple-btn:active {
    transform: scale(0.97);
}

.ripple-effect {
    position: absolute;
    border-radius: 50%;
    background: rgba(255,255,255,0.4);
    animation: ripple 0.6s ease-out;
    pointer-events: none;
}

@keyframes ripple {
    from {
        transform: scale(0);
        opacity: 0.8;
    }
    to {
        transform: scale(4);
        opacity: 0;
    }
}

@media (prefers-reduced-motion: reduce) {
    .ripple-btn:active {
        transform: none;
    }
    .ripple-effect {
        display: none;
    }
}
</style>

<script>
// Task 16: Button click animations with ripple effect
document.addEventListener('DOMContentLoaded', function() {
    // Add ripple effect to all Streamlit buttons
    function addRippleEffect() {
        const buttons = document.querySelectorAll('button[kind="primary"], button[kind="secondary"], .stButton button');

        buttons.forEach(button => {
            if (!button.classList.contains('ripple-initialized')) {
                button.classList.add('ripple-btn');
                button.classList.add('ripple-initialized');

                button.addEventListener('click', function(e) {
                    // Check for reduced motion preference
                    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                        return;
                    }

                    const ripple = document.createElement('span');
                    ripple.classList.add('ripple-effect');

                    const rect = button.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height);
                    const x = e.clientX - rect.left - size / 2;
                    const y = e.clientY - rect.top - size / 2;

                    ripple.style.width = ripple.style.height = size + 'px';
                    ripple.style.left = x + 'px';
                    ripple.style.top = y + 'px';

                    button.appendChild(ripple);

                    setTimeout(() => ripple.remove(), 600);
                });
            }
        });
    }

    // Initial application
    addRippleEffect();

    // Re-apply when Streamlit re-renders (using MutationObserver)
    const observer = new MutationObserver(addRippleEffect);
    observer.observe(document.body, { childList: true, subtree: true });
});

// Task 14 & 15: Dynamic scroll-responsive background
(function() {
    // Set CSS variable for background shift based on scroll
    let ticking = false;

    function updateBackgroundShift() {
        const scrollPercent = window.pageYOffset / (document.documentElement.scrollHeight - window.innerHeight);
        const shiftValue = Math.min(scrollPercent * 100, 100);
        document.documentElement.style.setProperty('--bg-shift', shiftValue);
        ticking = false;
    }

    // Throttled scroll handler
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(updateBackgroundShift);
            ticking = true;
        }
    });

    // Initial update
    updateBackgroundShift();

    // Optional: Add subtle particle animation
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const canvas = document.createElement('canvas');
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '0';
        canvas.style.opacity = '0.1';

        const container = document.querySelector('.stApp');
        if (container) {
            container.style.position = 'relative';
            container.insertBefore(canvas, container.firstChild);

            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            const particles = [];
            const particleCount = 30;

            for (let i = 0; i < particleCount; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    radius: Math.random() * 2 + 1,
                    vx: Math.random() * 0.5 - 0.25,
                    vy: Math.random() * 0.5 - 0.25
                });
            }

            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#004C97';

                particles.forEach(p => {
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                    ctx.fill();

                    p.x += p.vx;
                    p.y += p.vy;

                    if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                    if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
                });

                requestAnimationFrame(animate);
            }

            animate();

            window.addEventListener('resize', function() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            });
        }
    }
})();
</script>
""",
    unsafe_allow_html=True,
)

# Session state initialization
if "current_entity" not in st.session_state:
    st.session_state.current_entity = "AEML"
if "current_period" not in st.session_state:
    st.session_state.current_period = "Mar-24"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = None


# ==============================================
# SIDEBAR: Global Filters & Navigation
# ==============================================
with st.sidebar:
    # Adani Group logo
    st.markdown(
        """
        <div style='text-align: center; padding: 1rem 0 0.5rem 0;'>
            <svg width="120" height="40" viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
                <text x="10" y="35" font-family="Inter, sans-serif" font-size="28" font-weight="700" fill="white">ADANI</text>
                <text x="10" y="52" font-family="Inter, sans-serif" font-size="10" fill="rgba(255,255,255,0.8)">GROUP</text>
            </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h3 style='color:white;text-align:center;margin:0.5rem 0;font-weight:600;'>Project Aura</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;opacity:0.9;font-size:0.85rem;margin-bottom:1rem;'>AI-Powered Financial Review</p>",
        unsafe_allow_html=True,
    )

    # User profile and logout
    render_user_menu()
    st.markdown("---")

    # Entity & Period Selection
    st.markdown(
        "<h4 style='color:white;margin-top:1rem;'>Entity & Period</h4>", unsafe_allow_html=True
    )

    entities = ["AEML", "ABEX", "Entity003", "Entity004", "Entity005"]
    st.session_state.current_entity = st.selectbox(
        "Select Entity",
        entities,
        index=(
            entities.index(st.session_state.current_entity)
            if st.session_state.current_entity in entities
            else 0
        ),
    )

    periods = ["Mar-24", "2022-06", "Feb-24", "Jan-24", "Dec-23"]
    st.session_state.current_period = st.selectbox(
        "Select Period",
        periods,
        index=(
            periods.index(st.session_state.current_period)
            if st.session_state.current_period in periods
            else 0
        ),
    )

    st.markdown("---")

    # Quick Stats
    st.markdown("<h4 style='color:white;margin-top:1rem;'>Quick Stats</h4>", unsafe_allow_html=True)

    @st.cache_data(ttl=60)
    def load_quick_stats(entity: str, period: str):
        """Load quick stats with caching."""
        # Get all accounts for the period and filter by entity
        accounts = get_gl_accounts_by_period(period)
        accounts = [acc for acc in accounts if acc.entity == entity]

        if not accounts:
            return {"total_accounts": 0, "total_balance": 0}

        total_accounts = len(accounts)
        total_balance = sum([abs(float(acc.balance)) for acc in accounts])
        return {"total_accounts": total_accounts, "total_balance": total_balance}

    try:
        with st.spinner("Loading stats..."):
            stats = load_quick_stats(
                st.session_state.current_entity, st.session_state.current_period
            )

            if stats["total_accounts"] > 0:
                st.metric("Total Accounts", f"{stats['total_accounts']:,}")
                st.metric("Total Balance", f"₹{stats['total_balance']:,.0f}")
            else:
                st.info(
                    f"No accounts found for {st.session_state.current_entity} in {st.session_state.current_period}"
                )
    except Exception as e:
        st.error(f"Error loading stats: {e!s}")

    st.markdown("---")
    st.caption("Project Aura v1.0 | Finnovate Hackathon 2024")


# ==============================================
# PAGE ROUTING
# ==============================================
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<h4 style='color:white;margin-top:1rem;margin-bottom:1rem;'>Navigation</h4>",
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Dashboard",
        "Analytics",
        "Lookup",
        "Reports",
        "Email Management",
        "AI Assistant",
        "Settings",
    ],
    label_visibility="collapsed",
)


# ==============================================
# PAGE 1: HOME (OVERVIEW)
# ==============================================
if page == "Home":
    # Parallax hero banner
    st.markdown(
        '<div class="parallax">Project Aura – AI Financial Intelligence</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p style='font-size:1.1rem;color:#6b7280;text-align:center;margin-bottom:2rem;'>
        Enterprise-grade financial statement review platform for Adani Group's 1,000+ entity operations
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Executive Summary
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<h2>Executive Summary</h2>", unsafe_allow_html=True)
        try:
            summary = generate_executive_summary(
                st.session_state.current_entity, st.session_state.current_period
            )

            if "error" not in summary:
                # Overall Status
                status = summary.get("overall_status", "N/A")
                status_color = {
                    "Excellent": "#2ecc71",
                    "Good": "#3498db",
                    "Fair": "#f39c12",
                    "Needs Attention": "#e74c3c",
                }.get(status, "#95a5a6")

                st.markdown(
                    f"""
                <div style="background-color: {status_color}; color: white; padding: 1rem; border-radius: 0.5rem; text-align: center; font-size: 1.5rem; font-weight: bold;">
                    {status}
                </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown("<br>", unsafe_allow_html=True)

                # Key Metrics
                metrics = summary.get("key_metrics", {})
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                col_m1.metric("Total Accounts", f"{metrics.get('total_accounts', 0):,}")
                col_m2.metric("Total Balance", f"₹{metrics.get('total_balance', 0):,.0f}")
                col_m3.metric("Hygiene Score", f"{metrics.get('hygiene_score', 0):.1f}/100")
                col_m4.metric("Completion Rate", f"{metrics.get('completion_rate', 0):.1f}%")

                # Highlights
                st.markdown("#### ✅ Highlights")
                for highlight in summary.get("highlights", [])[:3]:
                    st.markdown(
                        f'<div class="success-item">✓ {highlight}</div>', unsafe_allow_html=True
                    )

                # Concerns
                st.markdown("#### ⚠️ Areas of Concern")
                for concern in summary.get("concerns", [])[:3]:
                    st.markdown(f'<div class="high-item">⚠ {concern}</div>', unsafe_allow_html=True)

                # Recommendations
                st.markdown("#### 💡 Recommendations")
                for rec in summary.get("recommendations", [])[:3]:
                    st.markdown(f"- {rec}")
            else:
                st.error(summary["error"])
        except Exception as e:
            st.error(f"Error generating summary: {e!s}")

    with col2:
        st.markdown("<h2>GL Hygiene Score</h2>", unsafe_allow_html=True)
        try:
            hygiene = calculate_gl_hygiene_score(
                st.session_state.current_entity, st.session_state.current_period
            )

            if "error" not in hygiene:
                fig = create_hygiene_gauge(hygiene["overall_score"], hygiene["components"])
                st.plotly_chart(fig, use_column_width=True)

                # Component Breakdown
                st.markdown('<div class="components-block">', unsafe_allow_html=True)
                st.markdown("**Components:**")
                for comp, score in hygiene["components"].items():
                    st.progress(
                        score / 100, text=f"{comp.replace('_', ' ').title()}: {score:.0f}/100"
                    )
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(hygiene["error"])
        except Exception as e:
            st.error(f"Error loading hygiene score: {e!s}")

    st.markdown("---")

    # Proactive Insights
    st.markdown("<h2>Proactive Insights</h2>", unsafe_allow_html=True)
    try:
        insights_list = generate_proactive_insights(
            st.session_state.current_entity, st.session_state.current_period
        )

        if insights_list:
            # 3-column card grid layout
            cols = st.columns(3)
            for idx, insight in enumerate(insights_list[:6]):  # Show up to 6 insights
                col = cols[idx % 3]

                priority = insight.get("priority", "info")
                priority_colors = {
                    "critical": "#E74C3C",
                    "high": "#F39C12",
                    "medium": "#0097A9",
                    "info": "#004C97",
                }
                color = priority_colors.get(priority, "#004C97")

                with col:
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, {color}15, {color}05);
                            border-left: 4px solid {color};
                            border-radius: 8px;
                            padding: 1rem;
                            margin-bottom: 1rem;
                            min-height: 180px;
                        ">
                            <div style="
                                background-color: {color};
                                color: white;
                                padding: 0.25rem 0.5rem;
                                border-radius: 4px;
                                font-size: 0.7rem;
                                font-weight: 600;
                                text-transform: uppercase;
                                display: inline-block;
                                margin-bottom: 0.5rem;
                            ">{priority}</div>
                            <h4 style="color: #1b1f23; margin: 0.5rem 0; font-size: 0.95rem;">{insight.get('title', 'Insight')}</h4>
                            <p style="color: #4b5563; font-size: 0.85rem; margin-bottom: 0.5rem;">{insight.get('message', 'N/A')}</p>
                            <div style="
                                color: #6b7280;
                                font-size: 0.75rem;
                                font-style: italic;
                                border-top: 1px solid #e5e7eb;
                                padding-top: 0.5rem;
                                margin-top: 0.5rem;
                            ">💡 {insight.get('action', 'No action specified')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            # Empty state
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, #004C9715, #004C9705);
                    border: 2px dashed #004C97;
                    border-radius: 12px;
                    padding: 2rem;
                    text-align: center;
                    margin: 1rem 0;
                ">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">📊</div>
                    <h3 style="color: #004C97; margin-bottom: 0.5rem;">No Insights Available</h3>
                    <p style="color: #6b7280;">Insights will appear here once sufficient data is available for this entity and period.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Error loading insights: {e!s}")


# ==============================================
# PAGE 2: DASHBOARD (5 COMPREHENSIVE DASHBOARDS)
# ==============================================
elif page == "Dashboard":
    st.markdown('<div class="main-header">Interactive Dashboards</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:1.05rem;color:#6b7280;margin-bottom:1.5rem;'>Comprehensive analytics with drill-down capabilities and real-time insights</p>",
        unsafe_allow_html=True,
    )

    # Import dashboard module
    from src.dashboards import apply_global_filters, render_dashboard

    # Apply global filters and get filter dict
    filters = apply_global_filters()

    st.markdown("---")

    # Create 5 tabs for the dashboards
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Overview",
            "Financial Analysis",
            "Review Status",
            "Quality & Hygiene",
            "Risk & Anomalies",
        ]
    )

    with tab1:
        # Overview Dashboard
        try:
            render_dashboard("overview", filters)
        except Exception as e:
            st.error(f"Error loading Overview Dashboard: {e!s}")
            st.exception(e)

    with tab2:
        # Financial Analysis Dashboard
        try:
            render_dashboard("financial", filters)
        except Exception as e:
            st.error(f"Error loading Financial Dashboard: {e!s}")
            st.exception(e)

    with tab3:
        # Review Status Dashboard
        try:
            render_dashboard("review", filters)
        except Exception as e:
            st.error(f"Error loading Review Dashboard: {e!s}")
            st.exception(e)

    with tab4:
        # Quality & Hygiene Dashboard
        try:
            render_dashboard("quality", filters)
        except Exception as e:
            st.error(f"Error loading Quality Dashboard: {e!s}")
            st.exception(e)

    with tab5:
        # Risk & Anomaly Dashboard
        try:
            render_dashboard("risk", filters)
        except Exception as e:
            st.error(f"Error loading Risk Dashboard: {e!s}")
            st.exception(e)


# ==============================================
# PAGE 3: ANALYTICS (INSIGHTS & DRILL-DOWN)
# ==============================================
elif page == "Analytics":
    st.markdown('<div class="main-header">Deep Dive Analytics</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(
        ["Drill-Down Analysis", "Multi-Period Comparison", "Pending Items Report"]
    )

    with tab1:
        st.subheader("Drill-Down Analysis")

        @st.cache_data(ttl=300)
        def get_dimension_values(entity: str, period: str, dimension: str):
            """Get unique values for a dimension with caching."""
            accounts = get_gl_accounts_by_period(period, entity)
            values = set()
            for acc in accounts:
                val = getattr(acc, dimension, None)
                if val:
                    values.add(str(val))
            return sorted(list(values))

        col1, col2 = st.columns(2)
        with col1:
            dimension = st.selectbox(
                "Dimension",
                ["category", "department", "criticality", "review_status"],
                help="Select dimension to drill down",
            )
        with col2:
            # Autocomplete with actual values
            try:
                available_values = get_dimension_values(
                    st.session_state.current_entity,
                    st.session_state.current_period,
                    f"account_{dimension}" if dimension == "category" else dimension,
                )
                value = st.selectbox(
                    "Filter Value",
                    options=[""] + available_values,
                    help="Select or enter a value to filter",
                )
            except:
                value = st.text_input("Filter Value (e.g., Assets, Finance, High)", "")

        if st.button("🔍 Analyze", type="primary"):
            if value:
                try:
                    report = generate_drill_down_report(
                        st.session_state.current_entity,
                        st.session_state.current_period,
                        dimension,
                        value,
                    )

                    if "error" not in report:
                        # Metrics
                        st.markdown("### Summary Metrics")
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        metrics = report.get("summary_metrics", {})
                        col_m1.metric("Total Accounts", f"{metrics.get('total_accounts', 0):,}")
                        col_m2.metric("Total Balance", f"₹{metrics.get('total_balance', 0):,.0f}")
                        col_m3.metric("Avg Balance", f"₹{metrics.get('avg_balance', 0):,.0f}")
                        col_m4.metric("Completion %", f"{metrics.get('completion_rate', 0):.1f}%")

                        # Status Distribution
                        st.markdown("### Status Distribution")
                        status_dist = report.get("status_distribution", {})
                        if status_dist:
                            cols = st.columns(len(status_dist))
                            for idx, (status, count) in enumerate(status_dist.items()):
                                cols[idx].metric(status, count)

                        # Top Accounts
                        st.markdown("### Top Accounts by Balance")
                        if "top_accounts" in report:
                            st.dataframe(
                                pd.DataFrame(report["top_accounts"]), use_column_width=True
                            )
                    else:
                        st.error(report["error"])
                except Exception as e:
                    st.error(f"Error: {e!s}")
            else:
                st.warning("Please enter a filter value")

    with tab2:
        st.subheader("Multi-Period Trend Analysis")

        @st.cache_data(ttl=300)
        def normalize_and_compare_periods(entity: str, periods: list):
            """Compare periods with normalization."""
            # Normalize period formats
            normalized_periods = []
            for period in periods:
                if "-" in period and len(period) == 6:  # Format: Mar-24
                    month_map = {
                        "Jan": "01",
                        "Feb": "02",
                        "Mar": "03",
                        "Apr": "04",
                        "May": "05",
                        "Jun": "06",
                        "Jul": "07",
                        "Aug": "08",
                        "Sep": "09",
                        "Oct": "10",
                        "Nov": "11",
                        "Dec": "12",
                    }
                    month_abbr, year = period.split("-")
                    if month_abbr in month_map:
                        normalized_periods.append(f"20{year}-{month_map[month_abbr]}")
                else:
                    normalized_periods.append(period)

            return compare_multi_period(entity, normalized_periods)

        selected_periods = st.multiselect(
            "Select Periods to Compare",
            ["2024-03", "2024-02", "2024-01", "2023-12", "2023-11", "Mar-24", "Feb-24", "Jan-24"],
            default=["2024-03", "2024-02", "2024-01"],
            help="Supports both YYYY-MM and Mon-YY formats",
        )

        if st.button("📊 Compare Periods", type="primary"):
            if len(selected_periods) >= 2:
                try:
                    comparison = normalize_and_compare_periods(
                        st.session_state.current_entity, selected_periods
                    )

                    if "error" not in comparison:
                        # Trend Charts
                        st.markdown("### Trend Analysis")

                        trend_data = {
                            "Total Balance": [
                                p["total_balance"] for p in comparison.get("period_summaries", [])
                            ],
                            "Hygiene Score": [
                                p["hygiene_score"] for p in comparison.get("period_summaries", [])
                            ],
                            "Completion Rate": [
                                p["completion_rate"] for p in comparison.get("period_summaries", [])
                            ],
                        }

                        fig = create_trend_line_chart(trend_data, selected_periods)
                        st.plotly_chart(fig, use_column_width=True)

                        # Period Summaries Table
                        st.markdown("### Period-wise Summary")
                        st.dataframe(
                            pd.DataFrame(comparison.get("period_summaries", [])),
                            use_column_width=True,
                        )

                        # Trends
                        st.markdown("### Identified Trends")
                        trends = comparison.get("trends", {})
                        for metric, trend_info in trends.items():
                            direction = trend_info.get("direction", "N/A")
                            icon = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(
                                direction, "❓"
                            )
                            st.markdown(
                                f"**{metric}:** {icon} {direction.title()} ({trend_info.get('change_pct', 0):.1f}%)"
                            )
                    else:
                        st.error(comparison["error"])
                except Exception as e:
                    st.error(f"Error: {e!s}")
            else:
                st.warning("Please select at least 2 periods")

    with tab3:
        st.subheader("Pending Items Report")

        @st.cache_data(ttl=120)
        def get_cached_pending_items(entity: str, period: str):
            """Get pending items with caching."""
            return get_pending_items_report(entity, period)

        try:
            with st.spinner("Loading pending items..."):
                pending = get_cached_pending_items(
                    st.session_state.current_entity, st.session_state.current_period
                )

            if "error" not in pending:
                # Summary with export button
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Pending Reviews", f"{pending.get('pending_reviews_count', 0):,}")
                col2.metric("Missing Docs", f"{pending.get('missing_docs_count', 0):,}")
                col3.metric("Flagged Items", f"{pending.get('flagged_items_count', 0):,}")

                # CSV Export button
                with col4:
                    all_items = []
                    all_items.extend(pending.get("pending_reviews", []))
                    all_items.extend(pending.get("missing_docs", []))
                    all_items.extend(pending.get("flagged_items", []))

                    if all_items:
                        import pandas as pd

                        df_export = pd.DataFrame(all_items)
                        csv = df_export.to_csv(index=False)
                        st.download_button(
                            "📥 Export CSV",
                            csv,
                            f"pending_items_{st.session_state.current_entity}_{st.session_state.current_period}.csv",
                            "text/csv",
                            use_container_width=True,
                        )

                # Pending Reviews
                st.markdown("### 📝 Pending Reviews")
                if pending.get("pending_reviews"):
                    st.dataframe(pd.DataFrame(pending["pending_reviews"]), use_column_width=True)
                else:
                    st.success("No pending reviews!")

                # Missing Documentation
                st.markdown("### 📄 Missing Documentation")
                if pending.get("missing_docs"):
                    st.dataframe(pd.DataFrame(pending["missing_docs"]), use_column_width=True)
                else:
                    st.success("All documentation complete!")

                # Flagged Items
                st.markdown("### 🚩 Flagged Items")
                if pending.get("flagged_items"):
                    st.dataframe(pd.DataFrame(pending["flagged_items"]), use_column_width=True)
                else:
                    st.success("No flagged items!")
            else:
                st.error(pending["error"])
        except Exception as e:
            st.error(f"Error: {e!s}")


# ==============================================
# PAGE 4: LOOKUP (ACCOUNT SEARCH)
# ==============================================
elif page == "Lookup":
    st.markdown('<div class="main-header">GL Account Lookup</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:1.05rem;color:#6b7280;margin-bottom:1.5rem;'>Search and explore GL accounts with advanced filters and fuzzy matching</p>",
        unsafe_allow_html=True,
    )

    # Sidebar filters
    with st.sidebar:
        st.markdown("---")
        st.markdown("<h4 style='color:white;'>🔍 Advanced Filters</h4>", unsafe_allow_html=True)

        filter_category = st.multiselect(
            "Category",
            ["Assets", "Liabilities", "Equity", "Revenue", "Expenses"],
            help="Filter by account category",
        )

        filter_department = st.multiselect(
            "Department",
            ["Finance", "Operations", "Sales", "IT", "HR", "Treasury", "Accounting"],
            help="Filter by department",
        )

        filter_criticality = st.multiselect(
            "Criticality", ["High", "Medium", "Low"], help="Filter by criticality level"
        )

        filter_status = st.multiselect(
            "Review Status", ["reviewed", "pending", "flagged"], help="Filter by review status"
        )

        if st.button("�️ Clear Filters", use_container_width=True):
            st.rerun()

    # Search bar with fuzzy matching
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input(
            "🔍 Search by GL Code or Description",
            placeholder="e.g., 100000, Cash, Bank (supports fuzzy matching)",
            label_visibility="collapsed",
        )
    with col2:
        use_fuzzy = st.checkbox("Fuzzy Search", value=True, help="Enable fuzzy matching for typos")

    if search_query:
        try:
            from rapidfuzz import fuzz, process

            accounts = get_gl_accounts_by_period(
                st.session_state.current_period, st.session_state.current_entity
            )

            # Apply filters
            if filter_category:
                accounts = [
                    a for a in accounts if getattr(a, "account_category", None) in filter_category
                ]
            if filter_department:
                accounts = [
                    a for a in accounts if getattr(a, "department", None) in filter_department
                ]
            if filter_criticality:
                accounts = [
                    a for a in accounts if getattr(a, "criticality", None) in filter_criticality
                ]
            if filter_status:
                accounts = [
                    a for a in accounts if getattr(a, "review_status", None) in filter_status
                ]

            # Search logic
            if use_fuzzy:
                # Fuzzy matching
                choices = {f"{acc.account_code} {acc.account_name}": acc for acc in accounts}
                matches = process.extract(
                    search_query, choices.keys(), scorer=fuzz.WRatio, limit=20
                )
                filtered = [
                    choices[match[0]] for match in matches if match[1] > 60
                ]  # 60% threshold
            else:
                # Exact substring match
                filtered = [
                    acc
                    for acc in accounts
                    if search_query.lower() in acc.account_code.lower()
                    or search_query.lower() in acc.account_name.lower()
                ]

            # Results header with export
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**Found {len(filtered)} account(s)**")
            with col2:
                if st.button("💾 Save Search", use_container_width=True):
                    from src.db.mongodb import get_mongo_database

                    db = get_mongo_database()
                    db["saved_searches"].insert_one(
                        {
                            "query": search_query,
                            "filters": {
                                "category": filter_category,
                                "department": filter_department,
                                "criticality": filter_criticality,
                                "status": filter_status,
                            },
                            "user": st.session_state.get("user_email", "unknown"),
                            "timestamp": datetime.now(),
                        }
                    )
                    st.success("✓ Search saved!")
            with col3:
                if filtered:
                    # Export to CSV
                    import pandas as pd

                    df = pd.DataFrame(
                        [
                            {
                                "GL Code": a.account_code,
                                "Description": a.account_name,
                                "Category": getattr(a, "account_category", "N/A"),
                                "Department": getattr(a, "department", "N/A"),
                                "Balance": float(getattr(a, "balance", 0)),
                                "Status": getattr(a, "review_status", "N/A"),
                                "Criticality": getattr(a, "criticality", "N/A"),
                            }
                            for a in filtered
                        ]
                    )
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Export CSV",
                        csv,
                        "gl_accounts.csv",
                        "text/csv",
                        use_container_width=True,
                    )

            st.markdown("---")

            # Modern card-based display
            for acc in filtered[:20]:  # Show top 20 results
                # Status badge colors
                status_colors = {"reviewed": "#2ECC71", "pending": "#F39C12", "flagged": "#E74C3C"}
                status_color = status_colors.get(
                    getattr(acc, "review_status", "pending"), "#95A5A6"
                )

                # Criticality colors
                crit_colors = {"High": "#E74C3C", "Medium": "#F39C12", "Low": "#3498DB"}
                crit_color = crit_colors.get(getattr(acc, "criticality", "Medium"), "#95A5A6")

                # Balance indicator
                balance = float(getattr(acc, "balance", 0))
                balance_icon = "+" if balance >= 0 else "-"
                balance_color = "#2ECC71" if balance >= 0 else "#E74C3C"

                # Highlight search terms
                code_display = acc.account_code
                name_display = acc.account_name
                if search_query and not use_fuzzy:
                    code_display = code_display.replace(
                        search_query,
                        f"<mark style='background-color:#FFF59D;'>{search_query}</mark>",
                    )
                    name_display = name_display.replace(
                        search_query,
                        f"<mark style='background-color:#FFF59D;'>{search_query}</mark>",
                    )

                st.markdown(
                    f"""
                    <div style="
                        background: white;
                        border-left: 5px solid {status_color};
                        border-radius: 10px;
                        padding: 1.25rem;
                        margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                        transition: all 0.3s ease;
                    " onmouseover="this.style.boxShadow='0 4px 16px rgba(0,0,0,0.12)'" onmouseout="this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                            <div>
                                <span style="
                                    background-color: #004C97;
                                    color: white;
                                    padding: 0.25rem 0.75rem;
                                    border-radius: 6px;
                                    font-size: 0.9rem;
                                    font-weight: 600;
                                    font-family: 'Courier New', monospace;
                                ">{code_display}</span>
                                <h3 style="color: #1b1f23; margin: 0.5rem 0 0 0; font-size: 1.1rem;">{name_display}</h3>
                            </div>
                            <div style="text-align: right;">
                                <span style="
                                    background-color: {status_color};
                                    color: white;
                                    padding: 0.25rem 0.75rem;
                                    border-radius: 20px;
                                    font-size: 0.75rem;
                                    font-weight: 600;
                                    text-transform: uppercase;
                                ">{getattr(acc, 'review_status', 'pending')}</span>
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
                            <div>
                                <div style="color: #6b7280; font-size: 0.8rem; margin-bottom: 0.25rem;">Category</div>
                                <span style="
                                    background-color: #0097A915;
                                    color: #0097A9;
                                    padding: 0.25rem 0.5rem;
                                    border-radius: 4px;
                                    font-size: 0.85rem;
                                    font-weight: 500;
                                ">{getattr(acc, 'account_category', 'N/A')}</span>
                            </div>

                            <div>
                                <div style="color: #6b7280; font-size: 0.8rem; margin-bottom: 0.25rem;">Department</div>
                                <span style="
                                    background-color: #004C9715;
                                    color: #004C97;
                                    padding: 0.25rem 0.5rem;
                                    border-radius: 4px;
                                    font-size: 0.85rem;
                                    font-weight: 500;
                                ">{getattr(acc, 'department', 'N/A')}</span>
                            </div>

                            <div>
                                <div style="color: #6b7280; font-size: 0.8rem; margin-bottom: 0.25rem;">Criticality</div>
                                <span style="
                                    background-color: {crit_color}15;
                                    color: {crit_color};
                                    padding: 0.25rem 0.5rem;
                                    border-radius: 4px;
                                    font-size: 0.85rem;
                                    font-weight: 600;
                                ">{"★ " if getattr(acc, 'criticality', '') == 'High' else ""}{getattr(acc, 'criticality', 'N/A')}</span>
                            </div>

                            <div>
                                <div style="color: #6b7280; font-size: 0.8rem; margin-bottom: 0.25rem;">Balance</div>
                                <span style="
                                    color: {balance_color};
                                    font-size: 1.1rem;
                                    font-weight: 700;
                                ">{balance_icon} ₹{abs(balance):,.2f}</span>
                            </div>
                        </div>

                        <div style="
                            margin-top: 1rem;
                            padding-top: 1rem;
                            border-top: 1px solid #e5e7eb;
                            display: grid;
                            grid-template-columns: repeat(2, 1fr);
                            gap: 0.5rem;
                            font-size: 0.85rem;
                            color: #6b7280;
                        ">
                            <div><strong>Debit Period:</strong> ₹{float(getattr(acc, 'debit_period', 0) or 0):,.2f}</div>
                            <div><strong>Credit Period:</strong> ₹{float(getattr(acc, 'credit_period', 0) or 0):,.2f}</div>
                            <div><strong>Reviewed By:</strong> {getattr(acc, 'reviewed_by', 'N/A')}</div>
                            <div><strong>Reviewed At:</strong> {str(getattr(acc, 'reviewed_at', 'N/A'))[:16] if getattr(acc, 'reviewed_at', None) else 'N/A'}</div>
                        </div>

                        {f'<div style="margin-top: 0.75rem; padding: 0.75rem; background-color: #f9fafb; border-radius: 6px; font-size: 0.85rem; color: #4b5563;"><strong>Comments:</strong> {getattr(acc, "comments", "")}</div>' if getattr(acc, 'comments', None) else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if len(filtered) > 20:
                st.info(
                    f"Showing top 20 of {len(filtered)} results. Refine your search to see more."
                )

        except Exception as e:
            st.error(f"Error: {e!s}")
    else:
        st.info("👆 Enter a search query to find GL accounts")


# ==============================================
# PAGE 5: REPORTS (EXPORT & GENERATION)
# ==============================================
elif page == "Reports":
    st.markdown(
        '<div class="main-header">📋 Report Configuration Wizard</div>', unsafe_allow_html=True
    )
    st.markdown("Create custom reports with an intuitive 4-step wizard")

    st.markdown("---")

    # Import report wizard
    from src.reports_ui import render_report_wizard

    # Render the wizard
    render_report_wizard()

    st.markdown("---")

    # Report History (list previously generated reports)
    st.subheader("📚 Report History")

    reports_dir = Path("data/reports")
    if reports_dir.exists():
        report_files = sorted(
            reports_dir.glob("*.*"), key=lambda x: x.stat().st_mtime, reverse=True
        )

        if report_files:
            # Group by report type
            grouped_reports = {}
            for file in report_files[:20]:  # Last 20 reports
                # Extract report type from filename
                parts = file.stem.split("_")
                if len(parts) >= 2:
                    report_key = parts[0]
                    if report_key not in grouped_reports:
                        grouped_reports[report_key] = []
                    grouped_reports[report_key].append(file)

            # Display in tabs
            if grouped_reports:
                tabs = st.tabs([f"{k.title()} ({len(v)})" for k, v in grouped_reports.items()])

                for tab, (report_key, files) in zip(tabs, grouped_reports.items(), strict=False):
                    with tab:
                        for file in files[:10]:  # Show 10 per type
                            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                            with col1:
                                st.text(file.name)
                            with col2:
                                st.caption(f"{file.stat().st_size / 1024:.1f} KB")
                            with col3:
                                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                                st.caption(mtime.strftime("%Y-%m-%d %H:%M"))
                            with col4:
                                with open(file, "rb") as f:
                                    st.download_button(
                                        label="�",
                                        data=f,
                                        file_name=file.name,
                                        key=f"history_{file.name}",
                                    )
        else:
            st.info("No reports generated yet. Generate your first report above!")
    else:
        st.info(
            "Reports directory not found. It will be created when you generate your first report."
        )


# ==============================================
# PAGE 6: EMAIL MANAGEMENT
# ==============================================
elif page == "Email Management":
    from src.dashboards.email_management_page import render_email_management_page

    render_email_management_page()


# ==============================================
# PAGE 7: AI ASSISTANT (CHAT INTERFACE)
# ==============================================
elif page == "AI Assistant":
    # Use new RAG-enhanced AI Assistant page
    from src.dashboards.ai_assistant_page import render_ai_assistant_page

    render_ai_assistant_page()


# ==============================================
# PAGE 8: SETTINGS (CONFIGURATION)
# ==============================================
elif page == "Settings":
    st.markdown('<div class="main-header">Settings & Configuration</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Database", "Notifications", "Data Upload", "About"])

    with tab1:
        st.subheader("🗄️ Database Connection Status & Metrics")

        @st.cache_data(ttl=60)
        def get_database_metrics():
            """Fetch comprehensive database metrics."""
            import time

            from sqlalchemy import text

            metrics = {}

            # PostgreSQL metrics
            try:
                start = time.time()
                session = get_postgres_session()

                # Version
                version_result = session.execute(text("SELECT version()")).scalar()
                metrics["pg_version"] = (
                    version_result.split(",")[0] if version_result else "Unknown"
                )

                # Row counts
                users_count = session.execute(text("SELECT COUNT(*) FROM users")).scalar()
                gl_accounts_count = session.execute(
                    text("SELECT COUNT(*) FROM gl_accounts")
                ).scalar()

                # Database size
                db_size = session.execute(
                    text("SELECT pg_size_pretty(pg_database_size('finnovate'))")
                ).scalar()

                session.close()
                pg_latency = (time.time() - start) * 1000  # ms

                metrics["postgresql"] = {
                    "status": "connected",
                    "version": metrics["pg_version"],
                    "users": users_count,
                    "gl_accounts": gl_accounts_count,
                    "db_size": db_size,
                    "latency_ms": round(pg_latency, 2),
                }
            except Exception as e:
                metrics["postgresql"] = {"status": "error", "message": str(e)}

            # MongoDB metrics
            try:
                start = time.time()
                db = get_mongo_database()

                # Server status
                server_status = db.client.server_info()

                # Collection counts
                audit_count = get_audit_trail_collection().count_documents({})
                sessions_count = get_review_sessions_collection().count_documents({})
                feedback_count = get_user_feedback_collection().count_documents({})
                validation_count = get_validation_results_collection().count_documents({})
                metadata_count = get_gl_metadata_collection().count_documents({})

                # Database stats
                db_stats = db.command("dbStats")

                mongo_latency = (time.time() - start) * 1000  # ms

                metrics["mongodb"] = {
                    "status": "connected",
                    "version": server_status.get("version", "Unknown"),
                    "audit_trail": audit_count,
                    "review_sessions": sessions_count,
                    "user_feedback": feedback_count,
                    "validation_results": validation_count,
                    "gl_metadata": metadata_count,
                    "db_size": f"{db_stats.get('dataSize', 0) / (1024*1024):.2f} MB",
                    "latency_ms": round(mongo_latency, 2),
                }
            except Exception as e:
                metrics["mongodb"] = {"status": "error", "message": str(e)}

            # ChromaDB metrics
            try:
                start = time.time()
                import chromadb

                # Try to connect to ChromaDB
                chroma_client = chromadb.PersistentClient(path="data/vectors")
                collections = chroma_client.list_collections()

                chroma_latency = (time.time() - start) * 1000  # ms

                metrics["chromadb"] = {
                    "status": "connected",
                    "collections": len(collections),
                    "collection_names": [c.name for c in collections],
                    "latency_ms": round(chroma_latency, 2),
                }
            except Exception as e:
                metrics["chromadb"] = {"status": "error", "message": str(e)}

            return metrics

        try:
            with st.spinner("Fetching database metrics..."):
                metrics = get_database_metrics()

            # 3-column layout for database cards
            col1, col2, col3 = st.columns(3)

            # PostgreSQL Card
            with col1:
                pg = metrics.get("postgresql", {})
                status_icon = "✅" if pg.get("status") == "connected" else "❌"
                status_color = "#2ECC71" if pg.get("status") == "connected" else "#E74C3C"

                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, #004C9715, #004C9705);
                        border-left: 4px solid {status_color};
                        border-radius: 10px;
                        padding: 1.25rem;
                        margin-bottom: 1rem;
                    ">
                        <h3 style="color: #004C97; margin: 0 0 1rem 0;">
                            {status_icon} PostgreSQL
                        </h3>
                        <div style="font-size: 0.9rem; color: #4b5563; line-height: 1.8;">
                            <strong>Version:</strong> {pg.get('version', 'N/A')[:30]}<br>
                            <strong>Users:</strong> {pg.get('users', 0):,}<br>
                            <strong>GL Accounts:</strong> {pg.get('gl_accounts', 0):,}<br>
                            <strong>Database Size:</strong> {pg.get('db_size', 'N/A')}<br>
                            <strong>Latency:</strong> <span style="color: {'#2ECC71' if pg.get('latency_ms', 999) < 100 else '#F39C12'};">{pg.get('latency_ms', 'N/A')} ms</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # MongoDB Card
            with col2:
                mongo = metrics.get("mongodb", {})
                status_icon = "✅" if mongo.get("status") == "connected" else "❌"
                status_color = "#2ECC71" if mongo.get("status") == "connected" else "#E74C3C"

                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, #0097A915, #0097A905);
                        border-left: 4px solid {status_color};
                        border-radius: 10px;
                        padding: 1.25rem;
                        margin-bottom: 1rem;
                    ">
                        <h3 style="color: #0097A9; margin: 0 0 1rem 0;">
                            {status_icon} MongoDB
                        </h3>
                        <div style="font-size: 0.9rem; color: #4b5563; line-height: 1.8;">
                            <strong>Version:</strong> {mongo.get('version', 'N/A')}<br>
                            <strong>Audit Trail:</strong> {mongo.get('audit_trail', 0):,}<br>
                            <strong>Review Sessions:</strong> {mongo.get('review_sessions', 0):,}<br>
                            <strong>User Feedback:</strong> {mongo.get('user_feedback', 0):,}<br>
                            <strong>Database Size:</strong> {mongo.get('db_size', 'N/A')}<br>
                            <strong>Latency:</strong> <span style="color: {'#2ECC71' if mongo.get('latency_ms', 999) < 100 else '#F39C12'};">{mongo.get('latency_ms', 'N/A')} ms</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ChromaDB Card
            with col3:
                chroma = metrics.get("chromadb", {})
                status_icon = "✅" if chroma.get("status") == "connected" else "❌"
                status_color = "#2ECC71" if chroma.get("status") == "connected" else "#E74C3C"

                collections_list = (
                    "<br>".join([f"• {name}" for name in chroma.get("collection_names", [])])
                    or "None"
                )

                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, #2ECC7115, #2ECC7105);
                        border-left: 4px solid {status_color};
                        border-radius: 10px;
                        padding: 1.25rem;
                        margin-bottom: 1rem;
                    ">
                        <h3 style="color: #2ECC71; margin: 0 0 1rem 0;">
                            {status_icon} ChromaDB
                        </h3>
                        <div style="font-size: 0.9rem; color: #4b5563; line-height: 1.8;">
                            <strong>Collections:</strong> {chroma.get('collections', 0)}<br>
                            <strong>Names:</strong><br>
                            <div style="margin-left: 1rem; font-size: 0.85rem; color: #6b7280;">
                                {collections_list}
                            </div>
                            <strong>Latency:</strong> <span style="color: {'#2ECC71' if chroma.get('latency_ms', 999) < 100 else '#F39C12'};">{chroma.get('latency_ms', 'N/A')} ms</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Error messages if any
            for db_name, db_data in metrics.items():
                if db_data.get("status") == "error":
                    st.error(
                        f"**{db_name.upper()} Error:** {db_data.get('message', 'Unknown error')}"
                    )

        except Exception as e:
            st.error(f"Error fetching database metrics: {e!s}")

    with tab2:
        st.subheader("🔔 Notification Preferences")
        st.markdown("Configure alerts and notifications for your account")

        # Initialize session state for preferences
        if "notification_prefs" not in st.session_state:
            st.session_state.notification_prefs = {
                "critical_items": {"enabled": True, "frequency": "instant", "threshold": 100000},
                "daily_summary": {"enabled": False, "frequency": "daily", "threshold": 0},
                "anomaly_alerts": {"enabled": True, "frequency": "instant", "threshold": 2.0},
                "sla_warnings": {"enabled": True, "frequency": "4hours", "threshold": 24},
            }

        # 2x2 grid of notification cards
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)

        # Card 1: Critical Items
        with row1_col1:
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, #E74C3C15, #E74C3C05);
                    border-left: 4px solid #E74C3C;
                    border-radius: 10px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                ">
                    <h4 style="color: #E74C3C; margin: 0 0 0.5rem 0;">🚨 Critical Items</h4>
                    <p style="font-size: 0.85rem; color: #6b7280; margin-bottom: 1rem;">
                        Get notified when high-priority items require attention
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            crit_enabled = st.checkbox(
                "Enable notifications",
                value=st.session_state.notification_prefs["critical_items"]["enabled"],
                key="crit_enabled",
            )

            crit_freq = st.selectbox(
                "Frequency",
                ["instant", "hourly", "daily"],
                index=["instant", "hourly", "daily"].index(
                    st.session_state.notification_prefs["critical_items"]["frequency"]
                ),
                key="crit_freq",
                disabled=not crit_enabled,
            )

            crit_threshold = st.slider(
                "Balance threshold (₹)",
                min_value=0,
                max_value=1000000,
                value=st.session_state.notification_prefs["critical_items"]["threshold"],
                step=50000,
                key="crit_threshold",
                disabled=not crit_enabled,
            )

            st.session_state.notification_prefs["critical_items"] = {
                "enabled": crit_enabled,
                "frequency": crit_freq,
                "threshold": crit_threshold,
            }

        # Card 2: Daily Summary
        with row1_col2:
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, #3498DB15, #3498DB05);
                    border-left: 4px solid #3498DB;
                    border-radius: 10px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                ">
                    <h4 style="color: #3498DB; margin: 0 0 0.5rem 0;">📊 Daily Summary</h4>
                    <p style="font-size: 0.85rem; color: #6b7280; margin-bottom: 1rem;">
                        Receive daily digest of all review activities
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            summary_enabled = st.checkbox(
                "Enable notifications",
                value=st.session_state.notification_prefs["daily_summary"]["enabled"],
                key="summary_enabled",
            )

            summary_freq = st.selectbox(
                "Frequency",
                ["daily", "weekly", "monthly"],
                index=["daily", "weekly", "monthly"].index(
                    st.session_state.notification_prefs["daily_summary"]["frequency"]
                ),
                key="summary_freq",
                disabled=not summary_enabled,
            )

            summary_time = st.time_input(
                "Delivery time",
                value=datetime.strptime("09:00", "%H:%M").time(),
                key="summary_time",
                disabled=not summary_enabled,
            )

            st.session_state.notification_prefs["daily_summary"] = {
                "enabled": summary_enabled,
                "frequency": summary_freq,
                "threshold": 0,
            }

        # Card 3: Anomaly Alerts
        with row2_col1:
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, #F39C1215, #F39C1205);
                    border-left: 4px solid #F39C12;
                    border-radius: 10px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                ">
                    <h4 style="color: #F39C12; margin: 0 0 0.5rem 0;">⚠️ Anomaly Alerts</h4>
                    <p style="font-size: 0.85rem; color: #6b7280; margin-bottom: 1rem;">
                        ML-detected unusual patterns and outliers
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            anomaly_enabled = st.checkbox(
                "Enable notifications",
                value=st.session_state.notification_prefs["anomaly_alerts"]["enabled"],
                key="anomaly_enabled",
            )

            anomaly_freq = st.selectbox(
                "Frequency",
                ["instant", "hourly", "4hours", "daily"],
                index=["instant", "hourly", "4hours", "daily"].index(
                    st.session_state.notification_prefs["anomaly_alerts"]["frequency"]
                ),
                key="anomaly_freq",
                disabled=not anomaly_enabled,
            )

            anomaly_threshold = st.slider(
                "Z-score threshold",
                min_value=1.0,
                max_value=5.0,
                value=st.session_state.notification_prefs["anomaly_alerts"]["threshold"],
                step=0.5,
                key="anomaly_threshold",
                disabled=not anomaly_enabled,
                help="Higher values = fewer alerts (only extreme outliers)",
            )

            st.session_state.notification_prefs["anomaly_alerts"] = {
                "enabled": anomaly_enabled,
                "frequency": anomaly_freq,
                "threshold": anomaly_threshold,
            }

        # Card 4: SLA Warnings
        with row2_col2:
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, #9B59B615, #9B59B605);
                    border-left: 4px solid #9B59B6;
                    border-radius: 10px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                ">
                    <h4 style="color: #9B59B6; margin: 0 0 0.5rem 0;">⏰ SLA Warnings</h4>
                    <p style="font-size: 0.85rem; color: #6b7280; margin-bottom: 1rem;">
                        Alerts for approaching review deadlines
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            sla_enabled = st.checkbox(
                "Enable notifications",
                value=st.session_state.notification_prefs["sla_warnings"]["enabled"],
                key="sla_enabled",
            )

            sla_freq = st.selectbox(
                "Frequency",
                ["4hours", "8hours", "daily"],
                index=["4hours", "8hours", "daily"].index(
                    st.session_state.notification_prefs["sla_warnings"]["frequency"]
                ),
                key="sla_freq",
                disabled=not sla_enabled,
            )

            sla_threshold = st.slider(
                "Warning threshold (hours before deadline)",
                min_value=4,
                max_value=72,
                value=st.session_state.notification_prefs["sla_warnings"]["threshold"],
                step=4,
                key="sla_threshold",
                disabled=not sla_enabled,
            )

            st.session_state.notification_prefs["sla_warnings"] = {
                "enabled": sla_enabled,
                "frequency": sla_freq,
                "threshold": sla_threshold,
            }

        st.markdown("---")

        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("💾 Save Preferences", use_container_width=True):
                try:
                    # Save to MongoDB
                    db = get_mongo_database()
                    db["notification_preferences"].update_one(
                        {"user_email": st.session_state.get("user_email", "unknown")},
                        {
                            "$set": {
                                "preferences": st.session_state.notification_prefs,
                                "updated_at": datetime.now(),
                            }
                        },
                        upsert=True,
                    )
                    st.success("✓ Preferences saved successfully!")
                except Exception as e:
                    st.error(f"Error saving preferences: {e!s}")

        with col2:
            if st.button("🧪 Test Notification", use_container_width=True):
                st.info(
                    """
                    **Test Notification Preview**

                    🚨 **Critical Item Alert**

                    Account 100000 (Cash and Cash Equivalents) requires immediate review.
                    - Balance: ₹2,450,000
                    - Status: Flagged
                    - Assigned to: You

                    [View Account] [Mark as Reviewed]
                    """
                )

        with col3:
            st.caption(
                "💡 Tip: Enable instant notifications for critical items to stay on top of urgent reviews"
            )

    with tab3:
        # Data Upload tab
        from src.upload_manager import render_upload_section

        render_upload_section()

    with tab4:
        st.subheader("About Project Aura")
        st.markdown(
            """
        **Project Aura** is an AI-powered financial statement review agent built for the Adani Group's
        1,000+ entity finance operations.

        **Key Features:**
        - ✅ Automated GL account validation
        - 📊 Real-time analytics and insights
        - 🤖 Natural language query interface
        - 📈 Multi-period trend analysis
        - 🎯 Anomaly detection using ML
        - 📄 Comprehensive reporting

        **Technology Stack:**
        - Python 3.11+
        - Streamlit (UI)
        - PostgreSQL (structured data)
        - MongoDB (documents & audit logs)
        - LangChain + Google Gemini (AI agent)
        - Plotly (visualizations)

        **Version:** 1.0.0
        **Hackathon:** Finnovate 2024
        **Team:** [Your Team Name]
        """
        )

        st.markdown("---")
        st.caption("© 2024 Project Aura. Built for Adani Group's Finnovate Hackathon.")

# ==============================================
# GLOBAL FOOTER & FLOATING ELEMENTS
# ==============================================
st.markdown(
    """
    <div class="app-footer">
        <hr style="margin-bottom:2rem;border:none;border-top:1px solid #e5e7eb;">
        <strong>© 2025 Project Aura</strong> | Adani Group | Built at Finnovate Hackathon<br>
        <small style="color:#9ca3af;">Powered by AI · Secured by Design · Built for Enterprise</small>
    </div>
    """,
    unsafe_allow_html=True,
)

# Floating "Back to Top" button
st.markdown(
    """
    <div class="fab">
        <a href="#project-aura-financial-review-agent">
            <button>↑ Top</button>
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)
