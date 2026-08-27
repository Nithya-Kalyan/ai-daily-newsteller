from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Render Environment Variables nunchi auto pick aithayi (No Hardcode)
SYSTEM_SENDER_EMAIL = os.getenv("SYSTEM_SENDER_EMAIL", "jj3457731@gmail.com")
SYSTEM_APP_PASSWORD = os.getenv("SYSTEM_APP_PASSWORD", "shjufljpxgzmmpmn")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")

client = OpenAI(api_key=OPENAI_API_KEY.strip()) if OPENAI_API_KEY else None

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

def generate_ai_content(domain: str) -> str:
    if not client:
        return f"Daily Updates for {domain}:\n- AI automation active\n- System online"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Write 3 daily tech bullets on {domain}."}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OPENAI ERROR: {str(e)}")
        return f"Daily Updates for {domain}:\n- AI automation online\n- Infrastructure active"

def send_instant_newsletter(receiver_email: str, phone: str, domain: str):
    ai_article = generate_ai_content(domain)
    
    msg = MIMEMultipart()
    msg['From'] = SYSTEM_SENDER_EMAIL.strip()
    msg['To'] = receiver_email.strip()
    msg['Subject'] = f"⚡ AI Daily Digest: {domain}"
    
    body = f"Hi!\n\nHere is your update for {domain}:\n\n{ai_article}\n\nPhone Registered: {phone}"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        clean_pass = SYSTEM_APP_PASSWORD.replace(" ", "").strip()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SYSTEM_SENDER_EMAIL.strip(), clean_pass)
        server.sendmail(SYSTEM_SENDER_EMAIL.strip(), receiver_email.strip(), msg.as_string())
        server.quit()
        print(f"SUCCESS: Delivered to {receiver_email}")
        return True
    except Exception as e:
        print(f"SMTP DISPATCH ERROR: {str(e)}")
        return False

@app.post("/subscribe-direct")
def subscribe_direct(req: UserSubscribeReq):
    try:
        conn = sqlite3.connect('newsletter.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subscribers (phone, email, domain) VALUES (?, ?, ?)", 
                       (req.phone, req.email, req.domain))
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB Error:", e)

    status = send_instant_newsletter(req.email, req.phone, req.domain)
    return {"status": "completed", "email_sent": status}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
