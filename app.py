import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np
import easyocr
import re
import io

st.set_page_config(page_title="Happi Cashbook Master", layout="wide")

st.markdown("""
    <style>
    .header-style { font-size: 24px; font-weight: bold; color: #0E4C92; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-style">🏢 HAPPI MOBILES - HEAD OFFICE MASTER CASHBOOK AUTOMATION</div>', unsafe_allow_html=True)

BRANCH_MASTER = [
    {"CODE": "ADBD", "BRANCH": "ADILABAD"}, {"CODE": "AMP", "BRANCH": "AMALAPURAM"},
    {"CODE": "AMPT", "BRANCH": "AMEERPET"}, {"CODE": "ANTP", "BRANCH": "ANANTAPUR"},
    {"CODE": "ARMU", "BRANCH": "ARMOOR"}, {"CODE": "ATMKR", "BRANCH": "ATMAKUR"},
    {"CODE": "BDHN", "BRANCH": "BODHAN"}, {"CODE": "BDPL", "BRANCH": "BODUPPAL"},
    {"CODE": "BG", "BRANCH": "BHUVANAGIRI"}, {"CODE": "BVRM", "BRANCH": "BHIMAVARAM"},
    {"CODE": "CHND", "BRANCH": "CHANDANAGAR"}, {"CODE": "CLX", "BRANCH": "CHIRALA"},
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
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

def extract_number(text_val):
    if not text_val:
        return None
    if re.search(r"\d{2}-\d{2}-\d{4}", str(text_val)):
        return None
    clean = str(text_val).replace(",", "").strip()
    match = re.search(r"(\d+\.?\d*)", clean)
    if match:
        try:
            return float(match.group(1))
        except:
            return None
    return None

def format_excel_formula(num_list):
    if not num_list:
        return ""
    if len(num_list) == 1:
        return num_list[0]
    return "=" + "+".join([str(x) for x in num_list])

col1, col2 = st.columns(2)

with col1:
    ho_dump_file = st.file_uploader("📂 1. Upload HO Apex Dr Balance Dump File (Excel / CSV)", type=["xlsx", "xls", "csv"])

with col2:
    uploaded_files = st.file_uploader("📥 2. Select Store Cashbook Screenshots", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# 1. Process HO Dr Balance Dump
ho_opening_balances = {}
if ho_dump_file:
    try:
        if ho_dump_file.name.endswith(".csv"):
            df_dump = pd.read_csv(ho_dump_file)
        else:
            df_dump = pd.read_excel(ho_dump_file)

        # Match Branch codes/names in the HO dump
        dump_text_cols = df_dump.astype(str)
        for b in BRANCH_MASTER:
            b_code = b["CODE"].lower()
            b_branch = b["BRANCH"].lower().replace(" ", "")
            
            for idx, row in df_dump.iterrows():
                row_str = " ".join(row.astype(str)).lower().replace(" ", "")
                if b_code in row_str or b_branch in row_str:
                    # Find first numeric amount in the row representing the Dr balance
                    for val in row:
                        amt = extract_number(val)
                        if amt is not None and amt > 0:
                            ho_opening_balances[b["BRANCH"]] = amt
                            break
                    break
        st.success(f"✅ HO Dump Processed: {len(ho_opening_balances)} stores Dr Balance mapped successfully!")
    except Exception as e:
        st.error(f"Error reading HO Dump file: {e}")

# 2. Process Store Screenshots (Denomination, Approvals, Finance, SR, Edits)
store_data_map = {}

if uploaded_files:
    with st.spinner("Processing screenshots and mapping data..."):
        for file in uploaded_files:
            image = Image.open(file)
            img_np = np.array(image)
            height, width = img_np.shape[:2]

            ocr_results = reader.readtext(img_np)
            full_text = " ".join([r[1] for r in ocr_results]).lower()

            matched_branch = None
            for b in BRANCH_MASTER:
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

            if not matched_branch:
                continue

            boxes = []
            for bbox, text, conf in ocr_results:
                cx = (bbox[0][0] + bbox[1][0]) / 2
                cy = (bbox[0][1] + bbox[2][1]) / 2
                boxes.append({"x": cx, "y": cy, "text": text.strip()})

            boxes.sort(key=lambda b: b["y"])
            rows = []
            for b in boxes:
                placed = False
                for r in rows:
                    if abs(r["y"] - b["y"]) <= 18:
                        r["items"].append(b)
                        r["y"] = sum(i["y"] for i in r["items"]) / len(r["items"])
                        placed = True
                        break
                if not placed:
                    rows.append({"y": b["y"], "items": [b]})

            for r in rows:
                r["items"].sort(key=lambda item: item["x"])

            denom_val = ""
            pending_apprvls = []
            finance_amnt = []
            sr_list = []
            edits_list = []
            ksp_approvals = []

            for r in rows:
                left_items = [i for i in r["items"] if i["x"] <= width * 0.68]
                right_items = [i for i in r["items"] if i["x"] > width * 0.68]

                # Denomination Total
                if any("total" in i["text"].lower() for i in right_items):
                    for i in reversed(right_items):
                        val = extract_number(i["text"])
                        if val is not None and val > 0:
                            denom_val = val
                            break

                # Line Items in Left Table
                left_text = " ".join([i["text"] for i in left_items]).lower()
                
                if not any(x in left_text for x in ["closing", "deposit", "diffrence", "difference", "total approval", "excess", "short", "approvals & sale", "add ins", "addins", "cash book"]):
                    amt = None
                    for i in left_items:
                        if i["x"] > width * 0.50:
                            val = extract_number(i["text"])
                            if val is not None and val > 0:
                                amt = val
                                break

                    if amt and amt > 0:
                        if any(k in left_text for k in ["pavan", "santhosh", "sharan"]):
                            ksp_approvals.append(amt)
                        elif any(k in left_text for k in ["admin", "mallesh", "shiva", "khan", "naresh", "coo", "asm", "javeed", "trade license"]):
                            pending_apprvls.append(amt)
                        elif any(k in left_text for k in ["bajaj", "idfc", "cash back", "cashback", "cash to card", "upi", "dbd"]):
                            finance_amnt.append(amt)
                        elif any(k in left_text for k in ["srn", "sr", "sale return", "sales return", "doa"]):
                            sr_list.append(amt)
                        elif "extra items" in left_text:
                            edits_list.append(amt)

            store_data_map[matched_branch] = {
                "DENOMINATION": denom_val,
                "PENDING APPRVLS": format_excel_formula(pending_apprvls),
                "FINANCE AMNT": format_excel_formula(finance_amnt),
                "SR": format_excel_formula(sr_list),
                "EDITS": format_excel_formula(edits_list),
                "(KSP)'Sir's Approvals": format_excel_formula(ksp_approvals)
            }

# Construct Final Master Table
final_rows = []
for idx, b in enumerate(BRANCH_MASTER, start=1):
    b_name = b["BRANCH"]
    d = store_data_map.get(b_name, {})
    
    # Priority for Opening Balance: HO Dump File > Manual Edit
    opening_bal = ho_opening_balances.get(b_name, "")
    
    final_rows.append({
        "Sl.No.": idx,
        "CODE": b["CODE"],
        "BRANCH": b["BRANCH"],
        "OPENING BALANCE": str(opening_bal),
        "DEPOSIT": "",
        "DENOMINATION": str(d.get("DENOMINATION", "")),
        "AddinGS": "",
        "PENDING APPRVLS": str(d.get("PENDING APPRVLS", "")),
        "FINANCE AMNT": str(d.get("FINANCE AMNT", "")),
        "SR": str(d.get("SR", "")),
        "SWEEPER SALARY": "",
        "EDITS": str(d.get("EDITS", "")),
        "APX SHORTAGE": "",
        "(KSP)'Sir's Approvals": str(d.get("(KSP)'Sir's Approvals", "")),
        "CLOSING BALANCE": "",
        "REMARKS": ""
    })

df_master = pd.DataFrame(final_rows)

st.subheader("📋 Head Office Master Cashbook (Editable)")
st.info("💡 **Note:"Below Given All Cells Are Editable")

edited_df = st.data_editor(
    df_master,
    use_container_width=True,
    height=550,
    disabled=["Sl.No.", "CODE", "BRANCH"],
    num_rows="fixed"
)

output = io.BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    edited_df.to_excel(writer, index=False, sheet_name='MASTER REPORT')
excel_data = output.getvalue()

st.download_button(
    label="📥 Download Master Excel Sheet (With Your Edits)",
    data=excel_data,
    file_name="HO_MASTER_CASHBOOK_REPORT.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
