import warnings
warnings.filterwarnings("ignore")
import psycopg2
from constants import *
from util import getConfig
import pandas as pd
from datetime import datetime

def connect():
    config = getConfig(db_conn_file)
    #print(f"config-{config['db']['postgres']}")
   
    conn = psycopg2.connect(**config['db']['postgres'])
    cursor = conn.cursor()   
    #print(f"config-2")

    return conn, cursor

def insert(data_list):    
    conn, cursor = connect()
    try:                
        # SQL query to insert data into the table
        insert_query = INSERT_QUERY
        
    
     
        # Prepare the values to be inserted
        values_list = [
            (
                data['usecase'],               
                data['functionality'],
                data['llm'],
                data['llm_parameters'],
                data['isBaseline'],
                data['run_no'],
                data['system_prompt'],
                data['user_prompt'],
                data['response'],
                data['ideal_response'],
                data['execution_time'],
                data['matches_baseline'],
                data['matches_ideal'],
                data['difference'],
                data['ideal_response_difference'],
                data['mode'],
                data['similarity_metric'],
                datetime.now()  # Current date for run_date
            )
            for data in data_list
        ]
     
        # Execute the insert query
        cursor.executemany(insert_query, values_list)        
        # Commit the transaction
        conn.commit()
        
        print("Data inserted successfully")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def read(q):    
    conn, cursor = connect()
    
    try:
        # Query the data from the table        
        df = pd.read_sql_query(q, conn)
        
        return df
    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def readWithGroupFilter(run_id):
    return read("".join([READ_QUERY, f"where run_no='{run_id}'"]))

