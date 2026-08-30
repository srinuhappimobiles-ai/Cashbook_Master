import io
import json
import math
import os
import re
import numpy as np
import pandas as pd
import streamlit as st

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
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
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
        color: #0E4C92; 
        margin-bottom: 4px; 
        display: flex; 
        align-items: center; 
        gap: 8px; 
    }
    .stSidebar { background-color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

# 107 Standard Branch Definitions
DEFAULT_BRANCHES = [
    {"CODE": "ADBD", "BRANCH": "ADILABAD"}, {"CODE": "AMP", "BRANCH": "AMALAPURAM"},
    {"CODE": "AMPT", "BRANCH": "AMEERPET"}, {"CODE": "ANTP", "BRANCH": "ANANTAPUR"},
    {"CODE": "ARMU", "BRANCH": "ARMOOR"}, {"CODE": "ATMKR", "BRANCH": "ATMAKUR"},
    {"CODE": "BDHN", "BRANCH": "BODHAN"}, {"CODE": "BDPL", "BRANCH": "BODUPPAL"},
    {"CODE": "BG", "BRANCH": "BHUVANAGIRI"}, {"CODE": "BVRM", "BRANCH": "BHIMAVARAM"},
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

# Shared Global Database across all browser tabs
@st.cache_resource
def get_shared_db():
    return {
        "branches": sorted(DEFAULT_BRANCHES, key=lambda x: x["BRANCH"].upper()),
        "entries": {}
    }

db = get_shared_db()
all_branches = db["branches"]

def format_excel_formula(num_list):
    if not num_list: return ""
    clean_ints = [str(int(x)) for x in num_list if x > 0]
    if not clean_ints: return ""
    if len(clean_ints) == 1: return clean_ints[0]
    return "=" + "+".join(clean_ints)

def normalize_name(s):
    if not s: return ""
    return re.sub(r"[^A-Za-z0-9]", "", str(s)).upper()

def evaluate_val(val):
    if val is None or pd.isna(val):
        return 0.0
    s = str(val).strip()
    if not s:
        return 0.0
    if s.startswith("="):
        expr = s[1:]
        try:
            if re.match(r"^[0-9+\-*/().\s]+$", expr):
                return float(eval(expr))
        except:
            return 0.0
    try:
        return float(s.replace(",", ""))
    except:
        return 0.0

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("### 🏢 Happi Control Hub")
    
    st.markdown("#### 👥 Work Mode")
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
        ho_dump_file = st.file_uploader("Upload Apex File", type=["xlsx", "xls", "csv"], key="ho_dump")

    with st.expander("📥 2. Addins Dump File", expanded=False):
        addins_dump_file = st.file_uploader("Upload Addins File", type=["xlsx", "xls", "csv"], key="addins_dump")

    with st.expander("💻 3. Import System Excel Sheet", expanded=False):
        master_import_file = st.file_uploader("Upload Local Sheet to Populate", type=["xlsx", "xls", "csv"], key="local_master_uploader")

    st.markdown("---")
    st.markdown("#### ⚙️ Data Actions")
    if st.button("🧹 Clear & Reset Master Cashbook", use_container_width=True):
        db["entries"] = {}
        st.rerun()

# Process Ingestions directly into Global Server State
if ho_dump_file:
    try:
        df_dump = pd.read_csv(ho_dump_file) if ho_dump_file.name.endswith(".csv") else pd.read_excel(ho_dump_file)
        b_col, a_col = df_dump.columns[0], df_dump.columns[1] if len(df_dump.columns) > 1 else df_dump.columns[0]
        for col in df_dump.columns:
            if "branch" in str(col).lower() or "store" in str(col).lower(): b_col = col
            if "balance" in str(col).lower() or "opening" in str(col).lower() or "amount" in str(col).lower(): a_col = col

        dump_dict = {}
        for _, row in df_dump.iterrows():
            b_val, raw_amt = normalize_name(row[b_col]), str(row[a_col]).replace(",", "").strip()
            match = re.search(r"(\d+\.?\d*)", raw_amt)
            if match and b_val:
                dump_dict[b_val] = int(round(float(match.group(1))))

        for b in all_branches:
            val = dump_dict.get(normalize_name(b["BRANCH"]), dump_dict.get(normalize_name(b["CODE"])))
            if val is not None:
                db.setdefault("entries", {}).setdefault(b["BRANCH"], {})["OPENING BALANCE"] = str(val)
        st.sidebar.success("✅ Apex Dr Balances Synced Globally!")
    except Exception as e:
        st.sidebar.error(f"Apex Error: {e}")

if addins_dump_file:
    try:
        df_addins = pd.read_csv(addins_dump_file) if addins_dump_file.name.endswith(".csv") else pd.read_excel(addins_dump_file)
        b_col, a_col = df_addins.columns[0], df_addins.columns[1] if len(df_addins.columns) > 1 else df_addins.columns[0]
        for col in df_addins.columns:
            if "branch" in str(col).lower() or "store" in str(col).lower(): b_col = col
            if "amount" in str(col).lower() or "total" in str(col).lower() or "addin" in str(col).lower(): a_col = col

        addins_dict = {}
        for _, row in df_addins.iterrows():
            b_val, raw_amt = normalize_name(row[b_col]), str(row[a_col]).replace(",", "").strip()
            match = re.search(r"(\d+\.?\d*)", raw_amt)
            if match and b_val:
                clean_amt = int(round(float(match.group(1))))
                if clean_amt > 0:
                    addins_dict.setdefault(b_val, []).append(clean_amt)

        for b in all_branches:
            vouchers = addins_dict.get(normalize_name(b["BRANCH"]), addins_dict.get(normalize_name(b["CODE"]), []))
            if vouchers:
                clean_ints = [str(int(x)) for x in vouchers if x > 0]
                formula_val = clean_ints[0] if len(clean_ints) == 1 else "=" + "+".join(clean_ints)
                db.setdefault("entries", {}).setdefault(b["BRANCH"], {})["AddinGS"] = formula_val
        st.sidebar.success("✅ Addins Synced Globally!")
    except Exception as e:
        st.sidebar.error(f"Addins Error: {e}")

if master_import_file:
    try:
        df_imported = pd.read_csv(master_import_file) if master_import_file.name.endswith(".csv") else pd.read_excel(master_import_file)
        df_imported.fillna("", inplace=True)
        b_col = "BRANCH" if "BRANCH" in df_imported.columns else df_imported.columns[2]
        
        for _, row in df_imported.iterrows():
            b_name = str(row[b_col]).strip().upper()
            target_entry = db.setdefault("entries", {}).setdefault(b_name, {})
            for col in df_imported.columns:
                if col not in ["Sl.No.", "SL.No.", "CODE", "BRANCH", "CLOSING BALANCE"]:
                    if str(row[col]).strip() != "":
                        target_entry[col] = str(row[col]).strip()
        st.sidebar.success("✅ Custom Local Master Excel Imported!")
    except Exception as e:
        st.sidebar.error(f"Import Error: {e}")

# Build Real-time DataFrame with Auto Closing Calculation
data_matrix = []
entries_dict = db.get("entries", {})

for idx, b in enumerate(selected_branches, start=1):
    b_name = b["BRANCH"]
    e = entries_dict.get(b_name, {})

    op_bal = e.get("OPENING BALANCE", "")
    dep = e.get("DEPOSIT", "")
    den = e.get("DENOMINATION", "")
    addin = e.get("AddinGS", "")
    pend = e.get("PENDING APPRVLS", "")
    fin = e.get("FINANCE AMNT", "")
    sr = e.get("SR", "")
    swp = e.get("SWEEPER SALARY", "")
    edt = e.get("EDITS", "")
    apx_sh = e.get("APX SHORTAGE", "")
    ksp = e.get("(KSP)'Sir's Approvals", "")
    rem = e.get("REMARKS", "")

    total_deductions = sum([
        evaluate_val(dep), evaluate_val(den), evaluate_val(addin),
        evaluate_val(pend), evaluate_val(fin), evaluate_val(sr),
        evaluate_val(swp), evaluate_val(edt), evaluate_val(apx_sh),
        evaluate_val(ksp)
    ])
    
    closing_val = evaluate_val(op_bal) - total_deductions
    closing_display = str(int(round(closing_val))) if op_bal != "" else ""

    data_matrix.append({
        "Sl.No.": idx,
        "CODE": b["CODE"],
        "BRANCH": b["BRANCH"],
        "OPENING BALANCE": op_bal,
        "DEPOSIT": dep,
        "DENOMINATION": den,
        "AddinGS": addin,
        "PENDING APPRVLS": pend,
        "FINANCE AMNT": fin,
        "SR": sr,
        "SWEEPER SALARY": swp,
        "EDITS": edt,
        "APX SHORTAGE": apx_sh,
        "(KSP)'Sir's Approvals": ksp,
        "CLOSING BALANCE": closing_display,
        "REMARKS": rem
    })

df_active = pd.DataFrame(data_matrix)

# Header & Download
col_head1, col_head2 = st.columns([3.5, 1])

with col_head1:
    st.markdown(
        f'<div class="main-title">📊 HAPPI MOBILES - MASTER CASHBOOK WORKSPACE '
        f'<span style="font-size: 13px; color: #16a34a; font-weight: bold;">● Active ({len(selected_branches)} Stores)</span></div>',
        unsafe_allow_html=True
    )

with col_head2:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_active.to_excel(writer, index=False, sheet_name='MASTER REPORT')
    st.download_button(
        label="📥 Download Master Excel",
        data=output.getvalue(),
        file_name="HO_MASTER_CASHBOOK_REPORT.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# Editable Data Grid
column_config = {
    col: st.column_config.TextColumn(col) for col in [
        "OPENING BALANCE", "DEPOSIT", "DENOMINATION", "AddinGS", "PENDING APPRVLS",
        "FINANCE AMNT", "SR", "SWEEPER SALARY", "EDITS", "APX SHORTAGE",
        "(KSP)'Sir's Approvals", "REMARKS"
    ]
}
column_config["CLOSING BALANCE"] = st.column_config.TextColumn("CLOSING BALANCE", disabled=True)

edited_df = st.data_editor(
    df_active,
    use_container_width=True,
    height=800,
    disabled=["Sl.No.", "CODE", "BRANCH", "CLOSING BALANCE"],
    column_config=column_config,
    num_rows="fixed",
    key=f"master_grid_{work_mode}_{len(selected_branches)}"
)

# Auto-save changes back to global cache
has_changes = False
for _, row in edited_df.iterrows():
    b_name = row["BRANCH"]
    store_entry = db.setdefault("entries", {}).setdefault(b_name, {})
    for col in ["OPENING BALANCE", "DEPOSIT", "DENOMINATION", "AddinGS", "PENDING APPRVLS", "FINANCE AMNT", "SR", "SWEEPER SALARY", "EDITS", "APX SHORTAGE", "(KSP)'Sir's Approvals", "REMARKS"]:
        val = str(row[col]) if pd.notna(row[col]) else ""
        if store_entry.get(col, "") != val:
            store_entry[col] = val
            has_changes = True

if has_changes:
    st.rerun()
