from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    return conn

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

@app.route('/delete_event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        return jsonify({"success": True, "message": "Thank you for subscribing to BINB! Keep an eye on your inbox."})
    return jsonify({"success": False, "message": "Invalid email address."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
