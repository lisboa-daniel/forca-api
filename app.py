from flask import Flask, request, jsonify
import psycopg2
import json

app = Flask(__name__)
DATABASE_URL = "postgres://forca.fatec:Cwoy8X5OfSnM@ep-morning-glitter-99273928.us-east-2.aws.neon.tech/neondb?options=endpoint%3Dep-morning-glitter-99273928&sslmode=require"

# Database connection function
def connect_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

conn = connect_db()
cursor = conn.cursor()

# Update your route functions to use PostgreSQL

# CADASTRO DE USUARIO
@app.route('/api/login', methods=['POST'])
def login():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        cursor.execute("""SELECT * 
                        FROM tb_user 
                        WHERE username=%s 
                        AND password=%s""", (username, password))

        user = cursor.fetchone()
        conn.close()
        if user:
            return jsonify({"message": "Login Successful"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login2', methods=['POST'])
def login2():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        cursor.execute("""SELECT * 
                        FROM tb_user 
                        WHERE username=%s 
                        AND password=%s""", (username, password))

        item = cursor.fetchone()
        
        
        if item:
            user = {
                "id": item[0],
                "username": item[1],
                "password": item[2],
                "icon": item[3],
                "coins": item[4],
                "level": item[5],
                "xp": item[6],
                "item1": item[7],
                "item2": item[8],
                "item3": item[9],
                "character": {
                    "color": "",
                    "head": "",
                    "top": "",
                    "bottom": ""
                }
            }
            cursor.execute("SELECT color,head,top,bottom FROM tb_character WHERE username=%s", (username,))
            item =  cursor.fetchone();
        
        
            user["character"]["color"] = item[0];
            user["character"]["head"] = item[1];
            user["character"]["top"] = item[2];
            user["character"]["bottom"] = item[3];
        else:
            user = None
            
        conn.close()
        if user:
            return jsonify(user), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        color = data.get('color', 'azul')  # Default color is blue if not provided

        cursor.execute("""SELECT * 
                        FROM tb_user 
                        WHERE username=%s""", (username,))
        user = cursor.fetchone()

        if user:
            return jsonify({"message": "User already exists"}), 200
        else:
            
            user = {
                "id": 0,
                "username": username,
                "password": password,
                "icon": "",
                "coins": 300,
                "level": 1,
                "xp": 0,
                "item1": "potion",
                "item2": "lapiseira",
                "item3": "sopa",
                "character": {
                    "color": "azul",
                    "head": "",
                    "top": "",
                    "bottom": ""
                    }
                }
            
            cursor.execute(
                """INSERT INTO tb_user (username, password, icon, coins, level, xp, item1,item2,item3)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                (username, password, '0', 300, 1, 0,"potion","lapiseira","sopa"))
            
            cursor.execute(
                """INSERT INTO tb_character (username, color, head, top, bottom)
                VALUES (%s, %s, %s, %s, %s)""", 
                (username, color, 'default', 'default', 'default'))
            
            conn.commit()
            conn.close()
            return jsonify(user), 201
        
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
            "xp": item[6],
            "item1": item[7],
            "item2": item[8],
            "item3": item[9]
        }
        users.append(user)

    # Return as JSON
    return jsonify(users)

# /api/userbynick/<string:username>
@app.route('/api/userbynick/<string:username>', methods=['GET'])
def get_userbynick(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tb_user WHERE username=%s", (username,))
    item = cursor.fetchone()


    # Check if the user exists
    if item:
        user = {
            "id": item[0],
            "username": item[1],
            "password": item[2],
            "icon": item[3],
            "coins": item[4],
            "level": item[5],
            "xp": item[6],
            "item1": item[7],
            "item2": item[8],
            "item3": item[9],
            "character": {
                "color": "",
                "head": "",
                "top": "",
                "bottom": ""
            }
        }
        cursor.execute("SELECT color,head,top,bottom FROM tb_character WHERE username=%s", (username,))
        item =  cursor.fetchone();
        
        
        user["character"]["color"] = item[0];
        user["character"]["head"] = item[1];
        user["character"]["top"] = item[2];
        user["character"]["bottom"] = item[3];
    
        
        print(user)
        
        conn.close()
        # Return the user as JSON
        return jsonify(user)
    else:
        # If the user doesn't exist, return an appropriate error message
        return jsonify({"error": "User not found"})

# INFO PERSONAGEM
# Character Methods
@app.route('/api/get_color', methods=['POST'])
def get_color():
    conn = connect_db()
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username']
    query = """SELECT color
               FROM tb_character
               WHERE username = %s
            """
    try:
        cursor.execute(query, (username,))
        color = cursor.fetchone()
        if color:
            color_value = color[0]
            return jsonify({"message": str(color_value)}), 200
        else:
            return jsonify({"message": "color not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Item Methods
@app.route('/api/get_storedeals', methods=['GET'])
def get_items():
    data = request.get_json()
    query = f"""SELECT s.item_id, i.name, i.description, i.icon, i.type, s.group, s.discount, s.cost
                FROM tb_store s
                INNER JOIN tb_item i
                ON s.item_id = i.id
            """
    try:
        cursor.execute(query)
        items_get = cursor.fetchall()
        
        items = []

        for item in items_get:
            send = {
                "item_id": item[0],
                "name": item[1],
                "description": item[2],
                "icon": item[3],
                "type": item[4],
                "group": item[5],
                "discount": item[6],
                "cost": item[7]
            }
            items.append(send)
            
        # Return as JSON
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


#


@app.route('/api/get_item', methods=['POST'])
def get_item():
    data = request.get_json()
    name = data['item_name']
    query = f"""SELECT name
                FROM tb_item
                WHERE name = '{name}'
            """
    try:
        cursor.execute(query)
        item = cursor.fetchone()
        if item:
            item_name = item[0]
            return jsonify({"message": str(item_name)}), 200
        else:
            return jsonify({"message":"item not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/set_color', methods=['POST'])
def set_color():
    conn = connect_db()
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username']
    color = data['color']
    query= """UPDATE tb_character 
              SET color = %s
              WHERE username = %s
            """
    try:
        cursor.execute(query, (color, username))
        conn.commit()
        return jsonify({"message": "color updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500





if __name__ == '__main__':
    app.run(debug=True)