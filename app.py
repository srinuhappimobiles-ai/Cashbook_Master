import io
import math
import os
import re
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Happi Cashbook Master Workspace",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 0.5rem !important; 
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
        font-size: 19px; 
        font-weight: 700; 
        color: #0E4C92; 
        display: flex; 
        align-items: center; 
        gap: 8px; 
    }
    .stSidebar { background-color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "cashbook_master.db"

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

DATA_COLS = [
    "OPENING_BALANCE", "DEPOSIT", "DENOMINATION", "ADDINGS",
    "PENDING_APPRVLS", "FINANCE_AMNT", "SR", "SWEEPER_SALARY",
    "EDITS", "APX_SHORTAGE", "KSP_APPROVALS", "REMARKS"
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS cashbook (
            code TEXT,
            branch TEXT PRIMARY KEY,
            opening_balance TEXT DEFAULT '',
            deposit TEXT DEFAULT '',
            denomination TEXT DEFAULT '',
            addings TEXT DEFAULT '',
            pending_apprvls TEXT DEFAULT '',
            finance_amnt TEXT DEFAULT '',
            sr TEXT DEFAULT '',
            sweeper_salary TEXT DEFAULT '',
            edits TEXT DEFAULT '',
            apx_shortage TEXT DEFAULT '',
            ksp_approvals TEXT DEFAULT '',
            remarks TEXT DEFAULT ''
        )
    """)
    for b in DEFAULT_BRANCHES:
        c.execute("""
            INSERT OR IGNORE INTO cashbook (code, branch)
            VALUES (?, ?)
        """, (b["CODE"], b["BRANCH"]))
    conn.commit()
    conn.close()

init_db()

def get_db_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM cashbook ORDER BY branch ASC", conn)
    conn.close()
    return df

def update_cell_db(branch, col_name, val):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"UPDATE cashbook SET {col_name.lower()} = ? WHERE branch = ?", (str(val), branch))
    conn.commit()
    conn.close()

def bulk_update_col(data_dict, col_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for branch, val in data_dict.items():
        c.execute(f"UPDATE cashbook SET {col_name.lower()} = ? WHERE branch = ?", (str(val), branch))
    conn.commit()
    conn.close()

def reset_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM cashbook")
    conn.commit()
    conn.close()
    init_db()

def normalize_key(s):
    if not s: return ""
    return re.sub(r"[^A-Za-z0-9]", "", str(s)).upper()

def evaluate_val(val):
    if val is None or pd.isna(val): return 0.0
    s = str(val).strip()
    if not s: return 0.0
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

def format_excel_formula(num_list):
    if not num_list: return ""
    clean_ints = [str(int(x)) for x in num_list if x > 0]
    if not clean_ints: return ""
    if len(clean_ints) == 1: return clean_ints[0]
    return "=" + "+".join(clean_ints)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏢 Happi Control Hub")
    
    st.markdown("#### 👥 Work Assignment Mode")
    work_mode = st.radio(
        "Assignment Mode:",
        ["👤 Single Cashier (All Stores)", "👥 Two Cashiers (Split 50-50)"],
        label_visibility="collapsed"
    )

    all_branches = sorted(DEFAULT_BRANCHES, key=lambda x: x["BRANCH"])
    selected_branches = all_branches

    if work_mode == "👥 Two Cashiers (Split 50-50)":
        mid_point = math.ceil(len(all_branches) / 2)
        c1_branches = all_branches[:mid_point]
        c2_branches = all_branches[mid_point:]
        cashier_view = st.selectbox("Current Cashier:", [f"Cashier 1 ({len(c1_branches)} Stores)", f"Cashier 2 ({len(c2_branches)} Stores)"])
        selected_branches = c1_branches if "Cashier 1" in cashier_view else c2_branches

    st.markdown("---")
    st.markdown("#### 📥 Direct File Ingestion")
    
    with st.expander("📂 1. Apex Dr Balance File", expanded=True):
        ho_dump_file = st.file_uploader("Upload Apex File", type=["xlsx", "xls", "xlsm", "csv"], key="ho_dump")

    with st.expander("📥 2. Addins Dump File", expanded=True):
        addins_dump_file = st.file_uploader("Upload Addins File", type=["xlsx", "xls", "xlsm", "csv"], key="addins_dump")

    st.markdown("---")
    st.markdown("#### ⚙️ Data Actions")
    if st.button("🧹 Clear & Reset Master Database", use_container_width=True):
        reset_db()
        st.rerun()

# 1. Process Apex Ingestion
if ho_dump_file:
    try:
        df_dump = pd.read_csv(ho_dump_file) if ho_dump_file.name.endswith(".csv") else pd.read_excel(ho_dump_file)
        b_col, a_col = df_dump.columns[0], df_dump.columns[1] if len(df_dump.columns) > 1 else df_dump.columns[0]
        for col in df_dump.columns:
            if "branch" in str(col).lower() or "store" in str(col).lower(): b_col = col
            if "balance" in str(col).lower() or "opening" in str(col).lower() or "amount" in str(col).lower(): a_col = col

        dump_dict = {}
        for _, row in df_dump.iterrows():
            b_val, raw_amt = normalize_key(row[b_col]), str(row[a_col]).replace(",", "").strip()
            match = re.search(r"(\d+\.?\d*)", raw_amt)
            if match and b_val:
                dump_dict[b_val] = int(round(float(match.group(1))))

        update_payload = {}
        for b in all_branches:
            val = dump_dict.get(normalize_key(b["BRANCH"]), dump_dict.get(normalize_key(b["CODE"])))
            if val is not None:
                update_payload[b["BRANCH"]] = str(val)

        if update_payload:
            bulk_update_col(update_payload, "opening_balance")
            st.sidebar.success(f"✅ Synced {len(update_payload)} Opening Balances!")
            st.rerun()
    except Exception as e:
        st.sidebar.error(f"Apex Error: {e}")

# 2. Process Addins Ingestion
if addins_dump_file:
    try:
        df_addins = pd.read_csv(addins_dump_file) if addins_dump_file.name.endswith(".csv") else pd.read_excel(addins_dump_file)
        b_col, a_col = df_addins.columns[0], df_addins.columns[1] if len(df_addins.columns) > 1 else df_addins.columns[0]
        for col in df_addins.columns:
            if "branch" in str(col).lower() or "store" in str(col).lower(): b_col = col
            if "amount" in str(col).lower() or "total" in str(col).lower() or "addin" in str(col).lower(): a_col = col

        addins_dict = {}
        for _, row in df_addins.iterrows():
            b_val, raw_amt = normalize_key(row[b_col]), str(row[a_col]).replace(",", "").strip()
            match = re.search(r"(\d+\.?\d*)", raw_amt)
            if match and b_val:
                clean_amt = int(round(float(match.group(1))))
                if clean_amt > 0:
                    addins_dict.setdefault(b_val, []).append(clean_amt)

        update_payload = {}
        for b in all_branches:
            vouchers = addins_dict.get(normalize_key(b["BRANCH"]), addins_dict.get(normalize_key(b["CODE"]), []))
            if vouchers:
                update_payload[b["BRANCH"]] = format_excel_formula(vouchers)

        if update_payload:
            bulk_update_col(update_payload, "addings")
            st.sidebar.success(f"✅ Synced {len(update_payload)} Addin Vouchers!")
            st.rerun()
    except Exception as e:
        st.sidebar.error(f"Addins Error: {e}")

# Build Active Workspace DataFrame from SQLite
df_raw = get_db_data()
df_raw.fillna("", inplace=True)

selected_branch_names = [b["BRANCH"] for b in selected_branches]
df_filtered = df_raw[df_raw["branch"].isin(selected_branch_names)].copy()

# Add Calculated Closing Balance
def compute_closing(row):
    op = evaluate_val(row["opening_balance"])
    if not str(row["opening_balance"]).strip():
        return ""
    deductions = sum([
        evaluate_val(row["deposit"]),
        evaluate_val(row["denomination"]),
        evaluate_val(row["addings"]),
        evaluate_val(row["pending_apprvls"]),
        evaluate_val(row["finance_amnt"]),
        evaluate_val(row["sr"]),
        evaluate_val(row["sweeper_salary"]),
        evaluate_val(row["edits"]),
        evaluate_val(row["apx_shortage"]),
        evaluate_val(row["ksp_approvals"])
    ])
    return str(int(round(op - deductions)))

df_filtered["closing_balance"] = df_filtered.apply(compute_closing, axis=1)

# Rename Columns for Clean Presentation
col_display_map = {
    "code": "CODE",
    "branch": "BRANCH",
    "opening_balance": "OPENING BALANCE",
    "deposit": "DEPOSIT",
    "denomination": "DENOMINATION",
    "addings": "AddinGS",
    "pending_apprvls": "PENDING APPRVLS",
    "finance_amnt": "FINANCE AMNT",
    "sr": "SR",
    "sweeper_salary": "SWEEPER SALARY",
    "edits": "EDITS",
    "apx_shortage": "APX SHORTAGE",
    "ksp_approvals": "(KSP)'Sir's Approvals",
    "closing_balance": "CLOSING BALANCE",
    "remarks": "REMARKS"
}

df_filtered.rename(columns=col_display_map, inplace=True)
df_filtered.insert(0, "Sl.No.", range(1, len(df_filtered) + 1))

# --- HEADER BAR & DOWNLOAD ---
col_h1, col_h2 = st.columns([3.5, 1])

with col_h1:
    st.markdown(
        f'<div class="main-title">📊 HAPPI MOBILES - MASTER CASHBOOK WORKSPACE '
        f'<span style="font-size: 13px; color: #16a34a; font-weight: bold;">● SQLite Persistent Cloud Sync</span></div>',
        unsafe_allow_html=True
    )

with col_h2:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='MASTER REPORT')
    st.download_button(
        label="📥 Download Master Excel",
        data=output.getvalue(),
        file_name="HO_MASTER_CASHBOOK_REPORT.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# Interactive Real-Time Data Grid
column_config = {
    col: st.column_config.TextColumn(col) for col in [
        "OPENING BALANCE", "DEPOSIT", "DENOMINATION", "AddinGS", "PENDING APPRVLS",
        "FINANCE AMNT", "SR", "SWEEPER SALARY", "EDITS", "APX SHORTAGE",
        "(KSP)'Sir's Approvals", "REMARKS"
    ]
}
column_config["CLOSING BALANCE"] = st.column_config.TextColumn("CLOSING BALANCE", disabled=True)

edited_df = st.data_editor(
    df_filtered,
    use_container_width=True,
    height=780,
    disabled=["Sl.No.", "CODE", "BRANCH", "CLOSING BALANCE"],
    column_config=column_config,
    num_rows="fixed",
    key=f"cashbook_grid_{work_mode}_{len(selected_branches)}"
)

# Auto-Save Modified Cells Directly to SQLite
rev_map = {v: k for k, v in col_display_map.items()}
has_updates = False

for _, row in edited_df.iterrows():
    b_name = row["BRANCH"]
    orig_row = df_filtered[df_filtered["BRANCH"] == b_name].iloc[0]
    
    for display_col in list(col_display_map.values())[2:]: # Only editable columns
        new_val = str(row[display_col]) if pd.notna(row[display_col]) else ""
        old_val = str(orig_row[display_col]) if pd.notna(orig_row[display_col]) else ""
        
        if new_val != old_val:
            db_col = rev_map[display_col]
            update_cell_db(b_name, db_col, new_val)
            has_updates = True

if has_updates:
    st.rerun()
