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
    iframe { height: calc(100vh - 65px) !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

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

if "new_updates" not in st.session_state:
    st.session_state.new_updates = {}

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

    st.session_state.new_updates[target_branch] = {
        "DENOMINATION": denom_val,
        "PENDING APPRVLS": format_excel_formula(pending_apprvls),
        "FINANCE AMNT": format_excel_formula(finance_amnt),
        "SR": format_excel_formula(sr_list),
        "EDITS": format_excel_formula(edits_list),
        "(KSP)'Sir's Approvals": format_excel_formula(ksp_approvals)
    }

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("### 🏢 Happi Control Hub")
    
    work_mode = st.radio(
        "Assignment Mode:",
        ["👤 Single Cashier (All Stores)", "👥 Two Cashiers (Split 50-50)"],
        label_visibility="collapsed"
    )

    all_branches = sorted(DEFAULT_BRANCHES, key=lambda x: x["BRANCH"].upper())
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
                st.success(f"✅ Mapped {target_branch_name}!")
                st.rerun()

    with st.expander("📂 2. Apex Dr Balance File", expanded=False):
        ho_dump_file = st.file_uploader("Upload Apex File", type=["xlsx", "xls", "csv"], key="ho_dump")

    with st.expander("📥 3. Addins Dump File", expanded=False):
        addins_dump_file = st.file_uploader("Upload Addins File", type=["xlsx", "xls", "csv"], key="addins_dump")

    st.markdown("---")
    st.markdown("#### ⚙️ Data Actions")
    if st.button("🧹 Clear & Reset All Data", use_container_width=True):
        st.session_state.clear_local_storage = True
        st.session_state.new_updates = {}
        st.rerun()

# Process Ingestions into Session Updates
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
                st.session_state.new_updates.setdefault(b["BRANCH"], {})["AddinGS"] = format_excel_formula(vouchers)
        st.sidebar.success("✅ Addins Loaded!")
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
                st.session_state.new_updates.setdefault(b["BRANCH"], {})["OPENING BALANCE"] = str(val)
        st.sidebar.success("✅ Apex Dr Balances Loaded!")
    except Exception as e:
        st.sidebar.error(f"Apex Error: {e}")

# Header
st.markdown(f'<div class="main-title">📊 HAPPI MOBILES - MASTER CASHBOOK WORKSPACE <span style="font-size: 13px; color: #64748b; font-weight: normal;">({len(selected_branches)} Stores Active)</span></div>', unsafe_allow_html=True)

# Build Baseline Cell Matrix
headers = [
    "SL.No.", "CODE", "BRANCH", "OPENING BALANCE", "DEPOSIT", "DENOMINATION", 
    "AddinGS", "PENDING APPRVLS", "FINANCE AMNT", "SR", "SWEEPER SALARY", 
    "EDITS", "APX SHORTAGE", "(KSP)'Sir's Approvals", "CLOSING BALANCE", "REMARKS"
]

header_map = {name: idx for idx, name in enumerate(headers)}
baseline_celldata = []

for c_idx, h_text in enumerate(headers):
    baseline_celldata.append({
        "r": 0, "c": c_idx,
        "v": { "v": h_text, "m": h_text, "bg": "#1e7082", "fc": "#ffffff", "bl": 1, "ht": 0, "vt": 0 }
    })

for r_idx, b in enumerate(all_branches, start=1):
    excel_row_num = r_idx + 1
    default_closing_formula = f"=D{excel_row_num}-SUM(E{excel_row_num}:N{excel_row_num})"

    row_vals = [
        str(r_idx), b["CODE"], b["BRANCH"], "", "", "", "", "", "", "", "", "", "", "", default_closing_formula, ""
    ]

    for c_idx, val in enumerate(row_vals):
        if val:
            cell_obj = {"r": r_idx, "c": c_idx, "v": {}}
            if str(val).startswith("="):
                cell_obj["v"]["f"] = str(val)
            else:
                try:
                    num = float(str(val).replace(",", ""))
                    cell_obj["v"]["v"] = int(round(num)) if num.is_integer() else num
                    cell_obj["v"]["ct"] = {"fa": "General", "t": "n"}
                except:
                    cell_obj["v"]["v"] = str(val)
                    cell_obj["v"]["ct"] = {"fa": "General", "t": "g"}
            baseline_celldata.append(cell_obj)

# Prepare JSON payloads
branch_row_map = {b["BRANCH"]: idx + 1 for idx, b in enumerate(all_branches)}
new_updates_json = json.dumps(st.session_state.new_updates)
clear_flag = "true" if st.session_state.get("clear_local_storage", False) else "false"
if st.session_state.get("clear_local_storage", False):
    st.session_state.clear_local_storage = False

luckysheet_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/luckysheet/dist/plugins/css/pluginsCss.css' />
    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/luckysheet/dist/plugins/plugins.css' />
    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/luckysheet/dist/css/luckysheet.css' />
    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/luckysheet/dist/assets/iconfont/iconfont.css' />
    <script src="https://cdn.jsdelivr.net/npm/luckysheet/dist/plugins/js/plugin.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/luckysheet/dist/luckysheet.umd.js"></script>
    <style>
        html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; }}
        #luckysheet {{ margin: 0px; padding: 0px; position: absolute; width: 100%; height: 100%; left: 0px; top: 0px; }}
    </style>
