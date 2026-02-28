from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        return jsonify({"success": True, "message": "Thank you for subscribing to BINB! Keep an eye on your inbox."})
    return jsonify({"success": False, "message": "Invalid email address."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
