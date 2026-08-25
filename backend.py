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

class QuickDispatchReq(BaseModel):
    phone: str
    receiver_email: str
    domain: str
    sender_email: str
    sender_password: str

def send_dynamic_email(sender_email: str, sender_pass: str, receiver_email: str, domain: str):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"🚀 AI Spot Tech Update: {domain}"
    
    body = (
        f"Hello!\n\n"
        f"Here is your daily tech update for {domain}:\n"
        f"1. AI Agents pushing autonomous execution boundaries.\n"
        f"2. Cloud Infrastructure scalable architectures optimized.\n\n"
        f"Best regards,\nAI Newsletter System"
    )
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

@app.post("/subscribe-direct")
def subscribe_direct(req: QuickDispatchReq, background_tasks: BackgroundTasks):
    try:
        conn = sqlite3.connect('newsletter.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO subscribers (phone, email, domain) VALUES (?, ?, ?)",
            (req.phone, req.receiver_email, req.domain)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB Error:", e)
        
    background_tasks.add_task(
        send_dynamic_email, 
        req.sender_email, 
        req.sender_password, 
        req.receiver_email, 
        req.domain
    )
    return {"status": "success", "message": "Newsletter Sent"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
