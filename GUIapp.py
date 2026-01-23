#Connecting to backend
import requests
import streamlit as st

API_URL = st.secrets["API_URL"]
API_TOKEN = st.secrets["API_TOKEN"]

def call_backend(payload):
    r = requests.post(
        f"{API_URL}/v1/run",
        json=payload,
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    r.raise_for_status()
    return r.json()

# Frontend bit


import streamlit as st
import pandas as pd

st.set_page_config(page_title="Country & Transport Inputs", page_icon="🌍", layout="wide")

# --------------------------------
# Config
# --------------------------------
YEARS = list(range(2020, 2051, 5))
FUEL_ROWS = ["Gasoline (%)", "Diesel (%)", "Electric (%)", "Biofuel (%)","Total (%)"]

# --------------------------------
# Defaults & utils
# --------------------------------
def default_transport_df():
    """
    Internally store transport fuel shares as years x fuel (rows=index=Year; columns=fuel).
    Defaults sum to 100 across all years.
    """
    base = {
        "Gasoline (%)": 30.0,
        "Diesel (%)": 40.0,
        "Electric (%)": 20.0,
        "Biofuel (%)": 10.0,
        "Total":100.0,
    }
    df = pd.DataFrame([base.copy() for _ in YEARS], index=YEARS)
    df.index.name = "Year"
    return df

def default_transport_km_wide():
    """
    Transport activity (as % of 2020) in a wide 1xN table with years as columns.
    Defaults 100 for all years, 120 for 2050.
    """
    vals = {y: 100.0 for y in YEARS}
    vals[2050] = 120.0
    km_df = pd.DataFrame([vals], index=["Transport km (% of 2020)"])
    return km_df

def init_state():
    defaults = {
        # Main
        "country": "Australia",
        "scenario": "Business-as-usual",
        "carbon_budget": "1.5 °C",
        # Transport data
        "transport_df": default_transport_df(),            # years (rows) × fuels (cols)
        "transport_km_wide": default_transport_km_wide(),  # 1 row × YEARS cols
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

# --------------------------------
# App
# --------------------------------
init_state()
st.title("🌍 Country & Transport Inputs")

tab_main, tab_transport, tab_outputs = st.tabs(["🧩 Main input", "🚗 Transport input", "📊 Outputs"])

# =============================
# Tab 1 — Main input
# =============================
with tab_main:
    st.subheader("Main input")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.selectbox(
            "Country",
            options=[
                "Australia", "China", "EU-27", "United States",
                "India", "Japan", "Brazil", "South Africa"
            ],
            key="country",
        )
    with col2:
        st.selectbox(
            "Scenario",
            options=["Business-as-usual", "100% renewables", "IEA"],
            key="scenario",
        )
    with col3:
        st.selectbox(
            "Carbon budget",
            options=["1.5 °C", "1.6 °C", "1.7 °C"],
            key="carbon_budget",
        )
#helpers before defaults/utils 
def build_transport_fuel_share(df_years_fuels: pd.DataFrame) -> dict:
    """
    Convert years×fuels (% columns) into {year: {fuel_key: float}}
    Drops the 'Total (%)' row; keeps your column names as keys.
    """
    # Ensure the DataFrame has expected index/columns
    df = df_years_fuels.reindex(index=YEARS, columns=FUEL_ROWS, fill_value=0.0)
    # Drop the 'Total (%)' column if it exists (you label it both 'Total' and 'Total (%)' in places)
    # We only want fuel rows to sum to 100; backend will validate.
    fuel_cols = [c for c in df.columns if c.lower().strip() != "total (%)" and c.lower().strip() != "total"]
    out = {}
    for year in YEARS:
        shares = {}
        for fuel_col in fuel_cols:
            # Normalize keys (optional): e.g., "Gasoline (%)" -> "gasoline"
            key = fuel_col.lower().replace("(%)", "").strip()
            shares[key] = float(df.loc[year, fuel_col])
        out[int(year)] = shares
    return out

def build_transport_activity(km_wide_df: pd.DataFrame) -> dict:
    """
    Convert 1×YEARS wide table into {year: float}
    Currently your values are '% of 2020'; that's fine for the placeholder backend.
    """
    # Ensure columns are YEARS and there is exactly one row
    df = km_wide_df.reindex(columns=YEARS).iloc[0]
    return {int(y): float(df[y]) for y in YEARS}

#-------Run button

if st.button("Run model"):
    # Pull current UI state
    country = st.session_state["country"]
    scenario = st.session_state["scenario"]
    # Build payload parts
    transport_fuel_share = build_transport_fuel_share(st.session_state["transport_df"])
    transport_activity = build_transport_activity(st.session_state["transport_km_wide"])

    payload = {
        "country": country,
        "scenario": scenario,
        "transport_fuel_share": transport_fuel_share,
        "transport_activity": transport_activity,
        "other_inputs": {"carbon_budget": st.session_state.get("carbon_budget")},
    }
    try:
        resp = call_backend(payload)
        st.success("Backend call OK")
        st.write(resp)  # replace with your pretty outputs later
    except requests.HTTPError as e:
        st.error(f"HTTP error: {e} — {getattr(e.response, 'text', '')}")
    except Exception as e:
        st.error(f"Request failed: {e}")


# =============================
# Tab 2 — Transport input
# =============================
with tab_transport:
    st.subheader("Transport input")

    # -------------------------
    # Table 1) Transport km (% of 2020) — wide editor (columns = years)
    # -------------------------
    st.markdown("#### Table 1 — Transport km (% of 2020), by year (2020–2050, 5-year steps)")
    st.caption("Edit values directly. 100 = same as 2020; 120 = 20% higher than 2020.")

    # Ensure column order is YEARS
    km_wide = st.session_state["transport_km_wide"].reindex(columns=YEARS)
    km_edited = st.data_editor(
        km_wide,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            str(y): st.column_config.NumberColumn(str(y), min_value=0.0, max_value=10000.0, step=1.0)
            for y in YEARS
        },
        key="km_editor",
    )
    # Save back
    st.session_state["transport_km_wide"] = km_edited.reindex(columns=YEARS)

    st.divider()

    # -------------------------
    # Table 2) Fuel mix — wide editor (rows = fuels, columns = years)
    # -------------------------
    st.markdown("#### Table 2 — Fuel mix by year")
    st.caption("Enter shares for gasoline, diesel, electric, and biofuel. The last row shows the simple sum (Total %).")

    # Build wide version for editing: fuels (rows) × years (cols)
    df_years_fuels = st.session_state["transport_df"].reindex(index=YEARS, columns=FUEL_ROWS)  # safe reindex
    fuel_wide = df_years_fuels.T  # rows=fuel, cols=years

    # Editable table
    edited_wide = st.data_editor(
        fuel_wide,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            str(y): st.column_config.NumberColumn(str(y), min_value=0.0, max_value=100.0, step=0.1)
            for y in YEARS
        },
        key="fuel_editor",
    )

    # Persist edits: transpose back to years×fuels
    edited_years_fuels = edited_wide.T.reindex(columns=FUEL_ROWS)
    edited_years_fuels.index.name = "Year"
    st.session_state["transport_df"] = edited_years_fuels

    # ---- Append "Total (%)" row as simple sum of previous rows ----
    totals_series = edited_wide.sum(axis=0)  # per-year totals
    totals_row = pd.DataFrame(
        [totals_series.values],
        index=["Total (%)"],
        columns=edited_wide.columns,
    )
    table2_with_totals = pd.concat([edited_wide, totals_row], axis=0).reindex(columns=YEARS)

    st.markdown("##### Table 2 — Fuel mix with Total (%)")
    st.dataframe(table2_with_totals, use_container_width=True)

# =============================
# Tab 3 — Outputs
# =============================
with tab_outputs:
    st.subheader("Results (echo of inputs)")

    c1, c2, c3 = st.columns(3)
    c1.metric("Country", st.session_state["country"])
    c2.metric("Scenario", st.session_state["scenario"])
    c3.metric("Carbon budget", st.session_state["carbon_budget"])

    st.divider()
    st.markdown("#### Transport km (% of 2020)")
    st.dataframe(st.session_state["transport_km_wide"].reindex(columns=YEARS), use_container_width=True)

    st.markdown("#### Fuel mix (years as columns) with totals")
    df_years_fuels = st.session_state["transport_df"].reindex(index=YEARS, columns=FUEL_ROWS)
    fuel_wide_out = df_years_fuels.T
    totals_out = pd.DataFrame(
        [fuel_wide_out.sum(axis=0).values],
        columns=fuel_wide_out.columns,
        index=["Total (%)"]
    )
    st.dataframe(pd.concat([fuel_wide_out, totals_out], axis=0).reindex(columns=YEARS), use_container_width=True)