</head>
<body>
    <div id="luckysheet"></div>
    <script>
        $(function () {{
            const STORAGE_KEY = "HAPPI_PERMANENT_MASTER_CASHBOOK_GRID";
            const clearFlag = {clear_flag};
            if (clearFlag) {{
                localStorage.removeItem(STORAGE_KEY);
            }}

            let baselineData = {json.dumps(baseline_celldata)};
            const branchMap = {json.dumps(branch_row_map)};
            const headerMap = {json.dumps(header_map)};
            const newUpdates = {new_updates_json};

            // 1. Load saved data from permanent browser storage
            let currentCells = [];
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {{
                try {{
                    currentCells = JSON.parse(saved);
                }} catch(e) {{
                    currentCells = baselineData;
                }}
            }} else {{
                currentCells = baselineData;
            }}

            // Helper to update or insert cell
            function setCellValue(r, c, val) {{
                let found = false;
                for (let i = 0; i < currentCells.length; i++) {{
                    if (currentCells[i].r === r && currentCells[i].c === c) {{
                        if (String(val).startsWith('=')) {{
                            currentCells[i].v = {{ f: String(val) }};
                        }} else {{
                            let num = parseFloat(String(val).replace(/,/g, ''));
                            if (!isNaN(num)) {{
                                currentCells[i].v = {{ v: num, ct: {{ fa: "General", t: "n" }} }};
                            }} else {{
                                currentCells[i].v = {{ v: String(val), ct: {{ fa: "General", t: "g" }} }};
                            }}
                        }}
                        found = true;
                        break;
                    }}
                }}
                if (!found) {{
                    let cellObj = {{ r: r, c: c, v: {{}} }};
                    if (String(val).startsWith('=')) {{
                        cellObj.v.f = String(val);
                    }} else {{
                        let num = parseFloat(String(val).replace(/,/g, ''));
                        if (!isNaN(num)) {{
                            cellObj.v = {{ v: num, ct: {{ fa: "General", t: "n" }} }};
                        }} else {{
                            cellObj.v = {{ v: String(val), ct: {{ fa: "General", t: "g" }} }};
                        }}
                    }}
                    currentCells.push(cellObj);
                }}
            }}

            // 2. Merge newly ingested OCR / Excel data
            if (newUpdates && Object.keys(newUpdates).length > 0) {{
                for (let branch in newUpdates) {{
                    if (branchMap[branch] !== undefined) {{
                        let r = branchMap[branch];
                        let fields = newUpdates[branch];
                        for (let colName in fields) {{
                            if (headerMap[colName] !== undefined) {{
                                let c = headerMap[colName];
                                setCellValue(r, c, fields[colName]);
                            }}
                        }}
                    }}
                }}
                localStorage.setItem(STORAGE_KEY, JSON.stringify(currentCells));
            }}

            // 3. Initialize Luckysheet with Auto-Saving Hook
            luckysheet.create({{
                container: 'luckysheet',
                showinfobar: false,
                showsheetbar: false,
                showstatisticBar: true,
                enableAddRow: false,
                enableAddBackTop: false,
                hook: {{
                    cellUpdated: function(r, c, oldVal, newVal, isRefresh) {{
                        setTimeout(() => {{
                            try {{
                                const allCells = luckysheet.getluckysheetfile()[0].celldata;
                                localStorage.setItem(STORAGE_KEY, JSON.stringify(allCells));
                            }} catch(err) {{}}
                        }}, 200);
                    }}
                }},
                data: [{{
                    "name": "MASTER REPORT",
                    "status": 1,
                    "order": 0,
                    "data": [],
                    "config": {{
                        "columnlen": {{
                            "0": 55, "1": 75, "2": 150, "3": 130, "4": 90, "5": 110,
                            "6": 100, "7": 130, "8": 110, "9": 90, "10": 120, "11": 90,
                            "12": 110, "13": 140, "14": 130, "15": 120
                        }}
                    }},
                    "celldata": currentCells,
                    "row": {len(all_branches) + 5},
                    "column": 18
                }}]
            }});
        }});
    </script>
</body>
</html>
"""

components.html(luckysheet_html, height=890)
