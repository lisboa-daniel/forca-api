from flask import Flask, request, jsonify
import sqlite3
import json

app = Flask(__name__)
DATABASE = "data.db"

conn = sqlite3.connect(DATABASE, check_same_thread=False)
cursor = conn.cursor()


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
            return jsonify({"message": "Login Successful"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
    
        cursor.execute(f"""SELECT * 
                           FROM tb_user 
                           WHERE username='{username}'
                           """)
        user = cursor.fetchone()

        if user:
            conn.close()  # Close the connection before returning
            return jsonify({"message": "User already exists"}), 200
        else:
            cursor.execute(
                f"""INSERT INTO tb_user (username,
                                        password, 
                                        icon, 
                                        coins, 
                                        level, 
                                        xp)
                    VALUES ('{username}',
                            '{password}',
                            '0',0,0,0)""")
            conn.commit()  # Commit the changes
            conn.close()  # Close the connection
            return jsonify({"message": "User Successfully Registered"}), 200

    except sqlite3.Error as e:
        conn.rollback()  # Roll back the changes
        conn.close()  # Close the connection
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        conn.close()  # Close the connection
        return jsonify({"error": str(e)}), 500



def create_table():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, description TEXT)")
    connection.commit()
    connection.close()

@app.route('/items', methods=['GET'])
def get_items():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    connection.close()
    return jsonify({'items': items})

@app.route('/api/user', methods=['GET'])
def get_users():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tb_user")
    items = cursor.fetchall()
    connection.close()
    
    #converte para objetos  
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

    #retorna em json
    return json.dumps(users)




@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO items (name, description) VALUES (?, ?)", (name, description))
    connection.commit()
    connection.close()
    return jsonify({'message': 'Item added successfully'})

if __name__ == '__main__':
    #create_table()
    app.run(debug=True)
