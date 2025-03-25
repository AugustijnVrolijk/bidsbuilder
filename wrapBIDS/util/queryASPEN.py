import mysql.connector
import pandas as pd
import json

from pathlib import Path
# Database connection function


def connect_to_database():
    """
    Establish a connection to the database.
    """
    path = Path(r"C:\Users\augus\BCI_Stuff\Aspen\database details.txt")

    with open(path,'r') as f:
        jsonString = f.read()
        vals = json.loads(jsonString)
        if not isinstance(vals, dict):
            raise ValueError(f"File {path} is a json containing {vals}, not a dict which was expected")

    return mysql.connector.connect(
        host=vals['host'],
        user=vals['user'],
        password=vals['password'],
        database=vals['database']
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

def main():
    pass

if __name__ == "__main__":
    main()