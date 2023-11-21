from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2 import sql
import json
import base64

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
                "icon": "0",
                "coins": 300,
                "level": 1,
                "xp": 0,
                "item1": "potion",
                "item2": "lapiseira",
                "item3": "sopa",
                "character": {
                    "color": "azul",
                    "accessory": "default_acessory",
                    "top": "default_top",
                    "bottom": "default_bottom"
                    }
                }
            
            cursor.execute(
                """INSERT INTO tb_user (username, password, icon, coins, level, xp, item1,item2,item3)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                (username, password, '0', 300, 1, 0,"potion","lapiseira","sopa"))
            
            cursor.execute(
                """INSERT INTO tb_character (username, color, accessory, top, bottom)
                VALUES (%s, %s, %s, %s, %s)""", 
                (username, color, 'default_accessory', 'default_top', 'default_bottom'))
            

            
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



#set de itens equipados
@app.route('/api/set_items', methods=['POST'])
def set_items():
    conn = connect_db()
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username']
    item1 = data['item1']
    item2 = data['item2']
    item3 = data['item3']

    query= f"""UPDATE tb_user 
                SET item1 = '{item1}', 
                    item2 = '{item2}',
                    item3 = '{item3}'
                WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "items updated"}), 200
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

@app.route('/api/getusercoin/<string:username>', methods=['GET'])
def get_coins(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT coins FROM tb_user WHERE username=%s", (username,))
    item = cursor.fetchone()


    # Check if the user exists
    if item:
        coins = {
            "coins": item[0]
        }
        cursor.execute("SELECT color,accessory,top,bottom FROM tb_character WHERE username=%s", (username,))
        item =  cursor.fetchone();
        
        conn.close()
        # Return the user as JSON
        return jsonify(coins)
    else:
        # If the user doesn't exist, return an appropriate error message
        return jsonify({"error": "User not found"})

    

@app.route('/api/insertimage', methods=['POST'])
def insert_image():
    try:
        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Get the file from the request
        file = request.files['file']
        
        # Read the bytes from the file
        image_bytes = file.read()

        # Get the file name
        image_name = file.filename

        # Insert the data into the database
        cursor.execute(sql.SQL("INSERT INTO tb_image (image_bytes, image_name) VALUES (%s, %s)"), (psycopg2.Binary(image_bytes), image_name))
        
        # Commit the transaction
        conn.commit()

        # Close the database connection
        conn.close()

        return jsonify({"success": "Image inserted successfully"})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"})

    

@app.route('/api/getimages', methods=['GET'])
def get_images():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tb_image")
    items = cursor.fetchall()
    images = []   
    if items:
        for item in items:
        
            
            image = {
                "id": item[0],
                "image_bytes": base64.b64encode(item[1]).decode('utf-8'),
                "image_name": item[2]
            }
            images.append(image);
       
        conn.close()
        # Return the user as JSON
        return jsonify(images)
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
 
@app.route('/api/set_icon', methods=['POST'])
def set_avatar():
    conn = connect_db()
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username']
    icon = data['icon']
    query= """UPDATE tb_user
              SET icon = %s
              WHERE username = %s
            """
    try:
        cursor.execute(query, (icon, username))
        conn.commit()
        return jsonify({"message": "avatar updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500   
    
@app.route('/api/update_character', methods=['POST'])
def update_character():
    conn = connect_db()
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username']
    color = data['color']
    top = data['top']
    bottom = data['bottom']
    accessory = data['accessory']

    query= """UPDATE tb_character 
            SET color = %s,
                top = %s,
                bottom = %s,
                accessory = %s
            WHERE username = %s
            """
    try:
        cursor.execute(query, (color, top, bottom, accessory, username))

        conn.commit()
        return jsonify({"message": "character updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
       
  
#INVENTARIO
@app.route('/api/get_costume_inventory/<username>', methods=['GET'])
def get_costume_inventory(username):
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
                    WHERE ti.type IN (11, 12, 13) 
                    AND tu.username = '{username}'
                )
                SELECT inventory_item_id, item_name, description, icon, type, amount, username
                FROM temp;
             """
    try:
        cursor.execute(query)
        item_arrays = cursor.fetchall()

        response = []
        for item_array in item_arrays:
            item = {
                "inventory_item_id": item_array[0],
                "item_name": item_array[1],
                "description": item_array[2],
                "icon": item_array[3],
                "type": item_array[4],
                "amount": item_array[5],
                "username": item_array[6]
            }
            response.append(item)

        cursor.close()  
        return jsonify(response), 200
          
    except Exception as e:
        cursor.close()
        return jsonify({"error": str(e)}), 500


@app.route('/api/coin_add', methods=['POST'])
def coin_increment():
    conn = connect_db()
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username'].lower()  # Convert the provided username to lowercase
    amount = data['amount']
    query = f"""UPDATE tb_user 
                SET coins = coins + {amount}
                WHERE LOWER(username) = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "Coins added: " + str(amount)})       
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create_inventory', methods=['POST'])
def inventory_create():
    conn = connect_db()
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username']
    item_name = data['item_name']
    coins = data['coins']
    
    user_id_select_query = f"""SELECT id
                               FROM tb_user 
                               WHERE username = '{username}' 
                            """
    item_id_select_query = f"""SELECT id
                               FROM tb_item 
                               WHERE name = '{item_name}' 
                            """
    
    query_coins = f"""UPDATE tb_user 
                      SET coins = {coins}
                      WHERE username = '{username}'"""
    
    try:
        # Get user and item IDs
        cursor.execute(user_id_select_query)
        user_id = str(cursor.fetchone()).strip("(),")
        cursor.execute(item_id_select_query)
        item_id = str(cursor.fetchone()).strip("(),")
        
        # Check if the item already exists in the user's inventory
        check_inventory_query = f"""SELECT id
                                    FROM tb_inventory 
                                    WHERE user_id = '{user_id}' 
                                      AND item_id = '{item_id}' 
                                 """
        cursor.execute(check_inventory_query)
        existing_inventory_id = cursor.fetchone()

        # If the item already exists, delete it
        if existing_inventory_id:
            delete_existing_query = f"""DELETE FROM tb_inventory
                                        WHERE id = {existing_inventory_id[0]}
                                     """
            cursor.execute(delete_existing_query)
        
        # Insert the new item into the inventory
        insert_query = f""" INSERT INTO tb_inventory (user_id,
                                                      item_id,
                                                      amount
                                                    )
                            VALUES ('{user_id}', '{item_id}', 1)
                        """
        cursor.execute(insert_query)
        # Update the user's coins
        cursor.execute(query_coins)
        
        # Commit the changes to the database
        conn.commit()

        return jsonify({"message": "Inventory created"}), 201
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


@app.route('/api/useitem', methods=['POST'])
def useitem():
    conn = connect_db()
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username']
    item = data['item_name']
    
    query_use_item = f"""UPDATE tb_inventory
                        SET amount = amount - 1
                        WHERE user_id = (SELECT id FROM tb_user WHERE username = '{username}')
                        AND item_id = (SELECT id FROM tb_item WHERE icon = '{item}')
                        AND amount > 0;
                    """

    try:
        cursor.execute(query_use_item)
        conn.commit()
        conn.close()
        return jsonify({"message": "Item used"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#PEGA INVENTARIO
@app.route('/api/get_items_inventory_by_type/<username>/<item_type>', methods=['GET'])
def get_items_by_type_from_inventory(username, item_type):
    conn = connect_db()
    cursor = conn.cursor()

    item_type_prefix = item_type[0]

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
                    WHERE tu.username = '{username}' 
                    AND ti.type::text LIKE '{item_type_prefix}%'
                )
                SELECT *
                FROM temp
             """
    try:
        cursor.execute(query)
        item_array = cursor.fetchall()
        cursor.close()
        if item_array:
            response = []
            for item in item_array:
                item_data = {
                    "inventory_item_id": item[0],
                    "item_name": item[1],
                    "description": item[2],
                    "icon": item[3],
                    "type": item[4],
                    "amount": item[5],
                    "username": item[6]
                }
                response.append(item_data)
            return jsonify(response), 200
        else:
            return jsonify({"message": "No user found or the user does not have any items of this type"}), 404
    except Exception as e:
        cursor.close()
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
        cursor.close()  
        if (item_array != None):
            response = {
            "inventory_item_id": item_array[0],
            "item_name": item_array[1],
            "description": item_array[2],
            "icon": item_array[3],
            "type": item_array[4],
            "amount": item_array[5],
            "username": item_array[6]
            
            }
            return jsonify(response), 200
        else:
            return jsonify({"message" : "Não usuário não encontrado ou não possui o item"}), 404
       
          
    except Exception as e:
        cursor.close()
        return jsonify({"error": str(e)}), 500



# WORDS
@app.route('/api/get_categories', methods=['GET'])
def get_categories():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tb_word_category")
        items = cursor.fetchall()
        conn.close()

        # Convert to objects
        categories = []
        for item in items:
            category = {
                "id": item[0],
                "category": item[1]
            }
            categories.append(category)

        # Return as JSON
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"})


@app.route('/api/get_words', methods=['GET'])
def get_words():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tb_word_data")
        items = cursor.fetchall()
        conn.close()

        # Convert to objects
        word_data = []
        for item in items:
            data = {
                "id": item[0],
                "category_id": item[1],
                "word": item[2]
            }
            word_data.append(data)

        # Return as JSON
        return jsonify(word_data)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"})




# item effects

@app.route('/api/get_effects', methods=['GET'])
def get_effects():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tb_item_effect")
        items = cursor.fetchall()
        conn.close()

        # Convert to objects
        effects = []
        for item in items:
            effect = {
                "id": item[0],
                "id_item": item[1],
                "effect_amount": item[2],
                "type": item[3]
            }
            effects.append(effect)

        # Return as JSON
        return jsonify(effects)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"})


@app.route('/api/get_consumable_item', methods=['GET'])
def get_consumable_item():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Perform the JOIN operation
        cursor.execute("""
            SELECT
                tb_item.id,
                tb_item.name,
                tb_item.description,
                tb_item.icon,
                tb_item_effect.type_class,
                tb_item_effect.type_effect,
                tb_item_effect.effect_amount,
                tb_item_effect.target
                
                
            FROM
                tb_item
            JOIN
                tb_item_effect ON tb_item.id = tb_item_effect.item_id
        """)

        items = cursor.fetchall()
        conn.close()

        # Convert to objects
        results = []
        for item in items:
            result = {
                "item_id": item[0],
                "item_name": item[1],
                "description": item[2],
                "icon": item[3],
                "type_class": item[4],
                "type_effect": item[5],
                "effect_amount": item[6],
                "target": item[7]
                
            }
            results.append(result)

        # Return as JSON
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"})



@app.route('/api/words_by_category/<category_name>', methods=['GET'])
def get_words_by_category(category_name):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Find category_id based on category_name
        cursor.execute("SELECT id FROM tb_word_category WHERE category = %s", (category_name,))
        category_id = cursor.fetchone()

        if category_id:
            # Retrieve words for the specified category
            cursor.execute("SELECT * FROM tb_word_data WHERE category_id = %s", (category_id[0],))
            items = cursor.fetchall()
            conn.close()

            # Convert to objects
            word_data = []
            for item in items:
                data = {
                    "id": item[0],
                    "category_id": item[1],
                    "word": item[2]
                }
                word_data.append(data)

            # Return as JSON
            return jsonify(word_data)
        else:
            return jsonify({"error": f"Category not found: {category_name}"})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"})


@app.route('/api/get_word_data', methods=['GET'])
def get_word_data():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Get all categories
        cursor.execute("SELECT id, category FROM tb_word_category")
        categories = cursor.fetchall()

        # Initialize the result array
        result = []

        # Iterate through categories
        for category in categories:
            # Retrieve words for the current category
            cursor.execute("SELECT word FROM tb_word_data WHERE category_id = %s", (category[0],))
            words = [item[0] for item in cursor.fetchall()]

            # Create the result object
            result_object = {
                "category_name": category[1],
                "word_data": words
            }

            # Append the result object to the result array
            result.append(result_object)

        conn.close()

        # Return as JSON
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"})
    
@app.route('/novecentos', methods=['GET'])
def pagina_compra2():
    return render_template('novecentos.html')    
    
# PAGINAS DO SITE
@app.route('/compra/<username>/<package>', methods=['GET'])
def pagina_compra(username, package):
    data = {
        'username': username,
        'package': package
    }
    return render_template('detalhe_compra.html', data=data, package_nice_name=package)




if __name__ == '__main__':
    app.run(debug=True)