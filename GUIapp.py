
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

