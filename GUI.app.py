
import streamlit as st
import pycountry

st.set_page_config(page_title="Country Selector", page_icon="🌍", layout="centered")

# ---------- Data ----------
def get_countries():
    """Return a sorted list of country names using pycountry."""
    names = []
    for c in pycountry.countries:
        # Use the common name if present, else the official name, else name
        name = getattr(c, "common_name", None) or getattr(c, "official_name", None) or c.name
        names.append(name)
    # Add a few custom regions if you want (optional)
    names.extend(["EU-27", "Global"])
    return sorted(set(names), key=lambda x: x.lower())

COUNTRIES = get_countries()

# ---------- UI ----------
st.title("🌍 Country Selector")
st.caption("A minimal Streamlit UI ready for Streamlit Cloud deployment")

with st.sidebar:
    st.header("Controls")
    st.write("Pick a country or region:")
    selected = st.selectbox("Country", options=COUNTRIES, index=COUNTRIES.index("Australia") if "Australia" in COUNTRIES else 0)
    multi = st.multiselect("Compare with (optional)", options=[c for c in COUNTRIES if c != selected], default=[])

st.subheader("Your selection")
st.write(f"**Primary:** {selected}")
if multi:
    st.write("**Compare with:**", ", ".join(multi))
else:
    st.write("_No comparison selected._")

st.divider()

# Example content/output (replace with your model or data later)
st.info(
