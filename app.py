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
        padding-top: 0.8rem !important; 
        padding-bottom: 0rem !important; 
        padding-left: 1.2rem !important; 
        padding-right: 1.2rem !important; 
        max-width: 100% !important;
    }
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .main-title { 
        font-size: 18px; 
        font-weight: 700; 
        color: #0E4C92; 
        margin-bottom: 8px; 
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
        "manual_edits": {}
    }

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

db = load_db()

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
    
    save_db(db)

# --- SIDEBAR: SMART ENTERPRISE CONTROL PANEL ---
with st.sidebar:
    st.markdown("### 🏢 Happi Control Hub")
    
    work_mode = st.radio(
        "Assignment Mode:",
        ["👤 Single Cashier (All Stores)", "👥 Two Cashiers (Split 50-50)"],
        label_visibility="collapsed"
    )

    all_branches = db["branches"]
    total_branches_count = len(all_branches)
    selected_branches = all_branches

    if work_mode == "👥 Two Cashiers (Split 50-50)":
        mid_point = math.ceil(total_branches_count / 2)
        c1_branches = all_branches[:mid_point]
        c2_branches = all_branches[mid_point:]
        
        c1_label = f"Cashier 1 ({len(c1_branches)} Stores)"
        c2_label = f"Cashier 2 ({len(c2_branches)} Stores)"
        
        cashier_view = st.selectbox("Current Cashier:", [c1_label, c2_label])
        if cashier_view == c1_label:
            selected_branches = c1_branches
        else:
            selected_branches = c2_branches

    st.markdown("---")
    with st.expander("📸 1. Single Store Snip (OCR)", expanded=True):
        target_branch_name = st.selectbox("Target Store:", [b["BRANCH"] for b in selected_branches], key="snip_paste_store")
        single_snip_file = st.file_uploader("Upload Cashbook Snip", type=["png", "jpg", "jpeg"], key=f"single_snip_{target_branch_name}")
        if single_snip_file:
            image = Image.open(single_snip_file)
            with st.spinner(f"Mapping {target_branch_name}..."):
                process_cashbook_image(image, target_branch_name)
                st.success(f"✅ Mapped to {target_branch_name}!")
                st.rerun()

    with st.expander("📂 2. Apex Dr Balance File", expanded=False):
        ho_dump_file = st.file_uploader("Upload Apex File", type=["xlsx", "xls", "csv"], key=f"ho_dump_{st.session_state.uploader_key}")

    with st.expander("📥 3. Addins Dump File", expanded=False):
        addins_dump_file = st.file_uploader("Upload Addins File", type=["xlsx", "xls", "csv"], key=f"addins_dump_{st.session_state.addins_key}")

    with st.expander("📁 4. Batch Screenshots OCR", expanded=False):
        uploaded_files = st.file_uploader("Upload Batch Snips", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="store_screenshots_uploader")

    st.markdown("---")
    st.markdown("#### ⚙️ Data Actions")
    if st.button("🗑️ Clear Dr Balances", use_container_width=True):
        db["ho_balances"] = {}
        for b_name in db["manual_edits"]:
            db["manual_edits"][b_name]["OPENING BALANCE"] = ""
        save_db(db)
        st.session_state.uploader_key += 1
        st.rerun()

    if st.button("🗑️ Clear Addins Only", use_container_width=True):
        db["addins_data"] = {}
        for b_name in db["manual_edits"]:
            db["manual_edits"][b_name]["AddinGS"] = ""
        save_db(db)
        st.session_state.addins_key += 1
        st.rerun()

    if st.button("🧹 Reset All Store Records", use_container_width=True):
        db["store_data"] = {}
        db["manual_edits"] = {}
        save_db(db)
        st.rerun()

