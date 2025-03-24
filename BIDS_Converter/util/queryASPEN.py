import mysql.connector
import pandas as pd

# Database connection function
def connect_to_database():
    """
    Establish a connection to the database.
    """
    return mysql.connector.connect(
        host='ribsbot.umcutrecht.nl',
        user='testxelo2',
        password='testxelo2',
        database='testxelo2'
    )

def queryASPEN(query):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    connection.close()
    return pd.DataFrame(results, columns=columns)
