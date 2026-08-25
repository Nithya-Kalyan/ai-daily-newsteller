import streamlit as st
import requests

BACKEND_URL = "https://ai-daily-newsteller.onrender.com"

st.set_page_config(page_title="AI Tech Updates", page_icon="⚡", layout="centered")

st.title("⚡ Direct AI Tech Newsletter Dispatch")
st.caption("Enter phone, email credentials and get instant tech update")

with st.form("quick_newsletter_form"):
    phone = st.text_input("Mobile Phone Number", max_chars=10, placeholder="9876543210")
    receiver_email = st.text_input("Receiver Email Address", placeholder="receiver@gmail.com")
    domain_choice = st.selectbox("Select Tech Domain Topic", ["AI & Machine Learning", "Cloud Infrastructure", "Cybersecurity"])
    
    st.divider()
    st.subheader("Sender Credentials")
    sender_email = st.text_input("Sender Gmail Address", placeholder="sender@gmail.com")
    sender_password = st.text_input("Sender App Password (16 digits)", type="password")
    
    submitted = st.form_submit_button("Dispatch Spot Tech Update 🚀", use_container_width=True)
    
    if submitted:
        if phone and receiver_email and sender_email and sender_password:
            payload = {
                "phone": phone,
                "receiver_email": receiver_email,
                "domain": domain_choice,
                "sender_email": sender_email,
                "sender_password": sender_password
            }
            with st.spinner("Dispatching update to target inbox..."):
                try:
                    res = requests.post(f"{BACKEND_URL}/subscribe-direct", json=payload)
                    if res.status_code == 200:
                        st.balloons()
                        st.success(f"🎉 Spot Tech Update sent directly to {receiver_email}!")
                    else:
                        st.error("Failed to send email. Verify App Password / Email details.")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.warning("Please fill in all form fields.")
