import streamlit as st
import requests

BACKEND_URL = "https://ai-daily-newsteller.onrender.com"

st.set_page_config(page_title="Dynamic AI Update", page_icon="⚡", layout="centered")

st.title("⚡ Direct Dynamic Newsletter Pipeline")

if "step" not in st.session_state:
    st.session_state.step = 1
if "phone" not in st.session_state:
    st.session_state.phone = ""

# STEP 1: Phone & Fast2SMS Key Spot Input
if st.session_state.step == 1:
    st.subheader("Step 1: Mobile OTP Verification 📱")
    phone_input = st.text_input("Enter Mobile Phone (10 digits)", max_chars=10)
    fast2sms_key = st.text_input("Fast2SMS Dev API Key", type="password")
    
    if st.button("Trigger OTP 📲"):
        if phone_input and fast2sms_key:
            res = requests.post(f"{BACKEND_URL}/send-otp", json={
                "phone": phone_input,
                "fast2sms_api_key": fast2sms_key
            })
            if res.status_code == 200:
                st.session_state.phone = phone_input
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Failed to send OTP. Check API Key.")
        else:
            st.warning("Please fill Mobile Number & API Key.")

# STEP 2: Enter Phone OTP
elif st.session_state.step == 2:
    st.subheader("Step 2: Enter OTP Code 🔒")
    otp_code = st.text_input("6-Digit OTP Received on Phone", max_chars=6)
    
    if st.button("Verify Phone OTP ✅"):
        res = requests.post(f"{BACKEND_URL}/verify-otp", json={
            "phone": st.session_state.phone,
            "otp": otp_code
        })
        if res.status_code == 200:
            st.session_state.step = 3
            st.rerun()
        else:
            st.error("Invalid OTP code.")

# STEP 3: Take Email Spot Input & Dispatch Immediately
elif st.session_state.step == 3:
    st.success("📱 Phone Verified!")
    st.subheader("Step 3: Setup Delivery Email & Preferences ✉️")
    
    target_email = st.text_input("Receiver Target Email Address")
    sender_email = st.text_input("Dispatch Sender Email Address")
    sender_pass = st.text_input("Sender App Password", type="password")
    domain = st.selectbox("Preferred Topic Domain", ["AI & ML", "Cloud", "Cybersecurity"])
    
    if st.button("Dispatch Spot Tech Update 🚀"):
        if target_email and sender_email and sender_pass:
            payload = {
                "phone": st.session_state.phone,
                "email": target_email,
                "domain": domain,
                "sender_email": sender_email,
                "sender_password": sender_pass
            }
            res = requests.post(f"{BACKEND_URL}/subscribe", json=payload)
            if res.status_code == 200:
                st.balloons()
                st.success(f"Spot tech update sent directly to {target_email}!")
            else:
                st.error("Dispatch Failed.")
