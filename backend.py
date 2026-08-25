from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
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

# Place your fixed system sender credentials here
SYSTEM_SENDER_EMAIL = "kalyankumarjalli07@gmail.com"
SYSTEM_APP_PASSWORD = "vacoyjtdviwoccmr"

def init_db():
    conn = sqlite3.connect('newsletter.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            phone TEXT,
            email TEXT,
            domain TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class UserSubscribeReq(BaseModel):
    phone: str
    email: str
    domain: str

def send_instant_newsletter(receiver_email: str, phone: str, domain: str):
    msg = MIMEMultipart()
    msg['From'] = SYSTEM_SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = f"🚀 AI Spot Newsletter: {domain}"
    
    body = (
        f"Hello!\n\n"
        f"Welcome to AI Daily Newsletter!\n"
        f"Your spot updates for domain '{domain}' are active for Phone: {phone}.\n\n"
        f"1. Next-gen AI deployment pipelines verified.\n"
        f"2. System automation active.\n\n"
        f"Best regards,\nAI Newsletter Team"
    )
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        clean_pass = SYSTEM_APP_PASSWORD.replace(" ", "").strip()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SYSTEM_SENDER_EMAIL.strip(), clean_pass)
        server.sendmail(SYSTEM_SENDER_EMAIL.strip(), receiver_email.strip(), msg.as_string())
        server.quit()
        print("Mail delivered successfully!")
    except Exception as e:
        print("SMTP Dispatch Error:", e)

@app.post("/subscribe-direct")
def subscribe_direct(req: UserSubscribeReq, background_tasks: BackgroundTasks):
    try:
        conn = sqlite3.connect('newsletter.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO subscribers (phone, email, domain) VALUES (?, ?, ?)",
            (req.phone, req.email, req.domain)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB Error:", e)
        
    background_tasks.add_task(send_instant_newsletter, req.email, req.phone, req.domain)
    return {"status": "success", "message": "Newsletter Dispatched"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
