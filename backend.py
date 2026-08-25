from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import requests
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

class SimpleSubscribeReq(BaseModel):
    phone: str
    email: str
    domain: str

def send_instant_notification(receiver_email: str, phone: str, domain: str):
    # Free public email dispatcher (No passwords needed)
    try:
        url = "https://formsubmit.co/ajax/" + receiver_email.strip()
        data = {
            "subject": f"🚀 AI Spot Newsletter: {domain}",
            "message": f"Welcome! Your subscription for domain '{domain}' is active for phone: {phone}.",
            "_template": "basic"
        }
        requests.post(url, data=data)
    except Exception as e:
        print("Dispatcher Error:", e)

@app.post("/subscribe-simple")
def subscribe_simple(req: SimpleSubscribeReq, background_tasks: BackgroundTasks):
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
        
    background_tasks.add_task(send_instant_notification, req.email, req.phone, req.domain)
    return {"status": "success", "message": "Email Dispatched"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
