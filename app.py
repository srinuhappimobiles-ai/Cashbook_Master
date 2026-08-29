import io
import json
import math
import os
import re
import numpy as np
import pandas as pd
from PIL import Image
import pytesseract
import streamlit as st

st.set_page_config(page_title="Happi Cashbook Master", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 0rem !important; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
        max-width: 100% !important;
    }
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
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

DB_FILE = "cashbook_master_db.json"

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

@st.cache_resource
def get_shared_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "branches": sorted(DEFAULT_BRANCHES, key=lambda x: x["BRANCH"].upper()),
        "entries": {}
    }

db = get_shared_db()

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

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
    if not val: return 0
    s = str(val).strip()
    if s.startswith("="):
        expr = s[1:]
        try:
            if re.match(r"^[0-9+\-*/().\s]+$", expr):
                return float(eval(expr))
        except:
            return 0
    try:
        return float(s.replace(",", ""))
    except:
        return 0

def process_cashbook_image(pil_img, target_branch):
    text_data = pytesseract.image_to_string(pil_img)
    lines = [l.strip() for l in text_data.split("\n") if l.strip()]

    denom_val = ""
    pending_apprvls = []
    finance_amnt = []
    sr_list = []
    edits_list = []
    ksp_approvals = []

    for line in lines:
        line_lower = line.lower()
        if any(h in line_lower for h in ["apx closing", "closing balance", "add ins", "addins", "total approval", "difference", "diffrence", "excess", "short", "corporate", "date", "bill no"]):
            continue

        cleaned = re.sub(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", " ", line)
        cleaned = re.sub(r"\b[A-Za-z0-9]+/[A-Za-z0-9]+/\d+\b", " ", cleaned)
        cleaned = re.sub(r"\b[A-Za-z0-9]+/\d+\b", " ", cleaned)

        nums = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", cleaned)
        valid_nums = []
        for n in nums:
            val = float(n.replace(",", ""))
            if val > 0 and val not in [2024, 2025, 2026, 2027]:
                valid_nums.append(int(round(val)))

        if valid_nums:
            amount = valid_nums[-1]
            if any(k in line_lower for k in ["bajaj", "idfc", "cash back", "cashback", "cash to card", "upi", "dbd", "finance"]):
                finance_amnt.append(amount)
            elif any(k in line_lower for k in ["sales return", "sale return", "srn", "sr/", "doa", "return", "sr "]):
                sr_list.append(amount)
            elif any(k in line_lower for k in ["pavan", "santhosh", "sharan"]):
                ksp_approvals.append(amount)
            elif "extra" in line_lower or "edit" in line_lower:
                edits_list.append(amount)
            else:
                pending_apprvls.append(amount)

        if "total" in line_lower and "approval" not in line_lower:
            tot_nums = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", line)
            if tot_nums:
                denom_val = str(int(float(tot_nums[-1].replace(",", ""))))

    store_entry = db["entries"].setdefault(target_branch, {})
    if denom_val: store_entry["DENOMINATION"] = denom_val
    if pending_apprvls: store_entry["PENDING APPRVLS"] = format_excel_formula(pending_apprvls)
    if finance_amnt: store_entry["FINANCE AMNT"] = format_excel_formula(finance_amnt)
    if sr_list: store_entry["SR"] = format_excel_formula(sr_list)
    if edits_list: store_entry["EDITS"] = format_excel_formula(edits_list)
    if ksp_approvals: store_entry["(KSP)'Sir's Approvals"] = format_excel_formula(ksp_approvals)
    save_db()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏢 Happi Control Hub")
    
    work_mode = st.radio(
        "Assignment Mode:",
        ["👤 Single Cashier (All Stores)", "👥 Two Cashiers (Split 50-50)"],
        label_visibility="collapsed"
    )

    all_branches = db["branches"]
    selected_branches = all_branches

    if work_mode == "👥 Two Cashiers (Split 50-50)":
        mid_point = math.ceil(len(all_branches) / 2)
        c1_branches = all_branches[:mid_point]
        c2_branches = all_branches[mid_point:]
        cashier_view = st.selectbox("Current Cashier:", [f"Cashier 1 ({len(c1_branches)} Stores)", f"Cashier 2 ({len(c2_branches)} Stores)"])
        selected_branches = c1_branches if "Cashier 1" in cashier_view else c2_branches

    st.markdown("---")
    with st.expander("📸 1. Single Store Snip (OCR)", expanded=True):
        target_branch_name = st.selectbox("Target Store:", [b["BRANCH"] for b in selected_branches], key="snip_paste_store")
        single_snip_file = st.file_uploader("Upload Cashbook Snip", type=["png", "jpg", "jpeg"], key=f"single_snip_{target_branch_name}")
        if single_snip_file:
            image = Image.open(single_snip_file)
            with st.spinner(f"Mapping {target_branch_name}..."):
                process_cashbook_image(image, target_branch_name)
                st.success(f"✅ Mapped & Synced {target_branch_name}!")
                st.rerun()

    with st.expander("📂 2. Apex Dr Balance File", expanded=False):
        ho_dump_file = st.file_uploader("Upload Apex File", type=["xlsx", "xls", "csv"], key="ho_dump")

    with st.expander("📥 3. Addins Dump File", expanded=False):
        addins_dump_file = st.file_uploader("Upload Addins File", type=["xlsx", "xls", "csv"], key="addins_dump")

    st.markdown("---")
    st.markdown("#### ⚙️ Data Actions")
    if st.button("🧹 Clear & Reset Master Server DB", use_container_width=True):
        db["entries"] = {}
        save_db()
        st.rerun()

# Process Ingestions directly into Global Server State
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
                db["entries"].setdefault(b["BRANCH"], {})["AddinGS"] = format_excel_formula(vouchers)
        save_db()
        st.sidebar.success("✅ Addins Synced Globally!")
    except Exception as e:
        st.sidebar.error(f"Addins Error: {e}")

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
                db["entries"].setdefault(b["BRANCH"], {})["OPENING BALANCE"] = str(val)
        save_db()
        st.sidebar.success("✅ Dr Balances Synced Globally!")
    except Exception as e:
        st.sidebar.error(f"Apex Error: {e}")

# Build DataFrame
data_matrix = []
for idx, b in enumerate(selected_branches, start=1):
    b_name = b["BRANCH"]
    e = db["entries"].get(b_name, {})

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

    # Auto-Calculate Live Closing Balance
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

col_head1, col_head2 = st.columns([3.5, 1])

with col_head1:
    st.markdown(f'<div class="main-title">📊 HAPPI MOBILES - MASTER CASHBOOK WORKSPACE <span style="font-size: 13px; color: #16a34a; font-weight: bold;">● Cloud Synced Real-Time</span></div>', unsafe_allow_html=True)

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
    height=780,
    disabled=["Sl.No.", "CODE", "BRANCH", "CLOSING BALANCE"],
    column_config=column_config,
    num_rows="fixed",
    key="master_live_editor"
)

# Sync edits back to server storage immediately
has_changes = False
for _, row in edited_df.iterrows():
    b_name = row["BRANCH"]
    store_entry = db["entries"].setdefault(b_name, {})
    for col in ["OPENING BALANCE", "DEPOSIT", "DENOMINATION", "AddinGS", "PENDING APPRVLS", "FINANCE AMNT", "SR", "SWEEPER SALARY", "EDITS", "APX SHORTAGE", "(KSP)'Sir's Approvals", "REMARKS"]:
        val = str(row[col]) if pd.notna(row[col]) else ""
        if store_entry.get(col, "") != val:
            store_entry[col] = val
            has_changes = True

if has_changes:
    save_db()
    st.rerun()
