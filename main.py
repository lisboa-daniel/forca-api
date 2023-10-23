from flask import Flask, request, jsonify
import sqlite3


app = Flask(__name__)

conn = sqlite3.connect('bd.db', check_same_thread=False)
cursor = conn.cursor()

# User Methods
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        query = f"""SELECT * 
                    FROM tb_user 
                    WHERE username='{username}' 
                    AND password='{password}'
                """
        cursor.execute(query)
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
        select_query = f""" SELECT * 
                            FROM tb_user 
                            WHERE username='{username}'
                        """
        set_query = f"""INSERT INTO tb_user (username,
                                             password, 
                                             icon, 
                                             coins, 
                                             level, 
                                             xp
                                            )
                        VALUES ('{username}',
                                '{password}',
                                '0',0,0,0)
                    """
        cursor.execute(select_query)
        user = cursor.fetchone()

        if user:
            return jsonify({"message": "User already exists"}), 200
        else:
            cursor.execute(set_query)
            conn.commit()
            return jsonify({"message": "User Successfully Registered"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/set_icon', methods=['POST'])
def set_icon():
    data = request.get_json()
    username = data['username']
    icon = data['icon']
    query = f"""UPDATE tb_user 
                SET icon = '{icon}'
                WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "Icon Updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_icon', methods=['POST'])
def get_icon():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT icon 
                FROM tb_user 
                WHERE username='{username}'
            """
    try:
        cursor.execute(query)
        icon = cursor.fetchone()
        if icon:
            icon_binary = icon[0]
            return (send_file(
                    io.BytesIO(icon_binary),
                    mimetype='image/png',
                    as_attachment=True,
                    download_name=f'icon.png')
                    )
        else:
            return jsonify({"message":"icon not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coin_increment', methods=['POST'])
def coin_increment():
    data = request.get_json()
    username = data['username']
    amount = data['amount']
    query = f"""UPDATE tb_user 
                SET coins = coins + {amount}
                WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "amount added"})       
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coin_decrement', methods=['POST'])
def coin_decrement():
    data = request.get_json()
    username = data['username']
    amount = data['amount']
    select_query = f"""SELECT coins 
                       FROM tb_user 
                       WHERE username='{username}'
                    """
    reset_query = f"""UPDATE tb_user 
                        SET coins = 0
                        WHERE username = '{username}' 
                   """
    subtract_query = f"""UPDATE tb_user 
                         SET coins = coins - {amount}
                         WHERE username = '{username}' 
                      """
        
    try:
        cursor.execute(select_query)
        coin_amount = cursor.fetchone()
        coin_amount = coin_amount[0]

        if coin_amount <= 0:
            cursor.execute(reset_query)
            conn.commit()
            return jsonify({"message": "don't have enough coins"})       

        elif coin_amount == amount:
            cursor.execute(reset_query)
            conn.commit()
            return jsonify({"message": f"{amount} subtracted"})       

        elif coin_amount > amount:
            cursor.execute(subtract_query)
            conn.commit()
            return jsonify({"message": f"{amount} subtracted"})       
        
        else:
            return jsonify({"message": "don't have enough coins"})       

        return jsonify({"message": "amount subtracted"})       
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_coins', methods=['POST'])
def get_coins():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT coins 
                FROM tb_user 
                WHERE username='{username}'
             """
    try:
        cursor.execute(query)
        coins = cursor.fetchone()
        if coins:
            coin_amount = coins[0]
            return jsonify({"message":str(coin_amount)}), 200
        else:
            return jsonify({"message":"coin amount not found" }), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/exp_increment', methods=['POST'])
def exp_increment():
    data = request.get_json()
    username = data['username']
    amount = data['amount']
    update_query = f"""UPDATE tb_user 
                       SET xp = xp + {amount}
                       WHERE username = '{username}'
                    """
    select_query = f""" SELECT xp
                        FROM tb_user 
                        WHERE username='{username}'
                    """
    reset_exp_query = f"""  UPDATE tb_user 
                            SET xp = 0
                            WHERE username = '{username}'
                       """
    level_up_query = f""" UPDATE tb_user 
                        SET level = level + 1
                        WHERE username = '{username}'
                      """

    try:
        cursor.execute(update_query)
        conn.commit()
        cursor.execute(select_query)

        exp_amount = cursor.fetchone()
        exp_amount = exp_amount[0]

        if exp_amount < 1000:
            return jsonify({"message": "exp amount added"})       
        
        else:
            cursor.execute(reset_exp_query)
            conn.commit()          
            cursor.execute(level_up_query)
            conn.commit()

            return jsonify({"message": "level up"})       

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_exp', methods=['POST'])
def get_exp():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT xp 
                FROM tb_user 
                WHERE username='{username}'
            """
    try:
        cursor.execute(query)
        exp = cursor.fetchone()
        if exp:
            exp_amount = exp[0]
            return jsonify({"message":str(exp_amount)}), 200
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
            return jsonify({"message":str(level_value)}), 200
        else:
            return jsonify({"message":"level not found" }), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_item1', methods=['POST'])
def get_item1():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT item1
                FROM tb_user
                WHERE username = '{username}
            """
    try:
        cursor.execute(query)
        item1 = cursor.fetchone()
        if item1:
            item1_value = item1[0]
            return jsonify({"message": str(item1_value)}), 200
        else:
            return jsonify({"message":"item1 not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/set_item1', methods=['POST'])
def set_item1():
    data = request.get_json()
    username = data['username']
    item = data['item']
    query= f"""UPDATE tb_user 
               SET item1 = '{item}'
               WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "item updated"}), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_item2', methods=['POST'])
def get_item2():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT item2
                FROM tb_user
                WHERE username = '{username}
            """
    try:
        cursor.execute(query)
        item2 = cursor.fetchone()
        if item2:
            item2_value = item2[0]
            return jsonify({"message": str(item2_value)}), 200
        else:
            return jsonify({"message":"item1 not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/set_item2', methods=['POST'])
def set_item2():
    data = request.get_json()
    username = data['username']
    item = data['item']
    query= f"""UPDATE tb_user 
                SET item2 = '{item}'
                WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "item updated"}), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_item3', methods=['POST'])
def get_item3():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT item3
                FROM tb_user
                WHERE username = '{username}
            """
    try:
        cursor.execute(query)
        item3 = cursor.fetchone()
        if item3:
            item3_value = item1[0]
            return jsonify({"message": str(item3_value)}), 200
        else:
            return jsonify({"message":"item3 not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/set_item3', methods=['POST'])
def set_item3():
    data = request.get_json()
    username = data['username']
    item = data['item']
    query= f"""UPDATE tb_user 
               SET item3 = '{item}'
               WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "item updated"}), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 500

# Character Methods
@app.route('/api/get_color', methods=['POST'])
def get_color():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT color
                FROM tb_character
                WHERE username = '{username}
            """
    try:
        cursor.execute(query)
        color = cursor.fetchone()
        if color:
            color_value = item1[0]
            return jsonify({"message": str(color_value)}), 200
        else:
            return jsonify({"message":"color not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/set_color', methods=['POST'])
def set_color():
    data = request.get_json()
    username = data['username']
    color = data['color']
    query= f"""UPDATE tb_user 
               SET color = '{color}'
               WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "color updated"}), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_head', methods=['POST'])
def get_head():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT head
                FROM tb_character
                WHERE username = '{username}
            """
    try:
        cursor.execute(query)
        head = cursor.fetchone()
        if head:
            head_value = item1[0]
            return jsonify({"message": str(head_value)}), 200
        else:
            return jsonify({"message":"head not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/set_head', methods=['POST'])
def set_head():
    data = request.get_json()
    username = data['username']
    head = data['head']
    query= f"""UPDATE tb_user 
               SET head = '{head}'
               WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "head updated"}), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_top', methods=['POST'])
def get_top():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT top
                FROM tb_character
                WHERE username = '{username}
            """
    try:
        cursor.execute(query)
        top = cursor.fetchone()
        if top:
            top_value = item1[0]
            return jsonify({"message": str(top_value)}), 200
        else:
            return jsonify({"message":"top not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/set_top', methods=['POST'])
def set_top():
    data = request.get_json()
    username = data['username']
    top = data['top']
    query= f"""UPDATE tb_user 
               SET top = '{top}'
               WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "top updated"}), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_bottom', methods=['POST'])
def get_bottom():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT bottom
                FROM tb_character
                WHERE username = '{username}
            """
    try:
        cursor.execute(query)
        bottom = cursor.fetchone()
        if bottom:
            bottom_value = item1[0]
            return jsonify({"message": str(bottom_value)}), 200
        else:
            return jsonify({"message":"bottom not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/set_bottom', methods=['POST'])
def set_bottom():
    data = request.get_json()
    username = data['username']
    bottom = data['bottom']
    query= f"""UPDATE tb_user 
               SET bottom = '{bottom}'
               WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "bottom updated"}), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_hands', methods=['POST'])
def get_hands():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT hands
                FROM tb_character
                WHERE username = '{username}
            """
    try:
        cursor.execute(query)
        hands = cursor.fetchone()
        if hands:
            hands_value = item1[0]
            return jsonify({"message": str(hands_value)}), 200
        else:
            return jsonify({"message":"hands not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/set_hands', methods=['POST'])
def set_hands():
    data = request.get_json()
    username = data['username']
    hands = data['hands']
    query= f"""UPDATE tb_user 
               SET hands = '{hands}'
               WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "hands updated"}), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_shoes', methods=['POST'])
def get_shoes():
    data = request.get_json()
    username = data['username']
    query = f"""SELECT shoes
                FROM tb_character
                WHERE username = '{username}
            """
    try:
        cursor.execute(query)
        shoes = cursor.fetchone()
        if shoes:
            shoes_value = item1[0]
            return jsonify({"message": str(shoes_value)}), 200
        else:
            return jsonify({"message":"shoes not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/set_shoes', methods=['POST'])
def set_shoes():
    data = request.get_json()
    username = data['username']
    shoes = data['shoes']
    query= f"""UPDATE tb_user 
               SET shoes = '{shoes}'
               WHERE username = '{username}'
            """
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "shoes updated"}), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 500

# Item Methods
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

# Store Methods
@app.route('/api/get_item_store', methods=['POST'])
def get_item_from_store():
    data = request.get_json()
    item_name = data['item_name']
    query = f"""WITH 'temp' AS (SELECT ts.id, ti.name,
                                       ti.description, ti.icon,
                                       ti.type, ts.cost, ts.discount
                                FROM tb_item AS ti
                                JOIN tb_store AS ts
                                ON ti.id = ts.item_id
                                WHERE ti.name='{item_name}'
                               )
                SELECT * 
                FROM temp
            """    
    try:
        cursor.execute(query)
        item = cursor.fetchone()
        if item:
            item_name = item[1]
            return jsonify({"message": str(item_name)}), 200
        else:
            return jsonify({"message":"item not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

# Inventory Methods
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
    insert_query = f""" INSERT INTO tb_inventory (user_id,
                                                item_id,
                                                amount
                                                )
                        VALUES ('{user_id}', '{item_id}', 0)
                    """
            
    try:
        cursor.execute(user_id_select_query)
        user_id = cursor.fetchone()
        cursor.execute(item_id_select_query)
        item_id = cursor.fetchone()
        cursor.execute(insert_query)
        conn.commit()

        return jsonify({"message":"Inventory created"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/get_item_inventory', methods=['POST'])
def get_item_from_inventory():
    data = request.get_json()
    username = data['username']
    item = data['item']
    query = f"""WITH 'temp' AS (SELECT tinv.id AS inventory_item_id , 
                                      ti.name AS item_name,
                                      ti.description, ti.icon,
                                      ti.type, tinv.amount, tu.username
                                FROM tb_item AS ti
                                JOIN tb_inventory AS tinv
                                ON ti.id = tinv.item_id
                                JOIN tb_user AS tu
                                ON tu.id = tinv.user_id
                                WHERE item_name = '{item}' 
                                AND username = '{username}'
                                )
                SELECT *
                FROM temp
             """
    try:
        cursor.execute(query)
        item_array = cursor.fetchone()  
        return jsonify({"message": str(item_array)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/add_item_inventory', methods=['POST'])
def add_item_inventory():
    data = request.get_json()
    username = data['username']
    item = data['item']
    amount = data['amount']
    query= f""" WITH 'temp' AS (SELECT  tinv.id AS
                                        inventory_item_id,
                                        ti.name AS item_name,
                                        ti.id AS item_id,
                                        tu.id AS user_id,
                                        tinv.amount AS item_amount,
                                        ti.description, ti.icon,
                                        ti.type, tu.username
                                FROM tb_item AS ti
                                JOIN tb_inventory AS tinv
                                ON ti.id = tinv.item_id
                                JOIN tb_user AS tu
                                ON tu.id = tinv.user_id
                                WHERE item_name = '{item}'
                                AND username = '{username}'
                              )
                UPDATE tb_inventory
                SET amount = amount + {amount}' 
                FROM temp
                WHERE tb_inventory.user_id = temp.user_id 
                AND tb_inventory.item_id = temp.item_id """
    
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": str(item_array)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/subt_item_inventory', methods=['POST'])
def subt_item_inventory():
    data = request.get_json()
    username = data['username']
    item = data['item']
    amount = data['amount']
    update_query= f""" WITH 'temp' AS (SELECT  tinv.id AS
                                        inventory_item_id,
                                        ti.name AS item_name,
                                        ti.id AS item_id,
                                        tu.id AS user_id,
                                        tinv.amount AS item_amount,
                                        ti.description, ti.icon,
                                        ti.type, tu.username
                                FROM tb_item AS ti
                                JOIN tb_inventory AS tinv
                                ON ti.id = tinv.item_id
                                JOIN tb_user AS tu
                                ON tu.id = tinv.user_id
                                WHERE item_name = '{item}'
                                AND username = '{username}'
                                )
                UPDATE tb_inventory
                SET amount = amount - {amount}' 
                FROM temp
                WHERE tb_inventory.user_id = temp.user_id 
                AND tb_inventory.item_id = temp.item_id 
            """
    reset_amount_query= f""" WITH 'temp' AS (SELECT  tinv.id AS
                                            inventory_item_id,
                                            ti.name AS item_name,
                                            ti.id AS item_id,
                                            tu.id AS user_id,
                                            tinv.amount AS item_amount,
                                            ti.description, ti.icon,
                                            ti.type, tu.username
                                    FROM tb_item AS ti
                                    JOIN tb_inventory AS tinv
                                    ON ti.id = tinv.item_id
                                    JOIN tb_user AS tu
                                    ON tu.id = tinv.user_id
                                    WHERE item_name = '{item}'
                                    AND username = '{username}'
                                    )
                    UPDATE tb_inventory
                    SET amount = 0' 
                    FROM temp
                    WHERE tb_inventory.user_id = temp.user_id 
                    AND tb_inventory.item_id = temp.item_id 
                """
    select_query = f""" 
                    WITH 'temp' AS (SELECT tinv.id AS inventory_item_id, 
                                            ti.name AS item_name,
                                            ti.description, ti.icon,
                                            ti.type, tinv.amount, tu.username
                                    FROM tb_item AS ti
                                    JOIN tb_inventory AS tinv
                                    ON ti.id = tinv.item_id 
                                    JOIN tb_user AS tu
                                    ON tu.id = tinv.user_id
                                    WHERE item_name = '{item}' 
                                    AND username = '{username}'
                                    )
                    SELECT *
                    FROM temp
                    """

    try:
        cursor.execute(update_query)
        conn.commit()
        cursor.execute(select_query)
        item_array = cursor.fetchone()
        item_amount = item_array[-2]
        
        if item_amount <= 0:
            cursor.execute(reset_amount_query)
            conn.commit()
            return jsonify({"message": "You don't have any of this item"}), 400
        else:
            cursor.execute(reset_amount_query)
            conn.commit()
            return jsonify({"message": "Item spent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
