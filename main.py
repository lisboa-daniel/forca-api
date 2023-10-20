from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect('data.db')
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

@app.route('api/register', methods=['POST'])
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
            return jsonify({"message": "User Successfully Registered"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('api/set_icon', methods=['UPDATE'])
def set_icon():

    username = data['username']
    icon = data['icon']
    try:
        cursor.execute(f"""UPDATE tb_user 
                        SET icon = '{icon}'
                        WHERE username = '{username}'
                        """)
        return jsonify({"message": "Icon Updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('api/get_icon', methods=['POST'])
def get_icon():
    username = data['username']
    try:
        cursor.execute(f"""SELECT icon 
                           FROM tb_user 
                           WHERE username='{username}'
                           """)
        icon = cursor.fetchone()
        if icon:
            icon_binary = icon[0]
            return (send_file(io.BytesIO(icon_binary), mimetype='image/png', as_attachment=True, download_name=f'icon.png'))
        else:
            return jsonify({"message":"icon not found" }), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