# --- BACKGROUND DATA PROCESSING ---
if addins_dump_file:
    current_addins_id = f"{addins_dump_file.name}_{addins_dump_file.size}"
    if st.session_state.get("last_addins_file") != current_addins_id:
        try:
            df_addins = pd.read_csv(addins_dump_file) if addins_dump_file.name.endswith(".csv") else pd.read_excel(addins_dump_file)
            branch_col, amt_col = None, None
            for col in df_addins.columns:
                c_low = str(col).lower()
                if "branch" in c_low or "store" in c_low or "name" in c_low: branch_col = col
                elif "amount" in c_low or "amt" in c_low or "value" in c_low or "total" in c_low or "addin" in c_low: amt_col = col
            if branch_col is None: branch_col = df_addins.columns[0]
            if amt_col is None: amt_col = df_addins.columns[1] if len(df_addins.columns) > 1 else df_addins.columns[0]

            addins_dict = {}
            for idx, row in df_addins.iterrows():
                b_val = normalize_name(row[branch_col])
                raw_amt = str(row[amt_col]).replace(",", "").strip()
                match = re.search(r"(\d+\.?\d*)", raw_amt)
                if match:
                    clean_amt = int(round(float(match.group(1))))
                    if b_val and clean_amt > 0:
                        if b_val not in addins_dict: addins_dict[b_val] = []
                        addins_dict[b_val].append(clean_amt)

            for b in db["branches"]:
                b_norm, b_code_norm = normalize_name(b["BRANCH"]), normalize_name(b["CODE"])
                vouchers = addins_dict.get(b_norm, addins_dict.get(b_code_norm, []))
                if vouchers:
                    formula_val = format_excel_formula(vouchers)
                    db["addins_data"][b["BRANCH"]] = formula_val
                    if b["BRANCH"] not in db["manual_edits"]: db["manual_edits"][b["BRANCH"]] = {}
                    db["manual_edits"][b["BRANCH"]]["AddinGS"] = formula_val

            save_db(db)
            st.session_state.last_addins_file = current_addins_id
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error Addins: {e}")

if ho_dump_file:
    current_file_id = f"{ho_dump_file.name}_{ho_dump_file.size}"
    if st.session_state.get("last_processed_file") != current_file_id:
        try:
            df_dump = pd.read_csv(ho_dump_file) if ho_dump_file.name.endswith(".csv") else pd.read_excel(ho_dump_file)
            branch_col, bal_col = None, None
            for col in df_dump.columns:
                c_low = str(col).lower()
                if "branch" in c_low or "store" in c_low or "name" in c_low: branch_col = col
                elif "balance" in c_low or "opening" in c_low or "dr" in c_low or "amount" in c_low: bal_col = col
            if branch_col is None: branch_col = df_dump.columns[0]
            if bal_col is None: bal_col = df_dump.columns[1] if len(df_dump.columns) > 1 else df_dump.columns[0]

            dump_dict = {}
            for idx, row in df_dump.iterrows():
                b_val = normalize_name(row[branch_col])
                raw_amt = str(row[bal_col]).replace(",", "").strip()
                match = re.search(r"(\d+\.?\d*)", raw_amt)
                if match:
                    clean_amt = int(round(float(match.group(1))))
                    if b_val and clean_amt is not None: dump_dict[b_val] = clean_amt

            for b in db["branches"]:
                b_norm, b_code_norm = normalize_name(b["BRANCH"]), normalize_name(b["CODE"])
                if b_norm in dump_dict or b_code_norm in dump_dict:
                    val = dump_dict.get(b_norm, dump_dict.get(b_code_norm))
                    db["ho_balances"][b["BRANCH"]] = val
                    if b["BRANCH"] not in db["manual_edits"]: db["manual_edits"][b["BRANCH"]] = {}
                    db["manual_edits"][b["BRANCH"]]["OPENING BALANCE"] = str(val)

            save_db(db)
            st.session_state.last_processed_file = current_file_id
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error Apex File: {e}")

if uploaded_files:
    for file in uploaded_files:
        image = Image.open(file)
        text_sample = pytesseract.image_to_string(image).lower()
        matched_branch = None
        for b in db["branches"]:
            b_name_clean, b_code_clean, file_clean = b["BRANCH"].lower(), b["CODE"].lower(), file.name.lower()
            if b_code_clean in file_clean or b_name_clean in file_clean or b_name_clean in text_sample or b_code_clean in text_sample:
                matched_branch = b["BRANCH"]
                break
        if matched_branch:
            process_cashbook_image(image, matched_branch)

