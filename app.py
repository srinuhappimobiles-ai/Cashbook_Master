import io
import json
import math
import os
import re
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Happi Cashbook Master - Excel 2010",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 0rem !important; 
        padding-left: 0.8rem !important; 
        padding-right: 0.8rem !important; 
        max-width: 100% !important;
    }
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarNav"] {
        visibility: visible !important;
        display: block !important;
    }
    .main-title { 
        font-size: 18px; 
        font-weight: 700; 
        color: #107c41; 
        margin-bottom: 4px; 
        display: flex; 
        align-items: center; 
        gap: 8px; 
    }
    .stSidebar { background-color: #f8fafc; }
    iframe { width: 100% !important; border: 1px solid #cbd5e1 !important; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

DEFAULT_BRANCHES = [
    {"CODE": "ADBD", "BRANCH": "ADILABAD"}, {"CODE": "AMP", "BRANCH": "AMALAPURAM"},
    {"CODE": "AMPT", "BRANCH": "AMEERPET"}, {"CODE": "ANTP", "BRANCH": "ANANTAPUR"},
    {"CODE": "ARMU", "BRANCH": "ARMOOR"}, {"CODE": "ATMKR", "BRANCH": "ATMAKUR"},
    {"CODE": "BDHN", "BRANCH": "BODHAN"}, {"CODE": "BDPL", "BRANCH": "BODUPPAL"},
    {"CODE": "BG", "BHUVANAGIRI": "BG"}, {"CODE": "BVRM", "BRANCH": "BHIMAVARAM"},
    {"CODE": "CHND", "BRANCH": "CHANDANAGAR"}, {"CODE": "CHNT", "BRANCH": "CHINTAL"},
    {"CODE": "DBGS", "BRANCH": "DABAGARDENS"}, {"CODE": "DBGS-2", "BRANCH": "DABAGARDENS-2"},
    {"CODE": "DVKD", "BRANCH": "DEVARAKONDA"}, {"CODE": "DVRM", "BRANCH": "DHARMAVRAM"},
    {"CODE": "ECIL", "BRANCH": "ECIL"}, {"CODE": "ELR", "BRANCH": "ELURU"},
    {"CODE": "GDVK", "BRANCH": "GODHAVARIKHANI"}, {"CODE": "GJWK", "BRANCH": "GAJUWAKA"},
    {"CODE": "GJWL", "BRANCH": "GAJWEL"}, {"CODE": "GNT", "BRANCH": "GUNTUR"},
    {"CODE": "GNT2", "BRANCH": "GUNTUR2"}, {"CODE": "GTKL", "BRANCH": "GUNTAKAL"},
    {"CODE": "GWD", "BRANCH": "GADWAL"}, {"CODE": "HAL", "BRANCH": "HALIYA"},
    {"CODE": "HNMK", "BRANCH": "HANUMAKONDA"}, {"CODE": "HUP", "BRANCH": "HINDUPUR"},
    {"CODE": "JCL", "BRANCH": "JADCHERLA"}, {"CODE": "JNGN", "BRANCH": "JANGAON"},
    {"CODE": "JTL", "BRANCH": "JAGTIAL"}, {"CODE": "KDGM", "BRANCH": "KALYANADURGAM"},
    {"CODE": "KDR", "BRANCH": "KADIRI"}, {"CODE": "KDR2", "BRANCH": "KADIRI-2"},
    {"CODE": "KKP", "BRANCH": "KUKATPALLY"}, {"CODE": "KMGH", "BRANCH": "KHARMANGHAT"},
    {"CODE": "KMM", "BRANCH": "KHAMMAM"}, {"CODE": "KMM2", "BRANCH": "KHAMMAM 2"},
    {"CODE": "KPM", "BRANCH": "KUPPAM"}, {"CODE": "KRKH", "BRANCH": "KHARKHANA"},
    {"CODE": "KRLA", "BRANCH": "KORUTLA"}, {"CODE": "KRMN", "BRANCH": "KARIMNAGAR"},
    {"CODE": "KRNL", "BRANCH": "KURNOOL"}, {"CODE": "KRNL2", "BRANCH": "KURNOOL2"},
    {"CODE": "KZP", "BRANCH": "KAZIPET"}, {"CODE": "MCI", "BRANCH": "MANCHERIAL"},
    {"CODE": "MDPL", "BRANCH": "MADANAPALLI"}, {"CODE": "MDPR", "BRANCH": "MADHAPUR"},
    {"CODE": "MDPT", "BRANCH": "MANDAPETA"}, {"CODE": "MHBR", "BRANCH": "MAHABUBNAGAR"},
    {"CODE": "MLKJ", "BRANCH": "MALKAJGIRI"}, {"CODE": "MRGA", "BRANCH": "MIRYALAGUDA"},
    {"CODE": "MTM", "BRANCH": "MACHILIPATNAM"}, {"CODE": "MVP", "BRANCH": "MVP COLONY"},
    {"CODE": "NDD", "BRANCH": "NIDADAVOLE"}, {"CODE": "NDL", "BRANCH": "NANDYALA"},
    {"CODE": "NGKL", "BRANCH": "NAGARKURNOOL"}, {"CODE": "NKRL", "BRANCH": "NAKREKAL"},
    {"CODE": "NLG", "BRANCH": "NALGONDA"}, {"CODE": "NRKD", "BRANCH": "NARAYANKHED"},
    {"CODE": "NRML", "BRANCH": "NIRMAL"}, {"CODE": "NRSP", "BRANCH": "NARASANNAPETA"},
    {"CODE": "NSMP", "BRANCH": "NARSAMPET"}, {"CODE": "NSPT", "BRANCH": "NARSIPATNAM"},
    {"CODE": "NZVD", "BRANCH": "NUZVID"}, {"CODE": "ONG", "BRANCH": "ONGOLE"},
    {"CODE": "PDPL", "BRANCH": "PEDDAPALLI"}, {"CODE": "PDPM", "BRANCH": "PEDDAPURAM"},
    {"CODE": "PIL", "BRANCH": "PILERU"}, {"CODE": "PLM", "BRANCH": "PALAMANER"},
    {"CODE": "PSA", "BRANCH": "PALASA"}, {"CODE": "PVA", "BRANCH": "PALAVANCHA"},
    {"CODE": "RCT", "BRANCH": "RAYACHOTI"}, {"CODE": "RJY", "BRANCH": "RAJAMUNDRY"},
    {"CODE": "RMTP", "BRANCH": "RAMANTHAPUR"}, {"CODE": "RTCX", "BRANCH": "RTC X ROAD"},
    {"CODE": "SDPT", "BRANCH": "SIDDIPET"}, {"CODE": "SDR", "BRANCH": "S.D.ROAD"},
    {"CODE": "SHDR", "BRANCH": "SHADNAGAR"}, {"CODE": "SHPR", "BRANCH": "SHAPUR"},
    {"CODE": "SKKM", "BRANCH": "SRIKAKULAM"}, {"CODE": "SMBD", "BRANCH": "SHAMSHABAD"},
    {"CODE": "SNGR", "BRANCH": "SANGAREDDY"}, {"CODE": "SPT", "BRANCH": "SOMPETA"},
    {"CODE": "SRN", "BRANCH": "S.R.NAGAR"}, {"CODE": "SRNR", "BRANCH": "SAROORNAGAR"},
    {"CODE": "SRPT", "BRANCH": "SURYAPET"}, {"CODE": "STNR", "BRANCH": "SANTOSHNAGAR"},
    {"CODE": "TDPG", "BRANCH": "TADEPALLIGUDEM"}, {"CODE": "TDPT", "BRANCH": "TADIPATRI"},
    {"CODE": "TDU", "BRANCH": "TANDUR"}, {"CODE": "TEK", "BRANCH": "TEKKALI"},
    {"CODE": "TN", "BRANCH": "TUNI"}, {"CODE": "TNK", "BRANCH": "TANUKU"},
    {"CODE": "TNL", "BRANCH": "TENALI"}, {"CODE": "TPT", "BRANCH": "TIRUPATHI"},
    {"CODE": "TPT2", "BRANCH": "TIRUPATHI 2"}, {"CODE": "UPL", "BRANCH": "UPPAL"},
    {"CODE": "VIJ-1", "BRANCH": "VIJAYAWADA 1"}, {"CODE": "VIJ-3", "BRANCH": "VIJAYAWADA 3"},
    {"CODE": "VIJ-4", "BRANCH": "VIJAYAWADA 4"}, {"CODE": "VNSP", "BRANCH": "VANASTALIPURAM"},
    {"CODE": "VZM", "BRANCH": "VIZIANAGARAM"}, {"CODE": "VZM2", "BRANCH": "VIZIANAGARAM 2"},
    {"CODE": "WGL", "BRANCH": "WARANGAL"}, {"CODE": "WGL2", "BRANCH": "WARANGAL 2"},
    {"CODE": "ZB", "BRANCH": "ZAHEERABAD"}
]

HEADERS = [
    "SL.No.", "CODE", "BRANCH", "OPENING BALANCE", "DEPOSIT", "DENOMINATION", 
    "AddinGS", "PENDING APPRVLS", "FINANCE AMNT", "SR", "SWEEPER SALARY", 
    "EDITS", "APX SHORTAGE", "(KSP)'Sir's Approvals", "CLOSING BALANCE", "REMARKS"
]

@st.cache_resource
def get_shared_db():
    return {
        "branches": sorted(DEFAULT_BRANCHES, key=lambda x: str(x.get("BRANCH", "")).upper()),
        "entries": {}
    }

db = get_shared_db()
all_branches = db["branches"]

SUPPORTED_EXCEL_TYPES = ["xlsx", "xls", "xlsm", "xlsb", "csv"]

def normalize_key(s):
    if not s: return ""
    return re.sub(r"[^A-Za-z0-9]", "", str(s)).upper()

def format_excel_formula(num_list):
    if not num_list: return ""
    clean_ints = [str(int(x)) for x in num_list if x > 0]
    if not clean_ints: return ""
    if len(clean_ints) == 1: return clean_ints[0]
    return "=" + "+".join(clean_ints)

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("### 🏢 Happi Control Hub")
    
    work_mode = st.radio(
        "Assignment Mode:",
        ["👤 Single Cashier (All Stores)", "👥 Two Cashiers (Split 50-50)"],
        label_visibility="collapsed"
    )

    selected_branches = all_branches
    if work_mode == "👥 Two Cashiers (Split 50-50)":
        mid_point = math.ceil(len(all_branches) / 2)
        c1_branches = all_branches[:mid_point]
        c2_branches = all_branches[mid_point:]
        cashier_view = st.selectbox("Current Cashier:", [f"Cashier 1 ({len(c1_branches)} Stores)", f"Cashier 2 ({len(c2_branches)} Stores)"])
        selected_branches = c1_branches if "Cashier 1" in cashier_view else c2_branches

    st.markdown("---")
    st.markdown("#### 📥 Direct File Ingestion")
    
    with st.expander("📂 1. Apex Dr Balance File", expanded=False):
        ho_dump_file = st.file_uploader("Upload Apex File", type=SUPPORTED_EXCEL_TYPES, key="ho_dump")

    with st.expander("📥 2. Addins Dump File", expanded=False):
        addins_dump_file = st.file_uploader("Upload Addins File", type=SUPPORTED_EXCEL_TYPES, key="addins_dump")

    with st.expander("💻 3. Import System Excel Sheet (.xlsm / .xlsx)", expanded=True):
        master_import_file = st.file_uploader("Upload Local Sheet to Populate", type=SUPPORTED_EXCEL_TYPES, key="local_master_uploader")

    st.markdown("---")
    st.markdown("#### ⚙️ Data Actions")
    if st.button("🧹 Clear & Reset Master Cashbook", use_container_width=True):
        db["entries"] = {}
        st.rerun()

# 1. Process Master Sheet Import (.xlsm / .xlsx)
if master_import_file:
    try:
        if master_import_file.name.endswith(".csv"):
            df_raw = pd.read_csv(master_import_file, header=None)
        else:
            df_raw = pd.read_excel(master_import_file, header=None)

        header_row_idx = 0
        for r_idx in range(min(15, len(df_raw))):
            row_vals = [normalize_key(x) for x in df_raw.iloc[r_idx].dropna()]
            if any(k in row_vals for k in ["BRANCH", "BRANCHNAME", "STORE", "OPENINGBALANCE", "DENOMINATION"]):
                header_row_idx = r_idx
                break

        if master_import_file.name.endswith(".csv"):
            df_imported = pd.read_csv(master_import_file, skiprows=header_row_idx)
        else:
            df_imported = pd.read_excel(master_import_file, skiprows=header_row_idx)

        df_imported.fillna("", inplace=True)

        col_mapping = {}
        for col in df_imported.columns:
            c_norm = normalize_key(col)
            for target_col in HEADERS:
                if c_norm == normalize_key(target_col) or target_col.upper() in str(col).upper():
                    col_mapping[col] = target_col
                    break
            if "BRANCH" not in col_mapping.values() and any(x in c_norm for x in ["BRANCH", "STORE"]):
                col_mapping[col] = "BRANCH"
            if "CODE" not in col_mapping.values() and "CODE" in c_norm:
                col_mapping[col] = "CODE"

        b_col_actual = None
        for orig, mapped in col_mapping.items():
            if mapped == "BRANCH":
                b_col_actual = orig
                break

        if b_col_actual is None:
            b_col_actual = df_imported.columns[2] if len(df_imported.columns) > 2 else df_imported.columns[0]

        imported_count = 0
        for _, row in df_imported.iterrows():
            b_val_norm = normalize_key(row[b_col_actual])
            if not b_val_norm: continue

            matched_branch = None
            for b in all_branches:
                if normalize_key(b.get("BRANCH", "")) == b_val_norm or normalize_key(b.get("CODE", "")) == b_val_norm:
                    matched_branch = b.get("BRANCH", "")
                    break

            if matched_branch:
                target_entry = db.setdefault("entries", {}).setdefault(matched_branch, {})
                for orig_col, cell_val in row.items():
                    standard_col = col_mapping.get(orig_col, str(orig_col).strip())
