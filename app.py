from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/eventmanagement")
mongo_db = mongo_client["eventmanagement"]
mongo_events = mongo_db["events"]
mongo_registrations = mongo_db["registrations"]

# DB setup
def init_db():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            date TEXT,
            location TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            name TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    events = list(mongo_events.find())
    return render_template('home.html', events=events)

@app.route('/event/<event_id>')
def event_detail(event_id):
    from bson.objectid import ObjectId
    event = mongo_events.find_one({"_id": ObjectId(event_id)})
    return render_template('event_detail.html', event=event)

@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']

        # Save to MongoDB
        mongo_events.insert_one({
            "title": title,
            "description": description,
            "date": date,
            "location": location
        })
        return redirect(url_for('home'))
    return render_template('add_event.html')

@app.route('/register/<event_id>', methods=['POST'])
def register(event_id):
    name = request.form['name']
    email = request.form['email']

    # Save to MongoDB
    mongo_registrations.insert_one({
        "event_id": event_id,
        "name": name,
        "email": email
    })
    return redirect(url_for('event_detail', event_id=event_id))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

