import streamlit as st
import requests

# Backend Live Base URL
BACKEND_URL = "https://ai-daily-newsteller.onrender.com"

st.set_page_config(page_title="Dynamic AI Newsletter Pipeline", page_icon="⚡", layout="centered")

# Modern Streamlit UI Styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Dynamic AI Tech Updates")
st.caption("Verify Phone via OTP -> Submit Target Email -> Get Spot Tech Update")

# Session state initialization for sequential steps
if "step" not in st.session_state:
    st.session_state.step = 1
if "phone" not in st.session_state:
    st.session_state.phone = ""

# -------------------------------------------------------------------
# STEP 1: Phone Input & Fast2SMS Trigger
# -------------------------------------------------------------------
if st.session_state.step == 1:
    st.subheader("Step 1: Mobile OTP Verification 📱")
    phone_input = st.text_input("Enter Mobile Phone (10 digits)", max_chars=10, placeholder="9876543210")
    
    if st.button("Trigger OTP 📲"):
        if len(phone_input) == 10 and phone_input.isdigit():
            with st.spinner("Sending OTP SMS via Fast2SMS..."):
                res = requests.post(f"{BACKEND_URL}/send-otp", json={"phone": phone_input})
                if res.status_code == 200:
                    st.session_state.phone = phone_input
                    st.session_state.step = 2
                    st.success("OTP sent to your phone number!")
                    st.rerun()
                else:
                    st.error("Failed to send OTP. Verify backend connectivity.")
        else:
            st.warning("Please enter a valid 10-digit phone number.")

# -------------------------------------------------------------------
# STEP 2: OTP Verification Spot
# -------------------------------------------------------------------
elif st.session_state.step == 2:
    st.subheader("Step 2: Enter Verification Code 🔒")
    st.info(f"OTP sent to: +91 {st.session_state.phone}")
    
    otp_input = st.text_input("6-Digit OTP Received on Phone", max_chars=6, placeholder="123456")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Verify OTP ✅"):
            if len(otp_input) == 6:
                res = requests.post(f"{BACKEND_URL}/verify-otp", json={"phone": st.session_state.phone, "otp": otp_input})
                if res.status_code == 200:
                    st.session_state.step = 3
                    st.rerun()
                else:
                    st.error("Invalid OTP entered. Try again.")
            else:
                st.warning("Enter complete 6-digit OTP.")
    with col2:
        if st.button("Change Mobile ↩️"):
            st.session_state.step = 1
            st.rerun()

# -------------------------------------------------------------------
# STEP 3: Email Input & Instant Tech Update Dispatch
# -------------------------------------------------------------------
elif st.session_state.step == 3:
    st.success("📱 Mobile Number Verified Successfully!")
    st.subheader("Step 3: Target Email & Preferences ✉️")
    
    target_email = st.text_input("Enter Your Receiver Email Address", placeholder="user@gmail.com")
    domain_choice = st.selectbox("Select Preferred Domain Topic", ["AI & Machine Learning", "Cloud Infrastructure", "Cybersecurity", "Web3 Development"])
    
    if st.button("Dispatch Spot Tech Digest 🚀"):
        if target_email and "@" in target_email:
            with st.spinner("Dispatching dynamic AI update to your inbox..."):
                payload = {
                    "phone": st.session_state.phone,
                    "email": target_email,
                    "domain": domain_choice
                }
                res = requests.post(f"{BACKEND_URL}/subscribe", json=payload)
                if res.status_code == 200:
                    st.balloons()
                    st.success(f"🎉 Spot Tech Update sent directly to {target_email}!")
                    # Sound Effect Trigger
                    st.components.v1.html("""
                        <audio autoplay>
                            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                        </audio>
                    """, height=0)
                else:
                    st.error("Subscription or dynamic mail trigger failed.")
        else:
            st.warning("Please enter a valid target email address.")
