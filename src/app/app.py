from flask import Flask, request
from mysql.connector import connect, Error
import time

connection = None

def init_db():
    global connection
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f'Connection to db (attempt {attempt + 1}/{max_retries}):', end='')
            connection = connect(host='db', user='root', password='123')
            print(' OK')

            print('Create db:', end='')
            create_db_query = "CREATE DATABASE IF NOT EXISTS vars"
            with connection.cursor() as cursor:
                cursor.execute(create_db_query)
            print(' OK')

            print('Change db:', end='')
            use_db_query = "USE vars"
            with connection.cursor() as cursor:
                cursor.execute(use_db_query)
            print(' OK')

            print('Create table:', end='')
            create_table_query = """
            CREATE TABLE IF NOT EXISTS vars(
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                value VARCHAR(100),
                UNIQUE (name)
            )
            """
            with connection.cursor() as cursor:
                cursor.execute(create_table_query)
                connection.commit()
            print(' OK')
            return True
            
        except Error as e:
            print(f' Failure: {e}')
            if attempt < max_retries - 1:
                print(f'Retrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
            else:
                print('Failed to connect to MySQL after all retries')
                raise
    
    return False


app = Flask(__name__)

@app.route('/var/<var_name>', methods=['GET'])
def get(var_name):
    if connection is None:
        return 'Database not connected', 500
    
    select_query = f"""
    SELECT value FROM vars
    WHERE name = '{var_name}'
    """
    
    print("Select query:", select_query)
    with connection.cursor() as cursor:
        cursor.execute(select_query)
        result = cursor.fetchall()
        if result:
            return result[0][0]
        return 'Variable not found', 404


@app.route('/var/<var_name>', methods=['POST'])
def set(var_name):
    if connection is None:
        return 'Database not connected', 500
    
    value = request.form.get("value")
    insert_query = f"""
    INSERT INTO vars (name, value)
    VALUES ('{var_name}', '{value}')
    ON DUPLICATE KEY UPDATE value='{value}'
    """
    
    print("Insert query:", insert_query)
    with connection.cursor() as cursor:
        cursor.execute(insert_query)
        connection.commit()
    
    return 'OK'


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)
