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

# Page configuration
st.set_page_config(page_title="Happi Cashbook Master", layout="wide")

st.markdown(
    """
    <style>
    .header-style { font-size: 24px; font-weight: bold; color: #0E4C92; margin-bottom: 15px; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="header-style">🏢 HAPPI MOBILES - HEAD OFFICE MASTER CASHBOOK'
    " AUTOMATION</div>",
    unsafe_allow_html=True,
)

DB_FILE = "cashbook_master_db.json"

DEFAULT_BRANCHES = [
    {"CODE": "ADBD", "BRANCH": "ADILABAD"},
    {"CODE": "AMP", "BRANCH": "AMALAPURAM"},
    {"CODE": "AMPT", "BRANCH": "AMEERPET"},
    {"CODE": "ANTP", "BRANCH": "ANANTAPUR"},
    {"CODE": "ARMU", "BRANCH": "ARMOOR"},
    {"CODE": "ATMKR", "BRANCH": "ATMAKUR"},
    {"CODE": "BDHN", "BRANCH": "BODHAN"},
    {"CODE": "BDPL", "BRANCH": "BODUPPAL"},
    {"CODE": "BG", "BRANCH": "BHUVANAGIRI"},
    {"CODE": "BVRM", "BRANCH": "BHIMAVARAM"},
    {"CODE": "CHND", "BRANCH": "CHANDANAGAR"},
    {"CODE": "CHNT", "BRANCH": "CHINTAL"},
    {"CODE": "DBGS", "BRANCH": "DABAGARDENS"},
    {"CODE": "DBGS-2", "BRANCH": "DABAGARDENS-2"},
    {"CODE": "DVKD", "BRANCH": "DEVARAKONDA"},
    {"CODE": "DVRM", "BRANCH": "DHARMAVRAM"},
    {"CODE": "ECIL", "BRANCH": "ECIL"},
    {"CODE": "ELR", "BRANCH": "ELURU"},
    {"CODE": "GDVK", "BRANCH": "GODHAVARIKHANI"},
    {"CODE": "GJWK", "BRANCH": "GAJUWAKA"},
    {"CODE": "GJWL", "BRANCH": "GAJWEL"},
    {"CODE": "GNT", "BRANCH": "GUNTUR"},
    {"CODE": "GNT2", "BRANCH": "GUNTUR2"},
    {"CODE": "GTKL", "BRANCH": "GUNTAKAL"},
    {"CODE": "GWD", "BRANCH": "GADWAL"},
    {"CODE": "HAL", "BRANCH": "HALIYA"},
    {"CODE": "HNMK", "BRANCH": "HANUMAKONDA"},
    {"CODE": "HUP", "BRANCH": "HINDUPUR"},
    {"CODE": "JCL", "BRANCH": "JADCHERLA"},
    {"CODE": "JNGN", "BRANCH": "JANGAON"},
    {"CODE": "JTL", "BRANCH": "JAGTIAL"},
    {"CODE": "KDGM", "BRANCH": "KALYANADURGAM"},
    {"CODE": "KDR", "BRANCH": "KADIRI"},
    {"CODE": "KDR2", "BRANCH": "KADIRI-2"},
    {"CODE": "KKP", "BRANCH": "KUKATPALLY"},
    {"CODE": "KMGH", "BRANCH": "KHARMANGHAT"},
    {"CODE": "KMM", "BRANCH": "KHAMMAM"},
    {"CODE": "KMM2", "BRANCH": "KHAMMAM 2"},
    {"CODE": "KPM", "BRANCH": "KUPPAM"},
    {"CODE": "KRKH", "BRANCH": "KHARKHANA"},
    {"CODE": "KRLA", "BRANCH": "KORUTLA"},
    {"CODE": "KRMN", "BRANCH": "KARIMNAGAR"},
    {"CODE": "KRNL", "BRANCH": "KURNOOL"},
    {"CODE": "KRNL2", "BRANCH": "KURNOOL2"},
    {"CODE": "KZP", "BRANCH": "KAZIPET"},
    {"CODE": "MCI", "BRANCH": "MANCHERIAL"},
    {"CODE": "MDPL", "BRANCH": "MADANAPALLI"},
    {"CODE": "MDPR", "BRANCH": "MADHAPUR"},
    {"CODE": "MDPT", "BRANCH": "MANDAPETA"},
    {"CODE": "MHBR", "BRANCH": "MAHABUBNAGAR"},
    {"CODE": "MLKJ", "BRANCH": "MALKAJGIRI"},
    {"CODE": "MRGA", "BRANCH": "MIRYALAGUDA"},
    {"CODE": "MTM", "BRANCH": "MACHILIPATNAM"},
    {"CODE": "MVP", "BRANCH": "MVP COLONY"},
    {"CODE": "NDD", "BRANCH": "NIDADAVOLE"},
    {"CODE": "NDL", "BRANCH": "NANDYALA"},
    {"CODE": "NGKL", "BRANCH": "NAGARKURNOOL"},
    {"CODE": "NKRL", "BRANCH": "NAKREKAL"},
    {"CODE": "NLG", "BRANCH": "NALGONDA"},
    {"CODE": "NRKD", "BRANCH": "NARAYANKHED"},
    {"CODE": "NRML", "BRANCH": "NIRMAL"},
    {"CODE": "NRSP", "BRANCH": "NARASANNAPETA"},
    {"CODE": "NSMP", "BRANCH": "NARSAMPET"},
    {"CODE": "NSPT", "BRANCH": "NARSIPATNAM"},
    {"CODE": "NZVD", "BRANCH": "NUZVID"},
    {"CODE": "ONG", "BRANCH": "ONGOLE"},
    {"CODE": "PDPL", "BRANCH": "PEDDAPALLI"},
    {"CODE": "PDPM", "BRANCH": "PEDDAPURAM"},
    {"CODE": "PIL", "BRANCH": "PILERU"},
    {"CODE": "PLM", "BRANCH": "PALAMANER"},
    {"CODE": "PSA", "BRANCH": "PALASA"},
    {"CODE": "PVA", "BRANCH": "PALAVANCHA"},
    {"CODE": "RCT", "BRANCH": "RAYACHOTI"},
    {"CODE": "RJY", "BRANCH": "RAJAMUNDRY"},
    {"CODE": "RMTP", "BRANCH": "RAMANTHAPUR"},
    {"CODE": "RTCX", "BRANCH": "RTC X ROAD"},
    {"CODE": "SDPT", "BRANCH": "SIDDIPET"},
    {"CODE": "SDR", "BRANCH": "S.D.ROAD"},
    {"CODE": "SHDR", "BRANCH": "SHADNAGAR"},
    {"CODE": "SHPR", "BRANCH": "SHAPUR"},
    {"CODE": "SKKM", "BRANCH": "SRIKAKULAM"},
    {"CODE": "SMBD", "BRANCH": "SHAMSHABAD"},
    {"CODE": "SNGR", "BRANCH": "SANGAREDDY"},
    {"CODE": "SPT", "BRANCH": "SOMPETA"},
    {"CODE": "SRN", "BRANCH": "S.R.NAGAR"},
    {"CODE": "SRNR", "BRANCH": "SAROORNAGAR"},
    {"CODE": "SRPT", "BRANCH": "SURYAPET"},
    {"CODE": "STNR", "BRANCH": "SANTOSHNAGAR"},
    {"CODE": "TDPG", "BRANCH": "TADEPALLIGUDEM"},
    {"CODE": "TDPT", "BRANCH": "TADIPATRI"},
    {"CODE": "TDU", "BRANCH": "TANDUR"},
    {"CODE": "TEK", "BRANCH": "TEKKALI"},
    {"CODE": "TN", "BRANCH": "TUNI"},
    {"CODE": "TNK", "BRANCH": "TANUKU"},
    {"CODE": "TNL", "BRANCH": "TENALI"},
    {"CODE": "TPT", "BRANCH": "TIRUPATHI"},
    {"CODE": "TPT2", "BRANCH": "TIRUPATHI 2"},
    {"CODE": "UPL", "BRANCH": "UPPAL"},
    {"CODE": "VIJ-1", "BRANCH": "VIJAYAWADA 1"},
    {"CODE": "VIJ-3", "BRANCH": "VIJAYAWADA 3"},
    {"CODE": "VIJ-4", "BRANCH": "VIJAYAWADA 4"},
    {"CODE": "VNSP", "BRANCH": "VANASTALIPURAM"},
    {"CODE": "VZM", "BRANCH": "VIZIANAGARAM"},
    {"CODE": "VZM2", "BRANCH": "VIZIANAGARAM 2"},
    {"CODE": "WGL", "BRANCH": "WARANGAL"},
    {"CODE": "WGL2", "BRANCH": "WARANGAL 2"},
    {"CODE": "ZB", "BRANCH": "ZAHEERABAD"},
]

if "uploader_key" not in st.session_state:
  st.session_state.uploader_key = 0


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
      "store_data": {},
      "manual_edits": {},
      "metadata": {},  # Stores SR/Finance Bill details for hover preview
  }


def save_db(data):
  with open(DB_FILE, "w") as f:
    json.dump(data, f, indent=2)


db = load_db()
if "metadata" not in db:
  db["metadata"] = {}

# --- WORK ASSIGNMENT / CASHIER SPLIT SIDEBAR ---
st.sidebar.title("👥 Work Assignment")
work_mode = st.sidebar.radio(
    "Select Work Mode:",
    ["👤 Single Cashier (All Stores)", "👥 Two Cashiers (Split 50-50)"],
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

  cashier_view = st.sidebar.selectbox(
      "Choose Your Cashier Assignment:", [c1_label, c2_label]
  )

  if cashier_view == c1_label:
    selected_branches = c1_branches
    st.sidebar.success(f"Loaded Cashier 1: **{len(selected_branches)}** Stores")
  else:
    selected_branches = c2_branches
    st.sidebar.success(f"Loaded Cashier 2: **{len(selected_branches)}** Stores")
else:
  st.sidebar.info(f"Loaded All: **{len(selected_branches)}** Stores")


# --- HELPER FUNCTIONS ---
def extract_number(text_val, round_val=False):
  if text_val is None:
    return None
  if re.search(r"\d{2}-\d{2}-\d{4}", str(text_val)):
    return None
  clean = str(text_val).replace(",", "").strip()
  match = re.search(r"(\d+\.?\d*)", clean)
  if match:
    try:
      num = float(match.group(1))
      return int(round(num)) if round_val else num
    except:
      return None
  return None


def format_excel_formula(num_list):
  if not num_list:
    return ""
  if len(num_list) == 1:
    return num_list[0]
  return "=" + "+".join([str(x) for x in num_list])


def normalize_name(s):
  if not s:
    return ""
  return re.sub(r"[^A-Za-z0-9]", "", str(s)).upper()


def parse_outlook_text(text):
  """Extracts structured values from direct pasted Outlook text/tables."""
  extracted = {
      "denom": "",
      "pending_apprvls": [],
      "finance_amnt": [],
      "sr_list": [],
      "edits_list": [],
      "ksp_approvals": [],
      "sr_meta": [],
      "finance_meta": [],
  }

  lines = text.strip().split("\n")
  for line in lines:
    clean_line = line.strip().lower()
    if not clean_line:
      continue

    # Extract all numbers from the line
    nums = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", line)
    clean_nums = []
    for n in nums:
      val = extract_number(n)
      if val is not None and val > 0:
        clean_nums.append(int(round(val)) if val.is_integer() else val)

    if not clean_nums:
      continue

    target_val = clean_nums[-1]

    # Denomination / Closing Match
    if any(k in clean_line for k in ["closing", "total", "denomination"]):
      extracted["denom"] = target_val
    elif any(k in clean_line for k in ["pavan", "santhosh", "sharan"]):
      extracted["ksp_approvals"].append(target_val)
    elif any(
        k in clean_line
        for k in [
            "admin",
            "mallesh",
            "shiva",
            "khan",
            "naresh",
            "coo",
            "asm",
            "javeed",
            "trade license",
        ]
    ):
      extracted["pending_apprvls"].append(target_val)
    elif any(
        k in clean_line
        for k in [
            "bajaj",
            "idfc",
            "cash back",
            "cashback",
            "cash to card",
            "upi",
            "dbd",
            "finance",
        ]
    ):
      extracted["finance_amnt"].append(target_val)
      remark = "Finance"
      if "cashback" in clean_line or "cash back" in clean_line:
        remark = "Cash Back"
      elif "cash to card" in clean_line:
        remark = "Cash to Card Modification"
      elif "dbd" in clean_line:
        remark = "DBD Modification"

      bill_match = re.search(r"\b(?:inv|bill|txn)[-_/\w\d]+\b", line, re.I)
      bill_no = bill_match.group(0) if bill_match else "N/A"
      extracted["finance_meta"].append(
          {"bill_no": bill_no, "amount": target_val, "remarks": remark}
      )
    elif any(
        k in clean_line
        for k in ["srn", "sr", "sale return", "sales return", "doa"]
    ):
      extracted["sr_list"].append(target_val)
      bill_match = re.search(r"\b(?:srn|inv|bill)[-_/\w\d]+\b", line, re.I)
      bill_no = bill_match.group(0) if bill_match else "N/A"
      extracted["sr_meta"].append({
          "bill_no": bill_no,
          "amount": target_val,
          "reason": "Sales Return",
      })
    elif "extra" in clean_line or "edit" in clean_line:
      extracted["edits_list"].append(target_val)

  return extracted


# --- 3 DATA INGESTION COLUMNS ---
col1, col2, col3 = st.columns([1.2, 1.2, 1.6])

with col1:
  ho_dump_file = st.file_uploader(
      "📂 1. Upload Apex Dr Balance File",
      type=["xlsx", "xls", "csv"],
      key=f"ho_dump_{st.session_state.uploader_key}",
  )

with col2:
  uploaded_files = st.file_uploader(
      "📥 2. Store Screenshots (OCR)",
      type=["png", "jpg", "jpeg"],
      accept_multiple_files=True,
      key="store_screenshots_uploader",
  )

with col3:
  with st.expander("⚡ 3. Direct Outlook Table Paste (Instant)", expanded=True):
    target_store_name = st.selectbox(
        "Select Store:",
        [b["BRANCH"] for b in selected_branches],
        key="quick_paste_store",
    )
    pasted_box = st.text_area(
        "Paste Outlook Mail Table/Text:",
        placeholder="Copy from Outlook -> Paste here (Ctrl+V)...",
        height=70,
        key="quick_paste_box",
    )
    if st.button(
        "🚀 Map Data to Store", use_container_width=True, key="btn_map_paste"
    ):
      if pasted_box.strip():
        res = parse_outlook_text(pasted_box)

        # Update store data
        db["store_data"][target_store_name] = {
            "DENOMINATION": res["denom"],
            "PENDING APPRVLS": format_excel_formula(res["pending_apprvls"]),
            "FINANCE AMNT": format_excel_formula(res["finance_amnt"]),
            "SR": format_excel_formula(res["sr_list"]),
            "EDITS": format_excel_formula(res["edits_list"]),
            "(KSP)'Sir's Approvals": format_excel_formula(
                res["ksp_approvals"]
            ),
        }

        # Store metadata for hover preview
        db["metadata"][target_store_name] = {
            "sr": res["sr_meta"],
            "finance": res["finance_meta"],
        }

        save_db(db)
        st.success(f"✅ Data mapped instantly to **{target_store_name}**!")
        st.rerun()
      else:
        st.warning("Please paste some text/table first.")


@st.cache_resource
def load_ocr():
  return easyocr.Reader(["en"])


reader = load_ocr()

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
        elif (
            "balance" in c_low
            or "opening" in c_low
            or "dr" in c_low
            or "amount" in c_low
        ):
          bal_col = col

      if branch_col is None:
        branch_col = df_dump.columns[0]
      if bal_col is None:
        bal_col = (
            df_dump.columns[1]
            if len(df_dump.columns) > 1
            else df_dump.columns[0]
        )

      dump_dict = {}
      for idx, row in df_dump.iterrows():
        b_val = normalize_name(row[branch_col])
        raw_amt = row[bal_col]
        clean_amt = extract_number(raw_amt, round_val=True)
        if b_val and clean_amt is not None:
          dump_dict[b_val] = clean_amt

      for b in db["branches"]:
        b_norm = normalize_name(b["BRANCH"])
        b_code_norm = normalize_name(b["CODE"])

        if b_norm in dump_dict:
          db["ho_balances"][b["BRANCH"]] = dump_dict[b_norm]
          if b["BRANCH"] not in db["manual_edits"]:
            db["manual_edits"][b["BRANCH"]] = {}
          db["manual_edits"][b["BRANCH"]]["OPENING BALANCE"] = str(
              dump_dict[b_norm]
          )
        elif b_code_norm in dump_dict:
          db["ho_balances"][b["BRANCH"]] = dump_dict[b_code_norm]
          if b["BRANCH"] not in db["manual_edits"]:
            db["manual_edits"][b["BRANCH"]] = {}
          db["manual_edits"][b["BRANCH"]]["OPENING BALANCE"] = str(
              dump_dict[b_code_norm]
          )

      save_db(db)
      st.session_state.last_processed_file = current_file_id
      st.rerun()
    except Exception as e:
      st.error(f"Error reading HO Dump file: {e}")

# Process Store Screenshots
if uploaded_files:
  with st.spinner("Processing screenshots and mapping data..."):
    for file in uploaded_files:
      image = Image.open(file)
      img_np = np.array(image)
      height, width = img_np.shape[:2]

      ocr_results = reader.readtext(img_np)
      full_text = " ".join([r[1] for r in ocr_results]).lower()

      matched_branch = None
      for b in db["branches"]:
        b_name_clean = b["BRANCH"].lower().replace(" ", "").replace("-", "")
        b_code_clean = b["CODE"].lower().replace("-", "")
        file_clean = (
            file.name.lower()
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
        )
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
      pending_apprvls, finance_amnt, sr_list, edits_list, ksp_approvals = (
          [],
          [],
          [],
          [],
          [],
      )

      for r in rows:
        left_items = [i for i in r["items"] if i["x"] <= width * 0.68]
        right_items = [i for i in r["items"] if i["x"] > width * 0.68]

        if any("total" in i["text"].lower() for i in right_items):
          for i in reversed(right_items):
            val = extract_number(i["text"], round_val=False)
            if val is not None and val > 0:
              denom_val = int(round(val)) if val.is_integer() else val
              break

        left_text = " ".join([i["text"] for i in left_items]).lower()

        if not any(
            x in left_text
            for x in [
                "closing",
                "deposit",
                "diffrence",
                "difference",
                "total approval",
                "excess",
                "short",
                "approvals & sale",
                "add ins",
                "addins",
                "cash book",
            ]
        ):
          amt = None
          for i in left_items:
            if i["x"] > width * 0.50:
              val = extract_number(i["text"], round_val=False)
              if val is not None and val > 0:
                amt = int(round(val)) if val.is_integer() else val
                break

          if amt and amt > 0:
            if any(k in left_text for k in ["pavan", "santhosh", "sharan"]):
              ksp_approvals.append(amt)
            elif any(
                k in left_text
                for k in [
                    "admin",
                    "mallesh",
                    "shiva",
                    "khan",
                    "naresh",
                    "coo",
                    "asm",
                    "javeed",
                    "trade license",
                ]
            ):
              pending_apprvls.append(amt)
            elif any(
                k in left_text
                for k in [
                    "bajaj",
                    "idfc",
                    "cash back",
                    "cashback",
                    "cash to card",
                    "upi",
                    "dbd",
                ]
            ):
              finance_amnt.append(amt)
            elif any(
                k in left_text
                for k in ["srn", "sr", "sale return", "sales return", "doa"]
            ):
              sr_list.append(amt)
            elif "extra items" in left_text:
              edits_list.append(amt)

      db["store_data"][matched_branch] = {
          "DENOMINATION": denom_val,
          "PENDING APPRVLS": format_excel_formula(pending_apprvls),
          "FINANCE AMNT": format_excel_formula(finance_amnt),
          "SR": format_excel_formula(sr_list),
          "EDITS": format_excel_formula(edits_list),
          "(KSP)'Sir's Approvals": format_excel_formula(ksp_approvals),
      }

    save_db(db)

# Build Master DataFrame for the Selected View
final_rows = []
for idx, b in enumerate(selected_branches, start=1):
  b_name = b["BRANCH"]
  d = db["store_data"].get(b_name, {})
  opening_bal = db["ho_balances"].get(b_name, "")
  manual = db["manual_edits"].get(b_name, {})

  final_rows.append({
      "Sl.No.": idx,
      "CODE": b["CODE"],
      "BRANCH": b["BRANCH"],
      "OPENING BALANCE": manual.get("OPENING BALANCE", str(opening_bal)),
      "DEPOSIT": manual.get("DEPOSIT", ""),
      "DENOMINATION": manual.get(
          "DENOMINATION", str(d.get("DENOMINATION", ""))
      ),
      "AddinGS": manual.get("AddinGS", ""),
      "PENDING APPRVLS": manual.get(
          "PENDING APPRVLS", str(d.get("PENDING APPRVLS", ""))
      ),
      "FINANCE AMNT": manual.get(
          "FINANCE AMNT", str(d.get("FINANCE AMNT", ""))
      ),
      "SR": manual.get("SR", str(d.get("SR", ""))),
      "SWEEPER SALARY": manual.get("SWEEPER SALARY", ""),
      "EDITS": manual.get("EDITS", str(d.get("EDITS", ""))),
      "APX SHORTAGE": manual.get("APX SHORTAGE", ""),
      "(KSP)'Sir's Approvals": manual.get(
          "(KSP)'Sir's Approvals", str(d.get("(KSP)'Sir's Approvals", ""))
      ),
      "CLOSING BALANCE": manual.get("CLOSING BALANCE", ""),
      "REMARKS": manual.get("REMARKS", ""),
  })

df_master = pd.DataFrame(final_rows)

st.subheader(
    f"📋 Head Office Master Cashbook ({len(selected_branches)} Stores Shown)"
)

edited_df = st.data_editor(
    df_master,
    use_container_width=True,
    height=550,
    disabled=["Sl.No.", "CODE", "BRANCH"],
    num_rows="fixed",
    key=f"master_data_editor_{work_mode}_{len(selected_branches)}",
)

# Persist manual edits
for idx, row in edited_df.iterrows():
  b_name = row["BRANCH"]
  if b_name not in db["manual_edits"]:
    db["manual_edits"][b_name] = {}

  db["manual_edits"][b_name] = {
      "OPENING BALANCE": (
          str(row["OPENING BALANCE"])
          if pd.notna(row["OPENING BALANCE"])
          else ""
      ),
      "DEPOSIT": str(row["DEPOSIT"]) if pd.notna(row["DEPOSIT"]) else "",
      "DENOMINATION": (
          str(row["DENOMINATION"]) if pd.notna(row["DENOMINATION"]) else ""
      ),
      "AddinGS": str(row["AddinGS"]) if pd.notna(row["AddinGS"]) else "",
      "PENDING APPRVLS": (
          str(row["PENDING APPRVLS"])
          if pd.notna(row["PENDING APPRVLS"])
          else ""
      ),
      "FINANCE AMNT": (
          str(row["FINANCE AMNT"]) if pd.notna(row["FINANCE AMNT"]) else ""
      ),
      "SR": str(row["SR"]) if pd.notna(row["SR"]) else "",
      "SWEEPER SALARY": (
          str(row["SWEEPER SALARY"]) if pd.notna(row["SWEEPER SALARY"]) else ""
      ),
      "EDITS": str(row["EDITS"]) if pd.notna(row["EDITS"]) else "",
      "APX SHORTAGE": (
          str(row["APX SHORTAGE"]) if pd.notna(row["APX SHORTAGE"]) else ""
      ),
      "(KSP)'Sir's Approvals": (
          str(row["(KSP)'Sir's Approvals"])
          if pd.notna(row["(KSP)'Sir's Approvals"])
          else ""
      ),
      "CLOSING BALANCE": (
          str(row["CLOSING BALANCE"])
          if pd.notna(row["CLOSING BALANCE"])
          else ""
      ),
      "REMARKS": str(row["REMARKS"]) if pd.notna(row["REMARKS"]) else "",
  }
save_db(db)

# Export and Reset options
c_down, c_reset = st.columns([4, 1.5])

with c_down:
  all_rows_export = []
  for idx, b in enumerate(db["branches"], start=1):
    b_name = b["BRANCH"]
    d = db["store_data"].get(b_name, {})
    opening_bal = db["ho_balances"].get(b_name, "")
    manual = db["manual_edits"].get(b_name, {})

    all_rows_export.append({
        "Sl.No.": idx,
        "CODE": b["CODE"],
        "BRANCH": b["BRANCH"],
        "OPENING BALANCE": manual.get("OPENING BALANCE", str(opening_bal)),
        "DEPOSIT": manual.get("DEPOSIT", ""),
        "DENOMINATION": manual.get(
            "DENOMINATION", str(d.get("DENOMINATION", ""))
        ),
        "AddinGS": manual.get("AddinGS", ""),
        "PENDING APPRVLS": manual.get(
            "PENDING APPRVLS", str(d.get("PENDING APPRVLS", ""))
        ),
        "FINANCE AMNT": manual.get(
            "FINANCE AMNT", str(d.get("FINANCE AMNT", ""))
        ),
        "SR": manual.get("SR", str(d.get("SR", ""))),
        "SWEEPER SALARY": manual.get("SWEEPER SALARY", ""),
        "EDITS": manual.get("EDITS", str(d.get("EDITS", ""))),
        "APX SHORTAGE": manual.get("APX SHORTAGE", ""),
        "(KSP)'Sir's Approvals": manual.get(
            "(KSP)'Sir's Approvals", str(d.get("(KSP)'Sir's Approvals", ""))
        ),
        "CLOSING BALANCE": manual.get("CLOSING BALANCE", ""),
        "REMARKS": manual.get("REMARKS", ""),
    })

  df_full_export = pd.DataFrame(all_rows_export)

  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_full_export.to_excel(writer, index=False, sheet_name="MASTER REPORT")
  excel_data = output.getvalue()

  st.download_button(
      label="📥 Download Full Master Excel Sheet (All Stores)",
      data=excel_data,
      file_name="HO_MASTER_CASHBOOK_REPORT.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      use_container_width=True,
  )

with c_reset:
  if st.button("🗑️ Clear Dr Balances Only", use_container_width=True):
    db["ho_balances"] = {}
    for b_name in db["manual_edits"]:
      db["manual_edits"][b_name]["OPENING BALANCE"] = ""
    save_db(db)

    st.session_state.uploader_key += 1
    if "last_processed_file" in st.session_state:
      del st.session_state["last_processed_file"]

    st.rerun()
