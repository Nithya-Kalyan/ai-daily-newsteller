from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uvicorn
from langchain_ollama import OllamaLLM
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = FastAPI()

try:
    llm = OllamaLLM(model="llama3.2:1b")
except Exception:
    llm = None

class SeparateSenderRegistration(BaseModel):
    name: str
    sender_email: str
    sender_app_password: str
    receiver_email: str
    domain: str

def init_db():
    conn = sqlite3.connect('newsletter.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS multi_sender_subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            sender_email TEXT,
            sender_app_password TEXT,
            receiver_email TEXT,
            domain TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def generate_ai_digest(name: str, domain: str) -> str:
    prompt = f"Draft a daily tech update for {name} in domain {domain}. Keep under 150 words with 3 news bullet points and 1 actionable tip."
    if llm:
        try:
            return llm.invoke(prompt)
        except Exception:
            pass
    return f"Hello {name},\n\nYour automated daily update for {domain}:\n- AI tooling integration standardizing.\n- Optimization in backend architecture.\n- Focus on operational reliability today."

def send_dynamic_email(sender_email: str, sender_pass: str, receiver_email: str, name: str, domain: str):
    content = generate_ai_digest(name, domain)
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"🚀 Daily Automated {domain} Digest for {name}"
    msg.attach(MIMEText(content, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_pass)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"✅ CRON/DISPATCH SUCCESS: {sender_email} -> {receiver_email}")
    except Exception as e:
        print(f"❌ DISPATCH FAILED: {e}")

# --- AUTOMATED DAILY CRON JOB FUNCTION ---
def send_daily_newsletters_to_all():
    print(f"⏰ Daily Cron Job Triggered at {datetime.now()}")
    conn = sqlite3.connect('newsletter.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, sender_email, sender_app_password, receiver_email, domain FROM multi_sender_subscribers")
    subscribers = cursor.fetchall()
    conn.close()

    for name, s_email, s_pass, r_email, domain in subscribers:
        send_dynamic_email(s_email, s_pass, r_email, name, domain)

# Background Scheduler Setup
scheduler = BackgroundScheduler()
# 📌 Daily Morning 8:00 AM ki run avvadaniki cron trigger:
scheduler.add_job(send_daily_newsletters_to_all, 'cron', hour=8, minute=0)
scheduler.start()

@app.post("/subscribe")
def subscribe_user(user: SeparateSenderRegistration, background_tasks: BackgroundTasks):
    conn = sqlite3.connect('newsletter.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO multi_sender_subscribers (name, sender_email, sender_app_password, receiver_email, domain) VALUES (?, ?, ?, ?, ?)", 
        (user.name, user.sender_email, user.sender_app_password, user.receiver_email, user.domain)
    )
    conn.commit()
    conn.close()

    # Instant welcome mail on registration
    background_tasks.add_task(
        send_dynamic_email, 
        user.sender_email, 
        user.sender_app_password, 
        user.receiver_email, 
        user.name, 
        user.domain
    )
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)