import streamlit as st
import requests

st.set_page_config(page_title="AI Digest - Ting Sound Test", page_icon="🔔", layout="centered")

st.title("🔔 Sound Notification AI Dispatcher")
st.write("Send email from one account to another to trigger the phone's **Ting!** alert sound.")

with st.form("sound_test_form"):
    name = st.text_input("Subscriber Name")
    
    st.markdown("**1. Sender Credentials (Mail pampinche account):**")
    sender_email = st.text_input("Sender Gmail Address")
    sender_app_pass = st.text_input("Sender 16-Digit App Password", type="password")
    
    st.markdown("**2. Target Phone Inbox (Notification ravalsina account):**")
    receiver_email = st.text_input("Receiver Target Email Address")
    
    domain = st.selectbox("Preferred Topic Domain", ["Software Engineering", "Cloud Systems", "AI & ML", "Cybersecurity"])
    
    submitted = st.form_submit_button("Dispatch & Trigger Sound Alert 🔊")

if submitted:
    if name and sender_email and sender_app_pass and receiver_email:
        payload = {
            "name": name,
            "sender_email": sender_email,
            "sender_app_password": sender_app_pass.replace(" ", ""),
            "receiver_email": receiver_email,
            "domain": domain
        }
        try:
            res = requests.post("http://127.0.0.1:8000/subscribe", json=payload)
            if res.status_code == 200:
                st.success(f"🎉 Success! Update dispatched from {sender_email} to {receiver_email}. Check receiver phone for sound alert!")
            else:
                st.error("Backend dispatch error.")
        except Exception:
            st.error("Backend not reachable. Run `python backend.py`.")
    else:
        st.warning("Please fill all required inputs.")