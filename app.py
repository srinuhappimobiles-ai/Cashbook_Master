import io
import json
import math
import os
import re
import easyocr
import numpy as np
import pandas as pd
from PIL import Image
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

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

def process_cashbook_ocr(img_np, target_branch):
    """Accurately parses all voucher amounts and separates Finance, SR, Pending Approvals."""
    height, width = img_np.shape[:2]
    ocr_results = reader.readtext(img_np)
    
    boxes = []
    for bbox, text, conf in ocr_results:
        cx = (bbox[0][0] + bbox[1][0]) / 2
        cy = (bbox[0][1] + bbox[2][1]) / 2
        boxes.append({
            "x": cx, 
            "y": cy, 
            "text": text.strip()
        })

    # Find Vertical Boundary for Approvals Body
    y_start_approvals = 0
    y_end_approvals = height
    
    for b in boxes:
        t = b["text"].lower()
        if "add ins" in t or "addins" in t or "add in" in t:
            y_start_approvals = max(y_start_approvals, b["y"] + 8)
        elif "total approval" in t:
            y_end_approvals = min(y_end_approvals, b["y"] - 5)

    # 1. Denomination Total from right table (x > 65% width)
    denom_val = ""
    right_boxes = [b for b in boxes if b["x"] > width * 0.65]
    for b in right_boxes:
        if "total" in b["text"].lower():
            nums = [
                int(float(n.replace(",", ""))) 
                for nb in right_boxes 
                if abs(nb["y"] - b["y"]) <= 25 
                for n in re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", nb["text"])
            ]
            if nums:
                denom_val = str(nums[-1])
                break
                
    if not denom_val:
        for b in boxes:
            if "deposit" in b["text"].lower() and b["x"] < width * 0.65:
                nums = [int(float(n.replace(",", ""))) for n in re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", b["text"])]
                if nums:
                    denom_val = str(nums[-1])
                    break

    # 2. Group Left Table items into horizontal lines
    voucher_boxes = [b for b in boxes if y_start_approvals < b["y"] < y_end_approvals and b["x"] <= width * 0.70]
    voucher_boxes.sort(key=lambda b: b["y"])
    
    v_rows = []
    for b in voucher_boxes:
        placed = False
        for r in v_rows:
            if abs(r["y"] - b["y"]) <= 22:
                r["items"].append(b)
                r["y"] = sum(i["y"] for i in r["items"]) / len(r["items"])
                placed = True
                break
        if not placed:
            v_rows.append({"y": b["y"], "items": [b]})

    pending_apprvls = []
    finance_amnt = []
    sr_list = []
    edits_list = []
    ksp_approvals = []

    for r in v_rows:
        r["items"].sort(key=lambda item: item["x"])
        full_line = " ".join([i["text"] for i in r["items"]])
        full_line_lower = full_line.lower()
        
        # Clean out dates & invoice codes so only real numbers remain
        cleaned_for_nums = re.sub(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", " ", full_line)
        cleaned_for_nums = re.sub(r"\b[A-Za-z0-9]+/[A-Za-z0-9]+/\d+\b", " ", cleaned_for_nums)
        cleaned_for_nums = re.sub(r"\b[A-Za-z0-9]+/\d+\b", " ", cleaned_for_nums)
        
        nums_found = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", cleaned_for_nums)
        clean_nums = []
        for n in nums_found:
            val = float(n.replace(",", ""))
            if val > 0 and val not in [2000, 500, 200, 100, 50, 20, 10, 5]:
                clean_nums.append(int(round(val)))
            elif val > 0 and (val >= 1000 or (val in [500, 200, 100, 50, 20, 10] and len(clean_nums) == 0)):
                clean_nums.append(int(round(val)))
                
        if clean_nums:
            target_amount = clean_nums[-1]
            
            # Categorize based on text keywords
            if any(k in full_line_lower for k in ["bajaj", "idfc", "cash back", "cashback", "cash to card", "upi", "dbd", "finance"]):
                finance_amnt.append(target_amount)
            elif any(k in full_line_lower for k in ["sales return", "sale return", "srn", "sr/", "doa", "return", "sr "]):
                sr_list.append(target_amount)
            elif any(k in full_line_lower for k in ["pavan", "santhosh", "sharan"]):
                ksp_approvals.append(target_amount)
            elif "extra" in full_line_lower or "edit" in full_line_lower:
                edits_list.append(target_amount)
            else:
                pending_apprvls.append(target_amount)

    f_denom = str(denom_val) if denom_val else ""
    f_pending = format_excel_formula(pending_apprvls)
    f_finance = format_excel_formula(finance_amnt)
    f_sr = format_excel_formula(sr_list)
    f_edits = format_excel_formula(edits_list)
    f_ksp = format_excel_formula(ksp_approvals)

    # Overwrite in database
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
    ho_dump_file = st.file_uploader(
        "📂 1. Apex Dr Balance File", 
        type=["xlsx", "xls", "csv"],
        key=f"ho_dump_{st.session_state.uploader_key}"
    )

with c_ingest2:
    addins_dump_file = st.file_uploader(
        "📥 2. Addins Excel/CSV Dump",
        type=["xlsx", "xls", "csv"],
        key=f"addins_dump_{st.session_state.addins_key}"
    )

with c_ingest3:
    uploaded_files = st.file_uploader(
        "📁 3. Batch Screenshots (OCR)", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True,
        key="store_screenshots_uploader"
    )

with c_ingest4:
    with st.expander("📸 4. Single Snip OCR Ingestion", expanded=True):
        target_branch_name = st.selectbox("Target Store:", [b["BRANCH"] for b in selected_branches], key="snip_paste_store")
        single_snip_file = st.file_uploader(
            f"Upload Snip for [{target_branch_name}]",
            type=["png", "jpg", "jpeg"],
            key=f"single_snip_{target_branch_name}"
        )
        if single_snip_file:
            image = Image.open(single_snip_file)
            img_np = np.array(image)
            with st.spinner(f"Mapping cashbook to {target_branch_name}..."):
                process_cashbook_ocr(img_np, target_branch_name)
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
            img_np = np.array(image)

            ocr_results = reader.readtext(img_np)
            full_text = " ".join([r[1] for r in ocr_results]).lower()

            matched_branch = None
            for b in db["branches"]:
                b_name_clean = b["BRANCH"].lower().replace(" ", "").replace("-", "")
                b_code_clean = b["CODE"].lower().replace("-", "")
                file_clean = file.name.lower().replace(" ", "").replace("-", "").replace("_", "")
                full_clean = full_text.replace(" ", "").replace("-", "")

                if file_clean.startswith(b_code_clean) or b_name_clean in file_clean:
                    matched_branch = b["BRANCH"]
                    break
                elif b_name_clean in full_clean:
                    matched_branch = b["BRANCH"]
                    break

            if matched_branch:
                process_cashbook_ocr(img_np, matched_branch)

# --- BUILD EXCEL DATA GRID WITH REAL FORMULA ENGINE ---
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
        idx,
        b["CODE"],
        b["BRANCH"],
        manual.get("OPENING BALANCE", str(opening_bal)),
        manual.get("DEPOSIT", ""),
        manual.get("DENOMINATION", str(d.get("DENOMINATION", ""))),
        manual.get("AddinGS", str(addins_val)),
        manual.get("PENDING APPRVLS", str(d.get("PENDING APPRVLS", ""))),
        manual.get("FINANCE AMNT", str(d.get("FINANCE AMNT", ""))),
        manual.get("SR", str(d.get("SR", ""))),
        manual.get("SWEEPER SALARY", ""),
        manual.get("EDITS", str(d.get("EDITS", ""))),
        manual.get("APX SHORTAGE", ""),
        manual.get("(KSP)'Sir's Approvals", str(d.get("(KSP)'Sir's Approvals", ""))),
        manual.get("CLOSING BALANCE", ""),
        manual.get("REMARKS", "")
    ]
    grid_rows.append(row_data)

st.subheader(f"📊 Head Office Master Cashbook ({len(selected_branches)} Stores Shown)")

hot_html = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.css">
    <script src="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/hyperformula/dist/hyperformula.full.min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: sans-serif; }}
        #excelGrid {{ width: 100%; height: 530px; overflow: hidden; }}
        .handsontable th {{ background-color: #F0F2F6; font-weight: bold; color: #333; }}
    </style>
</head>
<body>
    <div id="excelGrid"></div>
    <script>
        const container = document.getElementById('excelGrid');
        const data = {json.dumps(grid_rows)};
        const headers = {json.dumps(headers)};

        const hyperformulaInstance = HyperFormula.buildEmpty({{
            licenseKey: 'internal-use-in-handsontable',
        }});

        const hot = new Handsontable(container, {{
            data: data,
            colHeaders: headers,
            rowHeaders: true,
            height: 520,
            width: '100%',
            formulas: {{
                engine: hyperformulaInstance,
            }},
            columns: [
                {{ readOnly: true }},
                {{ readOnly: true }},
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
            licenseKey: 'non-commercial-and-evaluation'
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
