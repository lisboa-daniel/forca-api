from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# SQLite database connection
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# API endpoint to handle Unity WebGL requests
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        cursor.execute(f"""SELECT * 
                           FROM tb_user 
                           WHERE username='{username}' 
                           AND password='{password}'""")

        user = cursor.fetchone()

        if user:
            return jsonify({"message": "Login Successful"})
        else:
            return jsonify({"error": "Invalid username or password"}), 401
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