# --- TOP HEADER & DOWNLOAD BAR ---
col_head1, col_head2 = st.columns([3.5, 1])

with col_head1:
    st.markdown(f'<div class="main-title">📊 HAPPI MOBILES - MASTER CASHBOOK WORKSPACE <span style="font-size: 13px; color: #64748b; font-weight: normal;">({len(selected_branches)} Stores Active)</span></div>', unsafe_allow_html=True)

# Build Dynamic Matrix with Auto-Calculating Closing Balance
final_rows = []
for idx, b in enumerate(selected_branches, start=1):
    b_name = b["BRANCH"]
    d = db["store_data"].get(b_name, {})
    opening_bal = db["ho_balances"].get(b_name, "")
    addins_val = db["addins_data"].get(b_name, "")
    manual = db["manual_edits"].get(b_name, {})

    # Auto calculate Excel Formula: =D2-SUM(E2:N2)
    excel_row_num = idx + 1
    default_closing_formula = f"=D{excel_row_num}-SUM(E{excel_row_num}:N{excel_row_num})"

    final_rows.append({
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
        "(KSP)'Sir's Approvals": manual.get("(KSP)'Sir's Approvals", str(d.get("(KSP)'Sir's Approvals", ""))),
        "CLOSING BALANCE": manual.get("CLOSING BALANCE", default_closing_formula),
        "REMARKS": manual.get("REMARKS", "")
    })

df_master = pd.DataFrame(final_rows)

with col_head2:
    all_rows_export = []
    for idx, b in enumerate(db["branches"], start=1):
        b_name = b["BRANCH"]
        d = db["store_data"].get(b_name, {})
        opening_bal = db["ho_balances"].get(b_name, "")
        addins_val = db["addins_data"].get(b_name, "")
        manual = db["manual_edits"].get(b_name, {})
        excel_row_num = idx + 1
        default_closing_formula = f"=D{excel_row_num}-SUM(E{excel_row_num}:N{excel_row_num})"

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
            "CLOSING BALANCE": manual.get("CLOSING BALANCE", default_closing_formula),
            "REMARKS": manual.get("REMARKS", "")
        })

    df_full_export = pd.DataFrame(all_rows_export)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_full_export.to_excel(writer, index=False, sheet_name='MASTER REPORT')
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Download Master Excel",
        data=excel_data,
        file_name="HO_MASTER_CASHBOOK_REPORT.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# --- NATIVE FULL PERSISTENT DATA GRID ---
column_config = {
    col: st.column_config.TextColumn(col)
    for col in [
        "OPENING BALANCE", "DEPOSIT", "DENOMINATION", "AddinGS", "PENDING APPRVLS",
        "FINANCE AMNT", "SR", "SWEEPER SALARY", "EDITS", "APX SHORTAGE",
        "(KSP)'Sir's Approvals", "CLOSING BALANCE", "REMARKS"
    ]
}

edited_df = st.data_editor(
    df_master,
    use_container_width=True,
    height=800,
    disabled=["Sl.No.", "CODE", "BRANCH"],
    column_config=column_config,
    num_rows="fixed",
    key=f"persistent_cashbook_{work_mode}_{len(selected_branches)}"
)

# REAL-TIME INSTANT SYNC TO SERVER DISK
changes_made = False
for idx, row in edited_df.iterrows():
    b_name = row["BRANCH"]
    if b_name not in db["manual_edits"]:
        db["manual_edits"][b_name] = {}

    for col in ["OPENING BALANCE", "DEPOSIT", "DENOMINATION", "AddinGS", "PENDING APPRVLS", "FINANCE AMNT", "SR", "SWEEPER SALARY", "EDITS", "APX SHORTAGE", "(KSP)'Sir's Approvals", "CLOSING BALANCE", "REMARKS"]:
        val_str = str(row[col]) if pd.notna(row[col]) else ""
        if db["manual_edits"][b_name].get(col) != val_str:
            db["manual_edits"][b_name][col] = val_str
            changes_made = True

if changes_made:
    save_db(db)
