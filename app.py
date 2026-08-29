import math
import streamlit as st

# 1. Master stores list (Alphabetically sorted)
# Replace this sample list with your full dynamic list from DB or Excel
stores_list = sorted([
    "ADILABAD",
    "ALWAL",
    "ARMOOR",
    "BODHAN",
    "CHANDANAGAR",
    "DILSUKHNAGAR",
    "ECIL",
    "GAJUWAKA",
    "HANMAKONDA",
    "KHAMMAM",
    "KUKATPALLY",
    "MADHAPUR",
    "MEDCHAL",
    "NIZAMABAD",
    "SECUNDERABAD",
    "UPPAL",
    "WARANGAL",
])

# 2. Sidebar Work Mode Selector
st.sidebar.title("👥 Work Assignment Mode")
work_mode = st.sidebar.radio(
    "Select Mode:",
    ["👤 Single Cashier (All Stores)", "👥 Two Cashiers (Split Mode)"],
)

active_stores = []

if work_mode == "👤 Single Cashier (All Stores)":
  active_stores = stores_list
  st.info(f"📋 Single Mode: Loaded all **{len(active_stores)}** stores.")

else:
  # Dynamic logic to split total stores evenly into two halves
  total_count = len(stores_list)
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
    st.success(
        f"✅ **Cashier 1 Allocation:** {len(active_stores)} Stores"
        f" ({active_stores[0]} to {active_stores[-1]})"
    )
  else:
    active_stores = cashier_2_stores
    st.success(
        f"✅ **Cashier 2 Allocation:** {len(active_stores)} Stores"
        f" ({active_stores[0]} to {active_stores[-1]})"
    )

# 3. Table Rendering Filter
# Pass 'active_stores' to your main dataframe:
# df_filtered = df[df['Store Name'].isin(active_stores)]
