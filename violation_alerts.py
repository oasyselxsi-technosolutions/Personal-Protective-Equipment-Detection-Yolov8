import redis
import hashlib
import time
import smtplib
from twilio.rest import Client
from flask_socketio import SocketIO

# Remove test code from main module; this should be in your test file, not here.
# Redis and cooldown config
redis_client = redis.Redis(host='localhost', port=6379, db=0)
VIOLATION_ALERT_COOLDOWN = 20  # seconds

# Email/SMS config (replace with your credentials)
EMAIL_FROM = "your@email.com"
EMAIL_TO = "recipient@email.com"
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USER = "your@email.com"
SMTP_PASS = "yourpassword"

TWILIO_SID = "your_twilio_sid"
TWILIO_TOKEN = "your_twilio_token"
TWILIO_FROM = "+1234567890"
TWILIO_TO = "+1987654321"

# Hashing and deduplication

def hash_violation(violation):
    key = f"{violation['type']}|{violation['location']}|{violation.get('bbox', '')}"
    return hashlib.sha256(key.encode()).hexdigest()

def should_send_alert(violation):
    v_hash = hash_violation(violation)
    last_sent = redis_client.get(v_hash)
    now = int(time.time())
    if last_sent and now - int(last_sent) < VIOLATION_ALERT_COOLDOWN:
        return False
    redis_client.setex(v_hash, VIOLATION_ALERT_COOLDOWN, now)
    return True

# Email/SMS/WebSocket

def send_email(subject, body):
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(EMAIL_FROM, EMAIL_TO, message)

def send_sms(body):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(body=body, from_=TWILIO_FROM, to=TWILIO_TO)

def broadcast_violation(socketio: SocketIO, violation):
    socketio.emit('violation_alert', violation)
