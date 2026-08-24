from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uvicorn

app = FastAPI()

# Enable CORS for Streamlit Cloud access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return (
        f"Hello {name}!\n\n"
        f"🚀 Daily Digest Update ({domain}):\n"
        f"1. Scalable architecture deployed successfully.\n"
        f"2. Multi-sender dynamic email setup active.\n"
        f"3. Operational pipelines healthy.\n\n"
        f"Best regards,\nAutomated Newsletter System"
    )

def send_dynamic_email(sender_email: str, sender_pass: str, receiver_email: str, name: str, domain: str):
    content = generate_ai_digest(name, domain)
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"🚀 Daily Automated {domain} Digest for {name}"
    msg.attach(MIMEText(content, 'plain'))

    try:
        # Strip all whitespace from App Password
        clean_pass = sender_pass.replace(" ", "").strip()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email.strip(), clean_pass)
        server.sendmail(sender_email.strip(), receiver_email.strip(), msg.as_string())
        server.quit()
        print(f"✅ DISPATCH SUCCESS: {sender_email} -> {receiver_email}")
    except Exception as e:
        print(f"❌ DISPATCH FAILED: {e}")

@app.post("/subscribe")
def subscribe_user(user: SeparateSenderRegistration, background_tasks: BackgroundTasks):
    try:
        conn = sqlite3.connect('newsletter.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO multi_sender_subscribers (name, sender_email, sender_app_password, receiver_email, domain) VALUES (?, ?, ?, ?, ?)", 
            (user.name, user.sender_email, user.sender_app_password, user.receiver_email, user.domain)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

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
