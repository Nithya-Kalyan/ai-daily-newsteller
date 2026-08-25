from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import smtplib
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

# Replace with your actual credentials
SYSTEM_SENDER_EMAIL = "kalyankumarjalli07@gmail.com"  
SYSTEM_APP_PASSWORD = "uqddqmoipeijmnqr"  
OPENAI_API_KEY = "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"          

client = OpenAI(api_key=OPENAI_API_KEY)

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
    try:
        print("--> Generating AI Content via OpenAI...")
        prompt = f"Write 3 brief bullet points on latest developments in {domain}."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"!!! OPENAI ERROR: {str(e)}")
        return f"Daily Updates for {domain}:\n- Advanced infrastructure development\n- Automated AI workflows"

def send_instant_newsletter(receiver_email: str, phone: str, domain: str):
    ai_article = generate_ai_content(domain)
    
    msg = MIMEMultipart()
    msg['From'] = SYSTEM_SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = f"⚡ AI Daily Digest: {domain}"
    
    body = f"Hi!\n\nHere is your update for {domain}:\n\n{ai_article}\n\nBest regards,\nAI Newsletter Team"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        print("--> Connecting to SMTP Server...")
        clean_pass = SYSTEM_APP_PASSWORD.replace(" ", "").strip()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SYSTEM_SENDER_EMAIL.strip(), clean_pass)
        server.sendmail(SYSTEM_SENDER_EMAIL.strip(), receiver_email.strip(), msg.as_string())
        server.quit()
        print(f" SUCCESS: Mail delivered to {receiver_email}")
    except Exception as e:
        print(f"!!! SMTP DISPATCH ERROR: {str(e)}")

@app.post("/subscribe-direct")
def subscribe_direct(req: UserSubscribeReq):
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
        
    # Synchronous Execution so errors print immediately in Render Logs
    send_instant_newsletter(req.email, req.phone, req.domain)
    return {"status": "success", "message": "Newsletter Dispatched"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
