from flask import Flask, request, jsonify
import psycopg2
import json

app = Flask(__name__)
DATABASE_URL = "postgres://forca.fatec:Cwoy8X5OfSnM@ep-morning-glitter-99273928.us-east-2.aws.neon.tech/neondb?options=endpoint%3D[ep-morning-glitter-99273928]&sslmode=require"

# Database connection function
def connect_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# Update your route functions to use PostgreSQL




# /api/register
@app.route('/api/register', methods=['POST'])
def register():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
    
        cursor.execute("""SELECT * 
                        FROM tb_user 
                        WHERE username=%s""", (username,))
        user = cursor.fetchone()

        if user:
            return jsonify({"message": "User already exists"}), 200
        else:
            cursor.execute(
                """INSERT INTO tb_user (username, password, icon, coins, level, xp)
                VALUES (%s, %s, %s, %s, %s, %s)""", (username, password, '0', 0, 0, 0))
            conn.commit()
            conn.close()
            return jsonify({"message": "User Successfully Registered"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# /api/user
@app.route('/api/user', methods=['GET'])
def get_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tb_user")
    items = cursor.fetchall()
    conn.close()
    
    # Convert to objects  
    users = []
    for item in items:
        user = {
            "id": item[0],
            "username": item[1],
            "password": item[2],
            "icon": item[3],
            "coins": item[4],
            "level": item[5],
            "xp": item[6]
        }
        users.append(user)

    # Return as JSON
    return json.dumps(users)

# /api/userbynick/<string:username>
@app.route('/api/userbynick/<string:username>', methods=['GET'])
def get_userbynick(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tb_user WHERE username=%s", (username,))
    item = cursor.fetchone()
    conn.close()

    # Check if the user exists
    if item:
        user = {
            "id": item[0],
            "username": item[1],
            "password": item[2],
            "icon": item[3],
            "coins": item[4],
            "level": item[5],
            "xp": item[6]
        }
        # Return the user as JSON
        return json.dumps(user)
    else:
        # If the user doesn't exist, return an appropriate error message
        return json.dumps({"error": "User not found"})

if __name__ == '__main__':
    app.run(debug=True)
