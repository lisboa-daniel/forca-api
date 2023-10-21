from flask import Flask, request, jsonify
import sqlite3


app = Flask(__name__)

conn = sqlite3.connect('bd.db', check_same_thread=False)
cursor = conn.cursor()

############################################################
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
            conn.commit()
            return jsonify({"message": "User Successfully Registered"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/set_icon', methods=['POST'])
def set_icon():
    data = request.get_json()
    username = data['username']
    icon = data['icon']
    try:
        cursor.execute(f"""UPDATE tb_user 
                        SET icon = '{icon}'
                        WHERE username = '{username}'
                        """)
        conn.commit()
        return jsonify({"message": "Icon Updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_icon', methods=['POST'])
def get_icon():
    data = request.get_json()
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

@app.route('/api/coin_increment', methods=['POST'])
def coin_increment():
    data = request.get_json()
    username = data['username']
    amount = data['amount']

    try:
        cursor.execute(f"""UPDATE tb_user 
                            SET coins = coins + {amount}
                            "WHERE username = '{username}' """)
        conn.commit()
        return jsonify({"message": "amount added"})       
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# TODO
# @app.route('api/coin_decrement', methos=['UPDATE'])
# def coin_decrement():

#     username = data['username']
#     amount = data['amount']

#     try:
#         cursor.execute(f"""UPDATE tb_user 
#                             SET coins = coins - {amount}
#                             "WHERE username = '{username}' """)
#         return jsonify({"message": "amount subtracted"})       
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


@app.route('/api/get_coins', methods=['POST'])
def get_coins():
    data = request.get_json()
    username = data['username']
    try:
        cursor.execute(f"""SELECT coins 
                           FROM tb_user 
                           WHERE username='{username}'
                           """)
        coins = cursor.fetchone()
        if coins:
            coin_amount = coins[0]
            return ({"message":str(coin_amount)}), 200
        else:
            return jsonify({"message":"coin amount not found" }), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/exp_increment', methods=['POST'])
def exp_increment():
    data = request.get_json()
    username = data['username']
    amount = data['amount']

    try:
        cursor.execute(f"""UPDATE tb_user 
                            SET xp = xp + {amount}
                            "WHERE username = '{username}'""")
        conn.commit()
        return jsonify({"message": "exp amount added"})       
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_exp', methods=['POST'])
def get_exp():
    data = request.get_json()
    username = data['username']
    try:
        cursor.execute(f"""SELECT xp 
                           FROM tb_user 
                           WHERE username='{username}'
                           """)
        exp = cursor.fetchone()
        if exp:
            exp_amount = exp[0]
            return ({"message":str(exp_amount)}), 200
        else:
            return jsonify({"message":"exp amount not found" }), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_level', methods=['POST'])
def get_level():
    data = request.get_json()
    username = data['username']
    query= f"""SELECT level
                FROM tb_user 
                WHERE username='{username}'
            """
    try:
        cursor.execute(query)
        level = cursor.fetchone()
        if level:
            level_value = level[0]
            return ({"message":str(level_value)}), 200
        else:
            return jsonify({"message":"level not found" }), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_item1', methods=['POST'])
def get_item1():
    data = request.get_json()
    username = data['username']
    ...
@app.route('/api/set_item1', methods=['POST'])
def set_item1():
    data = request.get_json()
    username = data['username']
    conn.commit()
    ...
@app.route('/api/get_item2', methods=['POST'])
def get_item2():
    data = request.get_json()
    username = data['username']
    ...
@app.route('/api/set_item2', methods=['POST'])
def set_item2():
    data = request.get_json()
    username = data['username']
    conn.commit()
    ...
@app.route('/api/get_item3', methods=['POST'])
def get_item3():
    data = request.get_json()
    username = data['username']
    ...
@app.route('/api/set_item3', methods=['POST'])
def set_item3():
    data = request.get_json()
    username = data['username']
    conn.commit()
    ...
#######################################################################
if __name__ == '__main__':
    app.run(debug=True)
