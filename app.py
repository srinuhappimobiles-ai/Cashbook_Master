import math
import pandas as pd
import streamlit as st

# --- 1. Load Master Data (Replace with your actual Excel/DB load) ---
# Example: df_master = pd.read_excel("your_cashbook_file.xlsx")
# Getting unique sorted list of all 107 stores
if "df_master" not in st.session_state:
  # Dummy placeholder if you load from file:
  # st.session_state.df_master = pd.read_excel("path_to_file.xlsx")
  pass

# Assuming 'stores_list' contains all your 107 store names from your master sheet:
# stores_list = sorted(df_master['Store Name'].dropna().unique().tolist())

# --- 2. Sidebar Work Assignment Mode ---
st.sidebar.title("👥 Work Assignment Mode")
work_mode = st.sidebar.radio(
    "Select Mode:",
    ["👤 Single Cashier (All Stores)", "👥 Two Cashiers (Split Mode)"],
)

active_stores = []

# Fetch all stores dynamically from your main dataframe
if "df_master" in st.session_state:
  stores_list = sorted(
      st.session_state.df_master["Store Name"].dropna().unique().tolist()
  )
else:
  # Fallback to current loaded stores
  stores_list = [f"STORE_{i:03d}" for i in range(1, 108)]  # 107 stores example

total_count = len(stores_list)

if work_mode == "👤 Single Cashier (All Stores)":
  active_stores = stores_list
  st.sidebar.info(f"📋 Showing All **{len(active_stores)}** Stores.")
else:
  # Dynamic 50-50% split logic
  mid_point = math.ceil(total_count / 2)
  cashier_1_stores = stores_list[:mid_point]
  cashier_2_stores = stores_list[mid_point:]

  cashier_select = st.sidebar.selectbox(
      "Select Your Cashier ID:",
      [
          f"Cashier 1 ({len(cashier_1_stores)} Stores)",
          f"Cashier 2 ({len(cashier_2_stores)} Stores)",
      ],
  )

  if "Cashier 1" in cashier_select:
    active_stores = cashier_1_stores
  else:
    active_stores = cashier_2_stores

# --- 3. Filter and Display Main Sheet on Screen ---
st.subheader(f"📊 Cashbook Sheet ({len(active_stores)} Stores Assigned)")

# If you have df_master loaded, filter it by active_stores
if "df_master" in st.session_state:
  df_display = st.session_state.df_master[
      st.session_state.df_master["Store Name"].isin(active_stores)
  ]
  st.dataframe(df_display, use_container_width=True, height=500)
else:
  # Sample grid display of assigned stores
  df_placeholder = pd.DataFrame({
      "Store Name": active_stores,
      "Doctor Balance": 0.0,
      "Denomination": 0.0,
      "Approvals": 0.0,
      "Deposit": 0.0,
      "Status": "Pending",
  })
  st.dataframe(df_placeholder, use_container_width=True, height=500)
