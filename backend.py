from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import random
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active verification sessions dynamically in memory
otp_store = {}
verified_phones = set()

def init_db():
    conn = sqlite3.connect('newsletter.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verified_subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            phone TEXT UNIQUE,
            email TEXT,
            domain TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class SendOTPReq(BaseModel):
    phone: str
    fast2sms_api_key: str

class VerifyOTPReq(BaseModel):
    phone: str
    otp: str

class SubscribeReq(BaseModel):
    phone: str
    email: str
    domain: str
    sender_email: str
    sender_password: str

def send_sms_otp(phone: str, otp: str, api_key: str):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = f"variables_values={otp}&route=otp&numbers={phone}"
    headers = {
        'authorization': api_key,
        'Content-Type': "application/x-www-form-urlencoded"
    }
    requests.post(url, data=payload, headers=headers)

def send_dynamic_email(sender_email: str, sender_pass: str, receiver_email: str, domain: str):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"🚀 Live AI Tech Update: {domain}"
    
    body = (
        f"Hello!\n\n"
        f"🔥 Dynamic Spot Update for {domain}:\n"
        f"1. AI Agents & autonomous workflows running dynamically.\n"
        f"2. Phone verification via Fast2SMS successfully passed.\n"
        f"3. Spot dispatch architecture initialized without backend hardcoding.\n\n"
        f"Best regards,\nAutomated AI System"
    )
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        clean_pass = sender_pass.replace(" ", "").strip()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email.strip(), clean_pass)
        server.sendmail(sender_email.strip(), receiver_email.strip(), msg.as_string())
        server.quit()
        print("✅ Email Triggered Successfully")
    except Exception as e:
        print("❌ Email Dispatch Error:", e)

@app.post("/send-otp")
def trigger_otp(req: SendOTPReq):
    otp = str(random.randint(100000, 999999))
    otp_store[req.phone] = otp
    send_sms_otp(req.phone, otp, req.fast2sms_api_key)
    return {"status": "success"}

@app.post("/verify-otp")
def verify_otp(req: VerifyOTPReq):
    if otp_store.get(req.phone) == req.otp:
        verified_phones.add(req.phone)
        del otp_store[req.phone]
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="Invalid OTP")

@app.post("/subscribe")
def subscribe(req: SubscribeReq, background_tasks: BackgroundTasks):
    if req.phone not in verified_phones:
        raise HTTPException(status_code=400, detail="Phone OTP Not Verified")
    
    try:
        conn = sqlite3.connect('newsletter.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO verified_subscribers (phone, email, domain) VALUES (?, ?, ?)",
            (req.phone, req.email, req.domain)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB Error:", e)
        
    background_tasks.add_task(
        send_dynamic_email, 
        req.sender_email, 
        req.sender_password, 
        req.email, 
        req.domain
    )
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
