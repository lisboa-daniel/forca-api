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
                    "accessory": "",
                    "top": "",
                    "bottom": ""
                }
            }
            cursor.execute("SELECT color,accessory,top,bottom FROM tb_character WHERE username=%s", (username,))
            item =  cursor.fetchone();
        
        
            user["character"]["color"] = item[0];
            user["character"]["accessory"] = item[1];
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
                    "accessory": "",
                    "top": "",
                    "bottom": ""
                    }
                }
            
            cursor.execute(
                """INSERT INTO tb_user (username, password, icon, coins, level, xp, item1,item2,item3)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                (username, password, '0', 300, 1, 0,"potion","lapiseira","sopa"))
            
            cursor.execute(
                """INSERT INTO tb_character (username, color, accessory, top, bottom)
                VALUES (%s, %s, %s, %s, %s)""", 
                (username, color, 'default', 'default', 'default'))
            

            
            user_id_select_query = f"""SELECT id
                           FROM tb_user 
                           WHERE username = '{username}' 
                        """

            item_names = ["Poção de cura +1", "Lapiseira", "Sopinha de letras"]
            try:
                cursor.execute(user_id_select_query)
                user_id = str(cursor.fetchone()).strip("(),")

                for item_name in item_names:
                    item_id_select_query = f"""SELECT id
                                            FROM tb_item 
                                            WHERE name = '{item_name}' 
                                            """

                    cursor.execute(item_id_select_query)
                    item_id = str(cursor.fetchone()).strip("(),")
                    insert_query = f""" INSERT INTO tb_inventory (user_id,
                                                        item_id,
                                                        amount
                                                        )
                                        VALUES ('{user_id}', '{item_id}', 5)
                                    """

                    cursor.execute(insert_query)
            
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            
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
                "accessory": "",
                "top": "",
                "bottom": ""
            }
        }
        cursor.execute("SELECT color,accessory,top,bottom FROM tb_character WHERE username=%s", (username,))
        item =  cursor.fetchone();
        
        
        user["character"]["color"] = item[0];
        user["character"]["accessory"] = item[1];
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
    
    conn = connect_db()
    cursor = conn.cursor()
    
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
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404


#

# INFO FROM ITEM
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
#INVENTARIO


@app.route('/api/coin_update', methods=['POST'])
def coin_increment():
    data = request.get_json()
    username = data['username']
    amount = data['amount']
    query = f"""UPDATE tb_user 
                SET coins = {amount}
                WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "Coins updated to"+ str(amount)})       
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/create_inventory', methods=['POST'])
def inventory_create():
    data = request.get_json()
    username = data['username']
    item_name = data['item_name']
    user_id_select_query = f"""SELECT id
                               FROM tb_user 
                               WHERE username = '{username}' 
                            """
    item_id_select_query = f"""SELECT id
                               FROM tb_item 
                               WHERE name = '{item_name}' 
                            """
   
            
    try:
        cursor.execute(user_id_select_query)
        user_id = str(cursor.fetchone()).strip("(),")
        cursor.execute(item_id_select_query)
        item_id = str(cursor.fetchone()).strip("(),")
        
        insert_query = f""" INSERT INTO tb_inventory (user_id,
                                                item_id,
                                                amount
                                                )
                        VALUES ('{user_id}', '{item_id}', 1)
                    """
        
        cursor.execute(insert_query)
        conn.commit()
        conn.close()

        return jsonify({"message":"Inventory created"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/add_item', methods=['POST'])
def add_item_inventory():
    conn = connect_db()
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username']
    item = data['item_name']
    query= f""" WITH "temp" AS (
                    SELECT tinv.id AS inventory_item_id,
                        ti.name AS name,
                        ti.id AS item_id,
                        tu.id AS user_id,
                        tinv.amount AS item_amount,
                        ti.description,
                        ti.icon,
                        ti.type,
                        tu.username
                    FROM tb_item AS ti
                    JOIN tb_inventory AS tinv ON ti.id = tinv.item_id
                    JOIN tb_user AS tu ON tu.id = tinv.user_id
                    WHERE name = '{item}'
                    AND username = '{username}'
                )
                UPDATE tb_inventory
                SET amount = amount + '{1}'
                FROM temp
                WHERE tb_inventory.user_id = temp.user_id
                AND tb_inventory.item_id = temp.item_id; """
    
    try:
        cursor.execute(query)
        conn.commit()
        conn.close()
        return jsonify({"message": "Item adicionado"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#COMPRA
@app.route('/api/buy', methods=['POST'])
def buy():
    conn = connect_db()
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username']
    item = data['item_name']
    coins = data['coins']
    
    query_coins = f"""UPDATE tb_user 
                SET coins = {coins}
                WHERE username = '{username}'
            """
    query= f""" WITH "temp" AS (
                    SELECT tinv.id AS inventory_item_id,
                        ti.name AS name,
                        ti.id AS item_id,
                        tu.id AS user_id,
                        tinv.amount AS item_amount,
                        ti.description,
                        ti.icon,
                        ti.type,
                        tu.username
                    FROM tb_item AS ti
                    JOIN tb_inventory AS tinv ON ti.id = tinv.item_id
                    JOIN tb_user AS tu ON tu.id = tinv.user_id
                    WHERE name = '{item}'
                    AND username = '{username}'
                )
                UPDATE tb_inventory
                SET amount = amount + '{1}'
                FROM temp
                WHERE tb_inventory.user_id = temp.user_id
                AND tb_inventory.item_id = temp.item_id; """
    
    try:
        cursor.execute(query)
       
        
        cursor.execute(query_coins)
        conn.commit()
        
        
        conn.close()
        return jsonify({"message": "Item comprado"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# INFO FROM ITEM ON INVENTORY
@app.route('/api/get_item_inventory/<username>/<item_name>', methods=['GET'])
def get_item_from_inventory(username, item_name):
    conn = connect_db()
    cursor = conn.cursor()
    
    query = f"""WITH temp AS (
                    SELECT tinv.id AS inventory_item_id, 
                           ti.name AS item_name,
                           ti.description,
                           ti.icon,
                           ti.type,
                           tinv.amount,
                           tu.username
                    FROM tb_item AS ti
                    JOIN tb_inventory AS tinv ON ti.id = tinv.item_id
                    JOIN tb_user AS tu ON tu.id = tinv.user_id
                    WHERE ti.icon = '{item_name}' 
                    AND tu.username = '{username}'
                )
                SELECT *
                FROM temp
             """
    try:
        cursor.execute(query)
        item_array = cursor.fetchone() 
        
        response = {
            "inventory_item_id": item_array[0],
            "item_name": item_array[1],
            "description": item_array[2],
            "icon": item_array[3],
            "type": item_array[4],
            "amount": item_array[5],
            "username": item_array[6]
        }
        
        cursor.close()  
        return jsonify(response), 200
          
    except Exception as e:
        cursor.close()
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)