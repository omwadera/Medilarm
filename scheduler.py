# scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_mail import Mail, Message
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)
app.config.from_pyfile('config.py')
mail = Mail(app)

# Connect to MongoDB and get the medicines collection
client = MongoClient('mongodb://localhost:27017/')
db = client['medilarm_db']
medicines_collection = db['medicines']

# Function to send medicine alert notification
def send_medicine_alert():
    now = datetime.now()
    # Query medicines with the current time within the scheduled intake time
    due_medicines = medicines_collection.find({
        '$or': [
            {'before_breakfast': True, 'breakfast': False, 'after_breakfast': False, 'scheduled_time': now},
            # Add similar conditions for other meal times
        ]
    })

    for medicine in due_medicines:
        # Get the user's email (you need to define how users are associated with medicines in your app)
        user_email = medicine['user_email']
        # Compose the email message
        subject = 'Medicine Reminder - MediLarm'
        body = f"It's time to take your medicine: {medicine['name']}."
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[user_email])
        msg.body = body
        # Send the email
        mail.send(msg)

# Create the scheduler and schedule the task to run every minute
scheduler = BackgroundScheduler()
scheduler.add_job(send_medicine_alert, 'interval', minutes=1)

def start_scheduler():
    if not scheduler.running:
        scheduler.start()