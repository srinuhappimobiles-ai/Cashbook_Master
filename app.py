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

# --- SIDEBAR ---
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
    st.markdown("#### ⌨️ Active Excel 2010 Shortcuts")
    st.info("""
    * **Ctrl + D**: Fill Down (Drags formulas/values down)
    * **Ctrl + R**: Fill Right (Drags rightwards)
    * **Alt + H + B + A**: Apply All Borders
    * **Alt + H + B + N**: Remove Borders
    * **Alt + =**: AutoSum Formula
    * **Ctrl + B / I / U**: Bold, Italic, Underline
    """)

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
                    if standard_col not in ["SL.No.", "CODE", "BRANCH", "CLOSING BALANCE"]:
                        val_str = str(cell_val).strip()
                        if val_str and val_str != "nan":
                            target_entry[standard_col] = val_str
                imported_count += 1

        st.sidebar.success(f"✅ Loaded {imported_count} Stores from {master_import_file.name}!")
    except Exception as e:
        st.sidebar.error(f"Import Error: {e}")

# 2. Process Apex Dr Dump
if ho_dump_file:
    try:
        df_dump = pd.read_csv(ho_dump_file) if ho_dump_file.name.endswith(".csv") else pd.read_excel(ho_dump_file)
        b_col, a_col = df_dump.columns[0], df_dump.columns[1] if len(df_dump.columns) > 1 else df_dump.columns[0]
        for col in df_dump.columns:
            if "branch" in str(col).lower() or "store" in str(col).lower():
                b_col = col
            if "balance" in str(col).lower() or "opening" in str(col).lower() or "amount" in str(col).lower():
                a_col = col

        dump_dict = {}
        for _, row in df_dump.iterrows():
            b_val, raw_amt = normalize_key(row[b_col]), str(row[a_col]).replace(",", "").strip()
            match = re.search(r"(\d+\.?\d*)", raw_amt)
            if match and b_val:
                dump_dict[b_val] = int(round(float(match.group(1))))

        for b in all_branches:
            val = dump_dict.get(normalize_key(b.get("BRANCH", "")), dump_dict.get(normalize_key(b.get("CODE", ""))))
            if val is not None:
                db.setdefault("entries", {}).setdefault(b.get("BRANCH", ""), {})["OPENING BALANCE"] = str(val)
        st.sidebar.success("✅ Apex Dr Balances Synced Globally!")
    except Exception as e:
        st.sidebar.error(f"Apex Error: {e}")

# 3. Process Addins Dump
if addins_dump_file:
    try:
        df_addins = pd.read_csv(addins_dump_file) if addins_dump_file.name.endswith(".csv") else pd.read_excel(addins_dump_file)
        b_col, a_col = df_addins.columns[0], df_addins.columns[1] if len(df_addins.columns) > 1 else df_addins.columns[0]
        for col in df_addins.columns:
            if "branch" in str(col).lower() or "store" in str(col).lower():
                b_col = col
            if "amount" in str(col).lower() or "total" in str(col).lower() or "addin" in str(col).lower():
                a_col = col

        addins_dict = {}
        for _, row in df_addins.iterrows():
            b_val, raw_amt = normalize_key(row[b_col]), str(row[a_col]).replace(",", "").strip()
            match = re.search(r"(\d+\.?\d*)", raw_amt)
            if match and b_val:
                clean_amt = int(round(float(match.group(1))))
                if clean_amt > 0:
                    addins_dict.setdefault(b_val, []).append(clean_amt)

        for b in all_branches:
            vouchers = addins_dict.get(normalize_key(b.get("BRANCH", "")), addins_dict.get(normalize_key(b.get("CODE", "")), []))
            if vouchers:
                clean_ints = [str(int(x)) for x in vouchers if x > 0]
                formula_val = clean_ints[0] if len(clean_ints) == 1 else "=" + "+".join(clean_ints)
                db.setdefault("entries", {}).setdefault(b.get("BRANCH", ""), {})["AddinGS"] = formula_val
        st.sidebar.success("✅ Addins Synced Globally!")
    except Exception as e:
        st.sidebar.error(f"Addins Error: {e}")

# Prepare Celldata for Excel 2010
celldata = []

# Header Row: Excel 2010 Classic Dark Green Styling
for c_idx, h_text in enumerate(HEADERS):
    celldata.append({
        "r": 0, "c": c_idx,
        "v": { "v": h_text, "m": h_text, "bg": "#107c41", "fc": "#ffffff", "bl": 1, "ht": 0, "vt": 0 }
    })

