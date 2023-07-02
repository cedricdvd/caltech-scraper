import os
import mysql.connector

from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')

def connect_database():
    try:
        database = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE_NAME
        )
        
        cursor = database.cursor(buffered=True)

    except mysql.connector.Error as error:
        error_code = error.errno
        error_message = error.msg
        print(f'Error {error_code}: {error_message}')
        return None, None
    
    return database, cursor
