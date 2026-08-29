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
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(page_title="Happi Cashbook Master", layout="wide")

st.markdown("""
    <style>
    .header-style { font-size: 24px; font-weight: bold; color: #0E4C92; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-style">🏢 HAPPI MOBILES - HEAD OFFICE MASTER CASHBOOK AUTOMATION</div>', unsafe_allow_html=True)

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

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "addins_key" not in st.session_state:
    st.session_state.addins_key = 0

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "branches": sorted(DEFAULT_BRANCHES, key=lambda x: x["BRANCH"].upper()),
        "ho_balances": {},
        "addins_data": {},
        "store_data": {},
        "manual_edits": {},
        "metadata": {}
    }

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

db = load_db()
if "addins_data" not in db:
    db["addins_data"] = {}

# --- WORK ASSIGNMENT / CASHIER SPLIT SIDEBAR ---
st.sidebar.title("👥 Work Assignment")
work_mode = st.sidebar.radio(
    "Select Work Mode:",
    ["👤 Single Cashier (All Stores)", "👥 Two Cashiers (Split 50-50)"]
)

all_branches = db["branches"]
total_branches_count = len(all_branches)
selected_branches = all_branches

if work_mode == "👥 Two Cashiers (Split 50-50)":
    mid_point = math.ceil(total_branches_count / 2)
    c1_branches = all_branches[:mid_point]
    c2_branches = all_branches[mid_point:]
    
    c1_label = f"Cashier 1 ({len(c1_branches)} Stores: {c1_branches[0]['BRANCH']} to {c1_branches[-1]['BRANCH']})"
    c2_label = f"Cashier 2 ({len(c2_branches)} Stores: {c2_branches[0]['BRANCH']} to {c2_branches[-1]['BRANCH']})"
    
    cashier_view = st.sidebar.selectbox("Choose Your Cashier Assignment:", [c1_label, c2_label])
    
    if cashier_view == c1_label:
        selected_branches = c1_branches
        st.sidebar.success(f"Loaded Cashier 1: **{len(selected_branches)}** Stores")
    else:
        selected_branches = c2_branches
        st.sidebar.success(f"Loaded Cashier 2: **{len(selected_branches)}** Stores")
else:
    st.sidebar.info(f"Loaded All: **{len(selected_branches)}** Stores")

# --- HELPER FUNCTIONS ---
def format_excel_formula(num_list):
    if not num_list:
        return ""
    clean_ints = [str(int(x)) for x in num_list if x > 0]
    if not clean_ints:
        return ""
    if len(clean_ints) == 1:
        return clean_ints[0]
    return "=" + "+".join(clean_ints)

def normalize_name(s):
    if not s:
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", str(s)).upper()

def process_cashbook_image(pil_img, target_branch):
    """Ultra-lightweight OCR using Tesseract."""
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

    f_denom = str(denom_val) if denom_val else ""
    f_pending = format_excel_formula(pending_apprvls)
    f_finance = format_excel_formula(finance_amnt)
    f_sr = format_excel_formula(sr_list)
    f_edits = format_excel_formula(edits_list)
    f_ksp = format_excel_formula(ksp_approvals)

    db["store_data"][target_branch] = {
        "DENOMINATION": f_denom,
        "PENDING APPRVLS": f_pending,
        "FINANCE AMNT": f_finance,
        "SR": f_sr,
        "EDITS": f_edits,
        "(KSP)'Sir's Approvals": f_ksp
    }
    
    if target_branch not in db["manual_edits"]:
        db["manual_edits"][target_branch] = {}
        
    db["manual_edits"][target_branch]["DENOMINATION"] = f_denom
    db["manual_edits"][target_branch]["PENDING APPRVLS"] = f_pending
    db["manual_edits"][target_branch]["FINANCE AMNT"] = f_finance
    db["manual_edits"][target_branch]["SR"] = f_sr
    db["manual_edits"][target_branch]["EDITS"] = f_edits
    db["manual_edits"][target_branch]["(KSP)'Sir's Approvals"] = f_ksp
    db["manual_edits"][target_branch]["CLOSING BALANCE"] = ""
    db["manual_edits"][target_branch]["DEPOSIT"] = ""
    
    save_db(db)

# --- 4 DATA INGESTION COLUMNS ---
c_ingest1, c_ingest2, c_ingest3, c_ingest4 = st.columns([1, 1, 1, 1.2])

with c_ingest1:
    ho_dump_file = st.file_uploader("📂 1. Apex Dr Balance File", type=["xlsx", "xls", "csv"], key=f"ho_dump_{st.session_state.uploader_key}")

with c_ingest2:
    addins_dump_file = st.file_uploader("📥 2. Addins Excel/CSV Dump", type=["xlsx", "xls", "csv"], key=f"addins_dump_{st.session_state.addins_key}")

with c_ingest3:
    uploaded_files = st.file_uploader("📁 3. Batch Screenshots (OCR)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="store_screenshots_uploader")

with c_ingest4:
    with st.expander("📸 4. Single Snip OCR Ingestion", expanded=True):
        target_branch_name = st.selectbox("Target Store:", [b["BRANCH"] for b in selected_branches], key="snip_paste_store")
        single_snip_file = st.file_uploader(f"Upload Snip for [{target_branch_name}]", type=["png", "jpg", "jpeg"], key=f"single_snip_{target_branch_name}")
        if single_snip_file:
            image = Image.open(single_snip_file)
            with st.spinner(f"Mapping cashbook to {target_branch_name}..."):
                process_cashbook_image(image, target_branch_name)
                st.success(f"✅ Mapped to **{target_branch_name}** successfully!")
                st.rerun()

# --- PROCESS ADDINS DUMP FILE ---
if addins_dump_file:
    current_addins_id = f"{addins_dump_file.name}_{addins_dump_file.size}"
    if st.session_state.get("last_addins_file") != current_addins_id:
        try:
            if addins_dump_file.name.endswith(".csv"):
                df_addins = pd.read_csv(addins_dump_file)
            else:
                df_addins = pd.read_excel(addins_dump_file)

            branch_col, amt_col = None, None
            for col in df_addins.columns:
                c_low = str(col).lower()
                if "branch" in c_low or "store" in c_low or "name" in c_low:
                    branch_col = col
                elif "amount" in c_low or "amt" in c_low or "value" in c_low or "total" in c_low or "addin" in c_low:
                    amt_col = col

            if branch_col is None:
                branch_col = df_addins.columns[0]
            if amt_col is None:
                amt_col = df_addins.columns[1] if len(df_addins.columns) > 1 else df_addins.columns[0]

            addins_dict = {}
            for idx, row in df_addins.iterrows():
                b_val = normalize_name(row[branch_col])
                raw_amt = str(row[amt_col]).replace(",", "").strip()
                match = re.search(r"(\d+\.?\d*)", raw_amt)
                if match:
                    clean_amt = int(round(float(match.group(1))))
                    if b_val and clean_amt > 0:
                        if b_val not in addins_dict:
                            addins_dict[b_val] = []
                        addins_dict[b_val].append(clean_amt)

            mapped_count = 0
            for b in db["branches"]:
                b_norm = normalize_name(b["BRANCH"])
                b_code_norm = normalize_name(b["CODE"])
                
                vouchers = []
                if b_norm in addins_dict:
                    vouchers = addins_dict[b_norm]
                elif b_code_norm in addins_dict:
                    vouchers = addins_dict[b_code_norm]

                if vouchers:
                    formula_val = format_excel_formula(vouchers)
                    db["addins_data"][b["BRANCH"]] = formula_val
                    if b["BRANCH"] not in db["manual_edits"]:
                        db["manual_edits"][b["BRANCH"]] = {}
                    db["manual_edits"][b["BRANCH"]]["AddinGS"] = formula_val
                    mapped_count += 1

            save_db(db)
            st.session_state.last_addins_file = current_addins_id
            st.success(f"✅ Successfully mapped Addins for **{mapped_count}** stores!")
            st.rerun()

        except Exception as e:
            st.error(f"Error reading Addins file: {e}")

# Process HO Dump File
if ho_dump_file:
    current_file_id = f"{ho_dump_file.name}_{ho_dump_file.size}"
    if st.session_state.get("last_processed_file") != current_file_id:
        try:
            if ho_dump_file.name.endswith(".csv"):
                df_dump = pd.read_csv(ho_dump_file)
            else:
                df_dump = pd.read_excel(ho_dump_file)

            branch_col, bal_col = None, None
            for col in df_dump.columns:
                c_low = str(col).lower()
                if "branch" in c_low or "store" in c_low or "name" in c_low:
                    branch_col = col
                elif "balance" in c_low or "opening" in c_low or "dr" in c_low or "amount" in c_low:
                    bal_col = col

            if branch_col is None:
                branch_col = df_dump.columns[0]
            if bal_col is None:
                bal_col = df_dump.columns[1] if len(df_dump.columns) > 1 else df_dump.columns[0]

            dump_dict = {}
            for idx, row in df_dump.iterrows():
                b_val = normalize_name(row[branch_col])
                raw_amt = str(row[bal_col]).replace(",", "").strip()
                match = re.search(r"(\d+\.?\d*)", raw_amt)
                if match:
                    clean_amt = int(round(float(match.group(1))))
                    if b_val and clean_amt is not None:
                        dump_dict[b_val] = clean_amt

            for b in db["branches"]:
                b_norm = normalize_name(b["BRANCH"])
                b_code_norm = normalize_name(b["CODE"])

                if b_norm in dump_dict:
                    db["ho_balances"][b["BRANCH"]] = dump_dict[b_norm]
                    if b["BRANCH"] not in db["manual_edits"]:
                        db["manual_edits"][b["BRANCH"]] = {}
                    db["manual_edits"][b["BRANCH"]]["OPENING BALANCE"] = str(dump_dict[b_norm])
                elif b_code_norm in dump_dict:
                    db["ho_balances"][b["BRANCH"]] = dump_dict[b_code_norm]
                    if b["BRANCH"] not in db["manual_edits"]:
                        db["manual_edits"][b["BRANCH"]] = {}
                    db["manual_edits"][b["BRANCH"]]["OPENING BALANCE"] = str(dump_dict[b_code_norm])

            save_db(db)
            st.session_state.last_processed_file = current_file_id
            st.rerun()
        except Exception as e:
            st.error(f"Error reading HO Dump file: {e}")

# Process Batch Screenshots (OCR)
if uploaded_files:
    with st.spinner("Processing screenshots and mapping data..."):
        for file in uploaded_files:
            image = Image.open(file)
            text_sample = pytesseract.image_to_string(image).lower()

            matched_branch = None
            for b in db["branches"]:
                b_name_clean = b["BRANCH"].lower()
                b_code_clean = b["CODE"].lower()
                file_clean = file.name.lower()

                if b_code_clean in file_clean or b_name_clean in file_clean:
                    matched_branch = b["BRANCH"]
                    break
                elif b_name_clean in text_sample or b_code_clean in text_sample:
                    matched_branch = b["BRANCH"]
                    break

            if matched_branch:
                process_cashbook_image(image, matched_branch)

# --- CONVERT VALUES ---
def prepare_cell_value(val):
    if not val:
        return ""
    return str(val).strip()

headers = [
    "Sl.No.", "CODE", "BRANCH", "OPENING BALANCE", "DEPOSIT", "DENOMINATION", 
    "AddinGS", "PENDING APPRVLS", "FINANCE AMNT", "SR", "SWEEPER SALARY", 
    "EDITS", "APX SHORTAGE", "(KSP)'Sir's Approvals", "CLOSING BALANCE", "REMARKS"
]

grid_rows = []
for idx, b in enumerate(selected_branches, start=1):
    b_name = b["BRANCH"]
    d = db["store_data"].get(b_name, {})
    opening_bal = db["ho_balances"].get(b_name, "")
    addins_val = db["addins_data"].get(b_name, "")
    manual = db["manual_edits"].get(b_name, {})

    row_data = [
        str(idx),
        b["CODE"],
        b["BRANCH"],
        prepare_cell_value(manual.get("OPENING BALANCE", str(opening_bal))),
        prepare_cell_value(manual.get("DEPOSIT", "")),
        prepare_cell_value(manual.get("DENOMINATION", str(d.get("DENOMINATION", "")))),
        prepare_cell_value(manual.get("AddinGS", str(addins_val))),
        prepare_cell_value(manual.get("PENDING APPRVLS", str(d.get("PENDING APPRVLS", "")))),
        prepare_cell_value(manual.get("FINANCE AMNT", str(d.get("FINANCE AMNT", "")))),
        prepare_cell_value(manual.get("SR", str(d.get("SR", "")))),
        prepare_cell_value(manual.get("SWEEPER SALARY", "")),
        prepare_cell_value(manual.get("EDITS", str(d.get("EDITS", "")))),
        prepare_cell_value(manual.get("APX SHORTAGE", "")),
        prepare_cell_value(manual.get("(KSP)'Sir's Approvals", str(d.get("(KSP)'Sir's Approvals", "")))),
        prepare_cell_value(manual.get("CLOSING BALANCE", "")),
        manual.get("REMARKS", "")
    ]
    grid_rows.append(row_data)

st.subheader(f"📊 Head Office Master Cashbook ({len(selected_branches)} Stores Shown)")

# Robust Full Formula-Engine Grid
hot_html = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.css">
    <script src="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }}
        #excelGrid {{ width: 100%; height: 530px; overflow: hidden; font-size: 13px; }}
        .handsontable th {{ background-color: #0E4C92 !important; color: white !important; font-weight: bold; height: 28px; text-align: center; }}
        .handsontable td {{ font-size: 12px; }}
    </style>
</head>
<body>
    <div id="excelGrid"></div>
    <script>
        const container = document.getElementById('excelGrid');
        let rawData = {json.dumps(grid_rows)};
        const headers = {json.dumps(headers)};

        function colLetterToIndex(str) {{
            let num = 0;
            for (let i = 0; i < str.length; i++) {{
                num = num * 26 + (str.charCodeAt(i) - 64);
            }}
            return num - 1;
        }}

        function indexToColLetter(colIndex) {{
            let letter = '';
            while (colIndex >= 0) {{
                letter = String.fromCharCode((colIndex % 26) + 65) + letter;
                colIndex = Math.floor(colIndex / 26) - 1;
            }}
            return letter;
        }}

        function evaluateFormula(val, row, col, tableData) {{
            if (!val || typeof val !== 'string' || !val.startsWith('=')) return val;
            let expr = val.substring(1).trim().toUpperCase();

            try {{
                // Handle SUM(Range) or SUM(A, B, C)
                if (expr.startsWith('SUM(') && expr.endsWith(')')) {{
                    let inner = expr.substring(4, expr.length - 1);
                    let sum = 0;
                    if (inner.includes(':')) {{
                        let parts = inner.split(':');
                        let m1 = parts[0].match(/([A-Z]+)(\\d+)/);
                        let m2 = parts[1].match(/([A-Z]+)(\\d+)/);
                        if (m1 && m2) {{
                            let startCol = colLetterToIndex(m1[1]);
                            let startRow = parseInt(m1[2]) - 1;
                            let endCol = colLetterToIndex(m2[1]);
                            let endRow = parseInt(m2[2]) - 1;

                            for (let r = Math.min(startRow, endRow); r <= Math.max(startRow, endRow); r++) {{
                                for (let c = Math.min(startCol, endCol); c <= Math.max(startCol, endCol); c++) {{
                                    if (tableData[r] && tableData[r][c] !== undefined) {{
                                        let cellVal = evaluateFormula(tableData[r][c], r, c, tableData);
                                        let num = parseFloat(String(cellVal).replace(/,/g, ''));
                                        if (!isNaN(num)) sum += num;
                                    }}
                                }}
                            }}
                            return sum;
                        }}
                    }}
                }}

                // Handle cell references like D1 + E1 - F1
                let resolved = expr.replace(/([A-Z]+)(\\d+)/g, function(match, colStr, rowStr) {{
                    let c = colLetterToIndex(colStr);
                    let r = parseInt(rowStr) - 1;
                    if (tableData[r] && tableData[r][c] !== undefined) {{
                        let cellVal = evaluateFormula(tableData[r][c], r, c, tableData);
                        let num = parseFloat(String(cellVal).replace(/,/g, ''));
                        return isNaN(num) ? 0 : num;
                    }}
                    return 0;
                }});

                // Math eval safely
                if (/^[0-9+\\-*\\/().\\s]+$/.test(resolved)) {{
                    let result = Function('"use strict";return (' + resolved + ')')();
                    return Math.round(result * 100) / 100;
                }}
            }} catch (e) {{
                return '#ERROR!';
            }}
            return val;
        }}

        // Custom Renderer for Excel view
        function excelRenderer(instance, td, row, col, prop, value, cellProperties) {{
            Handsontable.renderers.TextRenderer.apply(this, arguments);
            if (value && String(value).startsWith('=')) {{
                let evaluated = evaluateFormula(value, row, col, instance.getData());
                td.innerText = evaluated;
                td.style.fontWeight = '500';
            }}
        }}

        const hot = new Handsontable(container, {{
            data: rawData,
            colHeaders: headers,
            rowHeaders: true,
            height: 520,
            width: '100%',
            cells: function(row, col) {{
                return {{ renderer: excelRenderer }};
            }},
            columns: [
                {{ readOnly: true, className: 'htCenter' }},
                {{ readOnly: true, className: 'htCenter' }},
                {{ readOnly: true }},
                {{ type: 'text' }},
                {{ type: 'text' }},
                {{ type: 'text' }},
                {{ type: 'text' }},
                {{ type: 'text' }},
                {{ type: 'text' }},
                {{ type: 'text' }},
                {{ type: 'text' }},
                {{ type: 'text' }},
                {{ type: 'text' }},
                {{ type: 'text' }},
                {{ type: 'text' }},
                {{ type: 'text' }}
            ],
            stretchH: 'all',
            manualColumnResize: true,
            manualRowResize: true,
            contextMenu: true,
            autoWrapRow: true,
            autoWrapCol: true,
            copyPaste: true,
            undo: true,
            selectionMode: 'multiple',
            licenseKey: 'non-commercial-and-evaluation'
        }});

        // Excel cell selection while formula typing
        hot.addHook('afterOnCellMouseDown', function(event, coords) {{
            const editor = hot.getActiveEditor();
            if (editor && editor.isOpened() && editor.TEXTAREA) {{
                let val = editor.TEXTAREA.value;
                if (val && val.startsWith('=')) {{
                    const cellLetter = indexToColLetter(coords.col) + (coords.row + 1);
                    if (val.endsWith('(') || val.endsWith(',') || val.endsWith('+') || val.endsWith('-') || val.endsWith('*') || val.endsWith('/')) {{
                        editor.TEXTAREA.value = val + cellLetter;
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

components.html(hot_html, height=550)

# Export and Reset options
c_down, c_reset_dr, c_reset_addins, c_reset_all = st.columns([2.5, 1, 1, 1.2])

with c_down:
    all_rows_export = []
    for idx, b in enumerate(db["branches"], start=1):
        b_name = b["BRANCH"]
        d = db["store_data"].get(b_name, {})
        opening_bal = db["ho_balances"].get(b_name, "")
        addins_val = db["addins_data"].get(b_name, "")
        manual = db["manual_edits"].get(b_name, {})

        all_rows_export.append({
            "Sl.No.": idx,
            "CODE": b["CODE"],
            "BRANCH": b["BRANCH"],
            "OPENING BALANCE": manual.get("OPENING BALANCE", str(opening_bal)),
            "DEPOSIT": manual.get("DEPOSIT", ""),
            "DENOMINATION": manual.get("DENOMINATION", str(d.get("DENOMINATION", ""))),
            "AddinGS": manual.get("AddinGS", str(addins_val)),
            "PENDING APPRVLS": manual.get("PENDING APPRVLS", str(d.get("PENDING APPRVLS", ""))),
            "FINANCE AMNT": manual.get("FINANCE AMNT", str(d.get("FINANCE AMNT", ""))),
            "SR": manual.get("SR", str(d.get("SR", ""))),
            "SWEEPER SALARY": manual.get("SWEEPER SALARY", ""),
            "EDITS": manual.get("EDITS", str(d.get("EDITS", ""))),
            "APX SHORTAGE": manual.get("APX SHORTAGE", ""),
            "(KSP)'Sir's Approvals": manual.get("(KSP)'Sir's Approvals", str(d.get("(KSP)'Sir's Approvals", "")) ),
            "CLOSING BALANCE": manual.get("CLOSING BALANCE", ""),
            "REMARKS": manual.get("REMARKS", "")
        })

    df_full_export = pd.DataFrame(all_rows_export)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_full_export.to_excel(writer, index=False, sheet_name='MASTER REPORT')
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Download Full Master Excel Sheet",
        data=excel_data,
        file_name="HO_MASTER_CASHBOOK_REPORT.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with c_reset_dr:
    if st.button("🗑️ Clear Dr Balances", use_container_width=True):
        db["ho_balances"] = {}
        for b_name in db["manual_edits"]:
            db["manual_edits"][b_name]["OPENING BALANCE"] = ""
        save_db(db)
        st.session_state.uploader_key += 1
        if "last_processed_file" in st.session_state:
            del st.session_state["last_processed_file"]
        st.rerun()

with c_reset_addins:
    if st.button("🗑️ Clear Addins Only", use_container_width=True):
        db["addins_data"] = {}
        for b_name in db["manual_edits"]:
            db["manual_edits"][b_name]["AddinGS"] = ""
        save_db(db)
        st.session_state.addins_key += 1
        if "last_addins_file" in st.session_state:
            del st.session_state["last_addins_file"]
        st.rerun()

with c_reset_all:
    if st.button("🧹 Reset All Store Entries", use_container_width=True):
        db["store_data"] = {}
        db["manual_edits"] = {}
        db["metadata"] = {}
        save_db(db)
        st.success("Cleaned all store records!")
        st.rerun()
