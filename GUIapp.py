
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Country & Transport Inputs", page_icon="🌍", layout="wide")

# --------------------------------
# Helpers: session defaults & utils
# --------------------------------
YEARS = list(range(2020, 2051, 5))
FUEL_COLS = ["Gasoline (%)", "Diesel (%)", "Electric (%)", "Biofuel (%)"]

def default_transport_df():
    # Start with a simple default split that sums to 100 across all years
    base = {
        "Gasoline (%)": 30.0,
        "Diesel (%)": 40.0,
        "Electric (%)": 20.0,
        "Biofuel (%)": 10.0,
    }
    df = pd.DataFrame([base.copy() for _ in YEARS], index=YEARS)
    df.index.name = "Year"
    df["Total (%)"] = df[FUEL_COLS].sum(axis=1)
    return df

def init_state():
    defaults = {
        # Main input
        "country": "Australia",
        "scenario": "Business-as-usual",
        "carbon_budget": "1.5 °C",
        # Transport input
        "transport_km_2050_pct": 120,  # % of 2020
        # Data table for fuel shares
        "transport_df": default_transport_df(),
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

def recompute_totals():
    df = st.session_state["transport_df"].copy()
    df["Total (%)"] = df[FUEL_COLS].sum(axis=1)
    st.session_state["transport_df"] = df
    return df

init_state()

st.title("🌍 Country & Transport Inputs")

# -----------------------------
# Tabs
# -----------------------------
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
            help="Select the jurisdiction to model."
        )

    with col2:
        st.selectbox(
            "Scenario",
            options=["Business-as-usual", "100% renewables", "IEA"],
            key="scenario",
            help="Choose the scenario framing for the run."
        )

    with col3:
        st.selectbox(
            "Carbon budget",
            options=["1.5 °C", "1.6 °C", "1.7 °C"],
            key="carbon_budget",
            help="Select the global temperature constraint to align with."
        )

    st.success("Main input selections captured. Proceed to the **Transport input** tab to set transport assumptions.")

# =============================
# Tab 2 — Transport input
# =============================
with tab_transport:
    st.subheader("Transport input")

    st.slider(
        "Transport km in 2050 (as % of 2020 values)",
        min_value=0, max_value=300, step=5,
        key="transport_km_2050_pct",
        help="Aggregate transport activity proxy. For example, 120% means 20% higher than 2020."
    )

    st.markdown("#### Fuel mix by year (2020–2050, 5-year steps)")
    st.caption("Manually enter the shares for gasoline, diesel, electric, and biofuel. The **Total %** column shows whether each year sums to 100.")

    # Editable table for fuel shares
    edited = st.data_editor(
        st.session_state["transport_df"][FUEL_COLS],  # expose only editable cols
        num_rows="fixed",
        use_container_width=True,
        key="transport_editor",
        column_config={
            "Gasoline (%)": st.column_config.NumberColumn(
                "Gasoline (%)", min_value=0.0, max_value=100.0, step=0.1, help="Share of transport energy in the selected year."
            ),
            "Diesel (%)": st.column_config.NumberColumn(
                "Diesel (%)", min_value=0.0, max_value=100.0, step=0.1
            ),
            "Electric (%)": st.column_config.NumberColumn(
                "Electric (%)", min_value=0.0, max_value=100.0, step=0.1
            ),
            "Biofuel (%)": st.column_config.NumberColumn(
                "Biofuel (%)", min_value=0.0, max_value=100.0, step=0.1
            ),
        }
    )

    # Merge edits back into session_state, recompute totals, and display totals
    df = st.session_state["transport_df"].copy()
    df.loc[:, FUEL_COLS] = edited[FUEL_COLS]
    st.session_state["transport_df"] = df
    df = recompute_totals()

    st.markdown("##### Totals by year")
    st.dataframe(df[["Total (%)"]], use_container_width=True)

    # Validation message
    off_years = df.index[(df["Total (%)"].round(2) != 100.00)].tolist()
    if off_years:
        st.warning(
            f"The following years do **not** sum to 100%: {', '.join(map(str, off_years))}. "
            "Please adjust the shares so each year totals 100%."
        )
    else:
        st.success("All years sum to 100% ✔")

# =============================
# Tab 3 — Outputs
# =============================
with tab_outputs:
    st.subheader("Results (echo of inputs)")

    # Summary
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Country", st.session_state["country"])
    c2.metric("Scenario", st.session_state["scenario"])
    c3.metric("Carbon budget", st.session_state["carbon_budget"])
    c4.metric("Transport km in 2050", f'{st.session_state["transport_km_2050_pct"]}% of 2020')

    st.divider()
    st.markdown("#### Transport fuel shares (with totals)")
    out_df = st.session_state["transport_df"].copy()
    st.dataframe(out_df, use_container_width=True)

    # Optional guidance / hook for your model
    st.info(
        "When you’re ready, replace this tab with your model run and visualizations.\n"
        "You can consume the inputs from `st.session_state` and `st.session_state['transport_df']`."
    )

    st.code(
        """# Example: use these inputs in your model
country = st.session_state["country"]
scenario = st.session_state["scenario"]
carbon_budget = st.session_state["carbon_budget"]
transport_km_2050_pct = st.session_state["transport_km_2050_pct"]
fuel_shares = st.session_state["transport_df"]  # pandas DataFrame indexed by Year
# results = run_model(country, scenario, carbon_budget, transport_km_2050_pct, fuel_shares)
""",
        language="python"
    )
    #comment
