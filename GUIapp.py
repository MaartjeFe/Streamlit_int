
import streamlit as st
import requests

API_URL = st.secrets.get("API_URL", "http://127.0.0.1:8000")  # or your deployed URL

st.set_page_config(page_title="Append Text Demo (API)", page_icon="🔌", layout="centered")
st.title("Append Text Demo (API)")
st.caption(f"Backend: {API_URL}")

# Optional: quick health check
status = st.empty()
try:
    r = requests.get(f"{API_URL}/health", timeout=3)
    if r.ok and r.json().get("status") == "ok":
        status.success("Backend connected")
    else:
        status.warning("Backend reachable but not healthy")
except Exception as e:
    status.error(f"Backend not reachable: {e}")

user_text = st.text_input("Your text:", value="", placeholder="Type something...")
suffix = st.text_input("Suffix (optional):", value=" — processed")

if st.button("Process"):
    try:
        with st.spinner("Calling backend..."):
            resp = requests.post(f"{API_URL}/append",
                                 json={"text": user_text, "suffix": suffix},
                                 timeout=10)
        if resp.ok:
            st.subheader("Result")
            st.code(resp.json()["result"])
        else:
            st.error(f"Backend error: {resp.status_code} {resp.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")
