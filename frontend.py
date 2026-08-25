import streamlit as st
import requests

BACKEND_URL = "https://ai-daily-newsteller.onrender.com"

st.set_page_config(page_title="AI Tech Updates", page_icon="⚡", layout="centered")

st.title("⚡ Direct AI Tech Newsletter")
st.caption("Enter phone and target email to receive instant spot tech update")

with st.form("clean_form"):
    phone = st.text_input("Mobile Phone Number", max_chars=10, placeholder="9876543210")
    receiver_email = st.text_input("Target Email Address", placeholder="user@gmail.com")
    domain_choice = st.selectbox("Select Domain Topic", ["AI & Machine Learning", "Cloud Infrastructure", "Cybersecurity"])
    
    submitted = st.form_submit_button("Get Instant Update 🚀", use_container_width=True)
    
    if submitted:
        if phone and receiver_email and "@" in receiver_email:
            payload = {
                "phone": phone,
                "email": receiver_email,
                "domain": domain_choice
            }
            with st.spinner("Dispatching update to target inbox..."):
                try:
                    res = requests.post(f"{BACKEND_URL}/subscribe-simple", json=payload)
                    if res.status_code == 200:
                        st.balloons()
                        st.success(f"🎉 Spot Tech Update dispatched directly to {receiver_email}!")
                    else:
                        st.error("Dispatch issue. Please check network.")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.warning("Please enter valid phone and target email.")
