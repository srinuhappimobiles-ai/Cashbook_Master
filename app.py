import io
import re
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Happi Cashbook Master",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 0rem !important; 
        padding-left: 0.8rem !important; 
        padding-right: 0.8rem !important; 
        max-width: 100% !important;
    }
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    /* Keep sidebar toggle button visible and styled properly */
    [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarNav"] {
        visibility: visible !important;
        display: block !important;
    }
    .main-title { 
        font-size: 18px; 
        font-weight: 700; 
        color: #0E4C92; 
        margin-bottom: 4px; 
        display: flex; 
        align-items: center; 
        gap: 8px; 
    }
    .stSidebar { background-color: #f8fafc; }
    iframe { width: 100% !important; border: 1px solid #cbd5e1 !important; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# Default Google Sheet URL placeholder (can be configured directly in sidebar)
DEFAULT_GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"

def get_embed_sheet_url(raw_url):
    """Converts a standard Google Sheet URL to an interactive full-screen embed URL."""
    if not raw_url:
        return ""
    # Strip edit/preview paths and append minimal interface parameters
    base_url = re.sub(r"/edit.*", "", raw_url.strip())
    base_url = re.sub(r"/view.*", "", base_url)
    return f"{base_url}/edit?rm=minimal&widget=true&headers=true"

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("### 🏢 Happi Control Hub")
    
    st.markdown("#### 🔗 Google Sheet Integration")
    sheet_url_input = st.text_input(
        "Live Google Sheet URL:",
        value=st.session_state.get("saved_sheet_url", DEFAULT_GOOGLE_SHEET_URL),
        placeholder="Paste Google Sheet Edit Link here"
    )
    if sheet_url_input:
        st.session_state.saved_sheet_url = sheet_url_input

    st.markdown("---")
    st.markdown("#### 📥 Direct File Ingestion")
    with st.expander("📂 1. Apex Dr Balance File", expanded=True):
        ho_dump_file = st.file_uploader("Upload Apex File", type=["xlsx", "xls", "csv"], key="ho_dump")

    with st.expander("📥 2. Addins Dump File", expanded=True):
        addins_dump_file = st.file_uploader("Upload Addins File", type=["xlsx", "xls", "csv"], key="addins_dump")

    st.markdown("---")
    st.markdown("#### 💡 Quick Instructions")
    st.info("""
    1. In Google Sheets, set access to **Share -> Anyone with the link -> Editor**.
    2. All updates, formulas, and drags are **100% live and auto-saved**.
    3. Access the workspace from any computer without losing data.
    """)

# Header Bar
col_head1, col_head2 = st.columns([3.5, 1])

with col_head1:
    st.markdown(
        '<div class="main-title">📊 HAPPI MOBILES - MASTER CASHBOOK WORKSPACE '
        '<span style="font-size: 13px; color: #16a34a; font-weight: bold;">● Live Google Sheet Connected</span></div>',
        unsafe_allow_html=True
    )

with col_head2:
    if sheet_url_input and "docs.google.com" in sheet_url_input:
        st.markdown(f"""
            <a href="{sheet_url_input}" target="_blank" style="text-decoration: none;">
                <button style="width: 100%; height: 38px; background-color: #0E4C92; color: white; border: none; border-radius: 5px; font-weight: 600; cursor: pointer;">
                    🚀 Open in New Tab
                </button>
            </a>
        """, unsafe_allow_html=True)

# Embedded Google Sheet (Full-Screen Viewport)
active_url = get_embed_sheet_url(sheet_url_input)

if "YOUR_SHEET_ID" in active_url or not active_url:
    st.warning("⚠️ Please paste your **Google Sheet link** in the left sidebar to load the live workspace.")
else:
    components.iframe(active_url, height=830, scrolling=True)
