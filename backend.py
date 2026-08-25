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

# Replace only your Fast2SMS API Key here
FAST2SMS_API_KEY = "unT74CcmX61p7XS6lLhrhkKrZdwl6OaGjLaBEhejPbfQowuqoNxfq8wIBDXS"

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

class VerifyOTPReq(BaseModel):
    phone: str
    otp: str

class SubscribeReq(BaseModel):
    phone: str
    email: str
    domain: str
    sender_email: str
    sender_password: str

def send_sms_otp(phone: str, otp: str):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = f"variables_values={otp}&route=otp&numbers={phone}"
    headers = {
        'authorization': FAST2SMS_API_KEY,
        'Content-Type': "application/x-www-form-urlencoded"
    }
    try:
        requests.post(url, data=payload, headers=headers)
    except Exception as e:
        print("SMS Error:", e)

def send_dynamic_email(sender_email: str, sender_pass: str, receiver_email: str, domain: str):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"🚀 AI Spot Tech Update: {domain}"
    
    body = f"Hello!\n\nYour spot subscription for topic {domain} is active.\n\nBest,\nAutomated System"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        clean_pass = sender_pass.replace(" ", "").strip()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email.strip(), clean_pass)
        server.sendmail(sender_email.strip(), receiver_email.strip(), msg.as_string())
        server.quit()
    except Exception as e:
        print("Email Dispatch Error:", e)

@app.post("/send-otp")
def trigger_otp(req: SendOTPReq):
    otp = str(random.randint(100000, 999999))
    otp_store[req.phone] = otp
    send_sms_otp(req.phone, otp)
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