entries_dict = db.get("entries", {})
for r_idx, b in enumerate(selected_branches, start=1):
    b_name = b.get("BRANCH", "")
    e = entries_dict.get(b_name, {})
    excel_row_num = r_idx + 1
    default_closing_formula = f"=D{excel_row_num}-SUM(E{excel_row_num}:N{excel_row_num})"

    row_vals = [
        str(r_idx),
        b.get("CODE", ""),
        b.get("BRANCH", ""),
        str(e.get("OPENING BALANCE", "")),
        str(e.get("DEPOSIT", "")),
        str(e.get("DENOMINATION", "")),
        str(e.get("AddinGS", "")),
        str(e.get("PENDING APPRVLS", "")),
        str(e.get("FINANCE AMNT", "")),
        str(e.get("SR", "")),
        str(e.get("SWEEPER SALARY", "")),
        str(e.get("EDITS", "")),
        str(e.get("APX SHORTAGE", "")),
        str(e.get("(KSP)'Sir's Approvals", "")),
        str(e.get("CLOSING BALANCE", default_closing_formula)),
        str(e.get("REMARKS", ""))
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
                except Exception:
                    cell_obj["v"]["v"] = str(val)
                    cell_obj["v"]["ct"] = {"fa": "General", "t": "g"}
            celldata.append(cell_obj)

# Main Workspace Header & Export
col_head1, col_head2 = st.columns([3.5, 1])

with col_head1:
    st.markdown(
        f'<div class="main-title">📊 HAPPI MOBILES - MASTER CASHBOOK (MICROSOFT EXCEL 2010 WORKSPACE) '
        f'<span style="font-size: 13px; color: #107c41; font-weight: bold;">● Active ({len(selected_branches)} Stores)</span></div>',
        unsafe_allow_html=True
    )

with col_head2:
    export_rows = []
    for idx, b in enumerate(all_branches, start=1):
        e = entries_dict.get(b.get("BRANCH", ""), {})
        excel_row_num = idx + 1
        export_rows.append({
            "SL.No.": idx, "CODE": b.get("CODE", ""), "BRANCH": b.get("BRANCH", ""),
            "OPENING BALANCE": e.get("OPENING BALANCE", ""), "DEPOSIT": e.get("DEPOSIT", ""),
            "DENOMINATION": e.get("DENOMINATION", ""), "AddinGS": e.get("AddinGS", ""),
            "PENDING APPRVLS": e.get("PENDING APPRVLS", ""), "FINANCE AMNT": e.get("FINANCE AMNT", ""),
            "SR": e.get("SR", ""), "SWEEPER SALARY": e.get("SWEEPER SALARY", ""),
            "EDITS": e.get("EDITS", ""), "APX SHORTAGE": e.get("APX SHORTAGE", ""),
            "(KSP)'Sir's Approvals": e.get("(KSP)'Sir's Approvals", ""),
            "CLOSING BALANCE": e.get("CLOSING BALANCE", f"=D{excel_row_num}-SUM(E{excel_row_num}:N{excel_row_num})"),
            "REMARKS": e.get("REMARKS", "")
        })
    df_export = pd.DataFrame(export_rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='MASTER REPORT')
    st.download_button(
        label="📥 Download Master Excel",
        data=output.getvalue(),
        file_name="HO_MASTER_CASHBOOK_2010.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# Full Excel 2010 Native Spreadsheet Engine with Direct Capturing Event Hooks
excel_2010_html = f"""
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
        html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; font-family: 'Segoe UI', Calibri, Arial, sans-serif; }}
        #luckysheet {{ margin: 0px; padding: 0px; position: absolute; width: 100%; height: 100%; left: 0px; top: 0px; }}
        .luckysheet-toolbar {{ background: #f3f3f3 !important; border-bottom: 1px solid #d4d4d4 !important; }}
    </style>
</head>
<body>
    <div id="luckysheet"></div>
    <script>
        $(function () {{
            luckysheet.create({{
                container: 'luckysheet',
                showinfobar: false,
                showsheetbar: false,
                showstatisticBar: true,
                enableAddRow: false,
                enableAddBackTop: false,
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
                    "celldata": {json.dumps(celldata)},
                    "row": {len(selected_branches) + 5},
                    "column": 18
                }}]
            }});

            function shiftFormulaRows(formulaStr, rowDelta) {{
                return formulaStr.replace(/([A-Za-z]+)(\\d+)/g, function(match, col, row) {{
                    let newRow = parseInt(row, 10) + rowDelta;
                    return col + newRow;
                }});
            }}

            function shiftFormulaCols(formulaStr, colDelta) {{
                return formulaStr.replace(/([A-Z]+)(\\d+)/g, function(match, col, row) {{
                    let colNum = 0;
                    for (let i = 0; i < col.length; i++) {{
                        colNum = colNum * 26 + (col.charCodeAt(i) - 64);
                    }}
                    colNum += colDelta;
                    let newCol = '';
                    while (colNum > 0) {{
                        let rem = (colNum - 1) % 26;
                        newCol = String.fromCharCode(65 + rem) + newCol;
                        colNum = Math.floor((colNum - 1) / 26);
                    }}
                    return newCol + row;
                }});
            }}

            // Intercept and Execute Keyboard Shortcuts directly in capture phase
            let keySequence = [];
            let keyTimer = null;

            window.addEventListener('keydown', function(e) {{
                let range = luckysheet.getRange();
                if (!range || range.length === 0) return;

                let r_start = range[0].row[0];
                let r_end = range[0].row[1];
                let c_start = range[0].column[0];
                let c_end = range[0].column[1];

                // 1. CTRL + D: Fill Down
                if ((e.ctrlKey || e.metaKey) && (e.key === 'd' || e.key === 'D' || e.keyCode === 68)) {{
                    e.preventDefault();
                    e.stopPropagation();

                    if (r_start === r_end && r_start > 0) {{
                        for (let c = c_start; c <= c_end; c++) {{
                            let topCell = luckysheet.getCellValue(r_start - 1, c, {{ type: 'all' }});
                            if (topCell) {{
                                if (topCell.f) {{
                                    luckysheet.setCellValue(r_start, c, {{ f: shiftFormulaRows(topCell.f, 1) }});
                                }} else {{
                                    luckysheet.setCellValue(r_start, c, topCell.v !== undefined ? topCell.v : topCell);
                                }}
                            }}
                        }}
                    }} else if (r_end > r_start) {{
                        for (let c = c_start; c <= c_end; c++) {{
                            let topCell = luckysheet.getCellValue(r_start, c, {{ type: 'all' }});
                            if (topCell) {{
                                for (let r = r_start + 1; r <= r_end; r++) {{
                                    let delta = r - r_start;
                                    if (topCell.f) {{
                                        luckysheet.setCellValue(r, c, {{ f: shiftFormulaRows(topCell.f, delta) }});
                                    }} else {{
                                        luckysheet.setCellValue(r, c, topCell.v !== undefined ? topCell.v : topCell);
                                    }}
                                }}
                            }}
                        }}
                    }}
                    luckysheet.refresh();
                    return false;
                }}

                // 2. CTRL + R: Fill Right
                if ((e.ctrlKey || e.metaKey) && (e.key === 'r' || e.key === 'R' || e.keyCode === 82)) {{
                    e.preventDefault();
                    e.stopPropagation();

                    for (let r = r_start; r <= r_end; r++) {{
                        let leftCell = luckysheet.getCellValue(r, c_start, {{ type: 'all' }});
                        if (leftCell) {{
                            for (let c = c_start + 1; c <= c_end; c++) {{
                                let delta = c - c_start;
                                if (leftCell.f) {{
                                    luckysheet.setCellValue(r, c, {{ f: shiftFormulaCols(leftCell.f, delta) }});
                                }} else {{
                                    luckysheet.setCellValue(r, c, leftCell.v !== undefined ? leftCell.v : leftCell);
                                }}
                            }}
                        }}
                    }}
                    luckysheet.refresh();
                    return false;
                }}

                // 3. ALT + = : AutoSum
                if (e.altKey && (e.key === '=' || e.key === '+' || e.keyCode === 187)) {{
                    e.preventDefault();
                    e.stopPropagation();

                    for (let c = c_start; c <= c_end; c++) {{
                        let colLetter = String.fromCharCode(65 + c);
                        let autoSum = '=SUM(' + colLetter + '2:' + colLetter + r_end + ')';
                        luckysheet.setCellValue(r_end + 1, c, {{ f: autoSum }});
                    }}
                    luckysheet.refresh();
                    return false;
                }}

                // 4. ALT Sequences: Alt+H+B+A (All Borders) & Alt+H+B+N (Clear Borders)
                if (e.altKey) {{
                    keySequence = ['ALT'];
                    clearTimeout(keyTimer);
                    keyTimer = setTimeout(() => {{ keySequence = []; }}, 2500);
                }} else if (keySequence.length > 0) {{
                    keySequence.push(e.key.toUpperCase());
                    let seq = keySequence.join('');

                    if (seq.includes('ALTHBA')) {{
                        e.preventDefault();
                        e.stopPropagation();
                        luckysheet.setCellFormat(r_start, c_start, 'bd', {{
                            borderType: 'border-all',
                            style: '1',
                            color: '#000000'
                        }}, {{
                            range: [{{ row: [r_start, r_end], column: [c_start, c_end] }}]
                        }});
                        keySequence = [];
                        return false;
                    }}

                    if (seq.includes('ALTHBN')) {{
                        e.preventDefault();
                        e.stopPropagation();
                        luckysheet.setCellFormat(r_start, c_start, 'bd', {{
                            borderType: 'border-none'
                        }}, {{
                            range: [{{ row: [r_start, r_end], column: [c_start, c_end] }}]
                        }});
                        keySequence = [];
                        return false;
                    }}
                }}
            }}, true);
        }});
    </script>
</body>
</html>
"""

components.html(excel_2010_html, height=860)
