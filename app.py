from flask import Flask, render_template, request, jsonify
import sqlite3
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    return conn

def send_email_async(to_email, html_content):
    sender_email = "testeremail@gmail.com"
    sender_password = ""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Your Upcoming Brandon Events!"
        msg['From'] = f"Brandon Is Not Boring <{sender_email}>"
        msg['To'] = to_email

        part = MIMEText(html_content, 'html')
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"Successfully sent newsletter to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/category/<string:category_name>')
def category(category_name):
    conn = get_db_connection()
    # Fetch events for the category
    events = conn.execute('SELECT * FROM events WHERE category = ?', (category_name.lower(),)).fetchall()
    conn.close()
    return render_template('category.html', category_name=category_name.capitalize(), events=events)

@app.route('/events')
def all_events():
    conn = get_db_connection()
    # Fetch all events
    events = conn.execute('SELECT * FROM events').fetchall()
    conn.close()
    return render_template('category.html', category_name='All', events=events)

@app.route('/delete_event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/newsletter')
def newsletter():
    return render_template('newsletter.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    
    # Strictly validate against the standard Email Regex format format
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"success": False, "message": "Invalid email address format."}), 400
        
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events ORDER BY date_time ASC').fetchall()
    conn.close()
    
    # Render the template into an HTML string to send via email
    html_content = render_template('email_template.html', events=events)
    
    # Start a background thread to prevent UI freezing
    email_thread = threading.Thread(target=send_email_async, args=(email, html_content))
    email_thread.start()
    
    return jsonify({"success": True, "message": "Thank you for subscribing! We are scanning and preparing your personalized events email right now."})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
