from fastapi import FastAPI, BackgroundTasks, HTTPException
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

# Credentials Setup
SYSTEM_SENDER_EMAIL = "kalyankumarjalli07@gmail.com"  # Enter Host Gmail
SYSTEM_APP_PASSWORD = "your_16_digit_app_password"  # Enter 16-digit App Pass
OPENAI_API_KEY = "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"          # Enter OpenAI API Key

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
    """Generates dynamic newsletter content using OpenAI"""
    try:
        prompt = f"Write a brief, high-value daily tech newsletter update (3 bullet points) about latest trends in {domain} for technical subscribers."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI Generation Error: {e}")
        return f"Daily Updates for {domain}:\n- Advanced infrastructure development\n- Security & AI automated integration\n- Industry scalability updates"

def send_instant_newsletter(receiver_email: str, phone: str, domain: str):
    # 1. Generate AI Content dynamically
    ai_article = generate_ai_content(domain)
    
    msg = MIMEMultipart()
    msg['From'] = SYSTEM_SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = f"⚡ AI Daily Digest: {domain}"
    
    body = (
        f"Hi Subscriber!\n\n"
        f"Here is your AI-curated daily update for topic: {domain}\n\n"
        f"{ai_article}\n\n"
        f"----------------------------------------\n"
        f"Registered Phone: {phone}\n"
        f"Best regards,\nAI Automated Newsletter Engine"
    )
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        clean_pass = SYSTEM_APP_PASSWORD.replace(" ", "").strip()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SYSTEM_SENDER_EMAIL.strip(), clean_pass)
        server.sendmail(SYSTEM_SENDER_EMAIL.strip(), receiver_email.strip(), msg.as_string())
        server.quit()
        print(f"SUCCESS: AI Newsletter sent to {receiver_email}")
    except Exception as e:
        print(f"SMTP Dispatch Error: {e}")

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
    return {"status": "success", "message": "AI Newsletter Dispatched"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
