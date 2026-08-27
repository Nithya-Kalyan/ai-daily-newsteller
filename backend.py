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
    # Direct Environment retrieval inside execution block
    api_token = os.environ.get("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")
    
    if not api_token:
        print("--> OpenAI key not configured in environment, returning template fallback.")
        return f"Daily Updates for {domain}:\n- AI automation engine active\n- Infrastructure operational\n- Real-time updates online"
    
    try:
        print("--> Calling OpenAI API...")
        client = OpenAI(api_key=api_token.strip())
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Write 3 short daily tech update bullet points on {domain}."}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"!!! OPENAI API ERROR: {str(e)}")
        return f"Daily Updates for {domain}:\n- Deep learning models processing updates\n- Infrastructure fully functional\n- System online"

def send_instant_newsletter(receiver_email: str, phone: str, domain: str):
    sender_mail = os.environ.get("jj3457731@gmail.com")
    sender_pass = os.environ.get("shjufljpxgzmmpmn")
    
    ai_article = generate_ai_content(domain)
    
    if not sender_mail or not sender_pass:
        print("!!! SMTP Error: System email credentials not configured in environment.")
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_mail.strip()
    msg['To'] = receiver_email.strip()
    msg['Subject'] = f"⚡ AI Daily Digest: {domain}"
    
    body = f"Hi!\n\nHere is your requested AI update for {domain}:\n\n{ai_article}\n\nRegistered Phone: {phone}"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        clean_pass = sender_pass.replace(" ", "").strip()
        print("--> Connecting to Gmail via SMTP_SSL (Port 465)...")
        
        # Connect via Port 465 SSL to bypass Render Port 587 restriction
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_mail.strip(), clean_pass)
        server.sendmail(sender_mail.strip(), receiver_email.strip(), msg.as_string())
        server.quit()
        
        print(f"SUCCESS: Email delivered to {receiver_email}")
        return True
    except Exception as e:
        print(f"!!! SMTP DISPATCH ERROR: {str(e)}")
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
        print("DB Log Error:", e)

    status = send_instant_newsletter(req.email, req.phone, req.domain)
    return {"status": "completed", "email_sent": status}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
