import warnings
warnings.filterwarnings("ignore")
import psycopg2
from constants import *
from util import getConfig
import pandas as pd
from datetime import datetime
from custom_logger import *

def connect():
    config = getConfig(db_conn_file)
    #print(f"config-{config['db']['postgres']}")
   
    conn = psycopg2.connect(**config['db']['postgres'])
    cursor = conn.cursor()   
    #print(f"config-2")

    return conn, cursor

def create_test_results_detail_table():
    conn, cursor = connect()
    try:
        # SQL query to create the table with foreign key constraint
        create_table_query = """
        CREATE TABLE IF NOT EXISTS test_results_detail (
            test_results_detail_no SERIAL PRIMARY KEY,
            test_run_no INTEGER REFERENCES test_results(test_run_no),
            original_response TEXT,
            actual_response TEXT,
            ideal_response TEXT,
            difference TEXT,
            original_run_no INTEGER,
            original_prompt TEXT,
            execution_time DOUBLE PRECISION
        );
        """
        
        # Execute the create table query
        cursor.execute(create_table_query)
        
        # Commit the transaction
        conn.commit()
        print("Test results detail table created successfully")

    except Exception as e:
        print(f"Error creating table: {e}")
    
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_test_results_table():
    conn, cursor = connect()
    try:
        # SQL query to create the table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS test_results (
            test_run_no SERIAL PRIMARY KEY,
            test_run_date DATE DEFAULT CURRENT_DATE,
            total_tests INTEGER,
            tests_passed INTEGER,
            tests_failed INTEGER,
            tests_pass_rate TEXT,
            model TEXT,
            average_execution_time DOUBLE PRECISION
        );
        """
        
        # Execute the create table query
        cursor.execute(create_table_query)
        
        # Commit the transaction
        conn.commit()
        print("Test results table created successfully")

    except Exception as e:
        print(f"Error creating table: {e}")
    
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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
                datetime.now(),  # Current date for run_date
                data['use_for_training'],
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


def get_test_data(test_size_limit):
    if(test_size_limit == None):
        return read(TEST_QUERY)
    else:
        return read("".join([TEST_QUERY, f"LIMIT {test_size_limit}"]))



def insert_test_results_data(model:str,total_tests: int, tests_passed: int, tests_failed: int, pass_rate: str, average_execution_time: float):
    conn, cursor = connect()
    try:
        insert_query = """
        INSERT INTO test_results (total_tests, tests_passed, tests_failed, tests_pass_rate, average_execution_time)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING test_run_no;
        """
        
        cursor.execute(insert_query, (total_tests, tests_passed, tests_failed, pass_rate, average_execution_time))
        test_run_no = cursor.fetchone()[0]
    
        conn.commit()
        print(f"Test results inserted successfully with run number: {test_run_no}")
        return test_run_no

    except Exception as e:
        print(f"Error inserting test results: {e}")
        return None
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_test_results_detail_data(model:str,test_run_no: int,original_response: str,actual_response: str,ideal_response: str,difference: str,original_run_no: int,original_prompt: str, execution_time: float):
    #logger.critical(f"insert_test_results_detail_data - {model},{test_run_no},{original_response},{actual_response},{ideal_response},{difference},{original_run_no},{original_prompt}")
    conn, cursor = connect()
    try: 
        insert_query = """
        INSERT INTO test_results_detail (test_run_no, original_response, actual_response, ideal_response, difference,original_run_no,original_prompt, execution_time)
        VALUES (%s, %s, %s, %s, %s,%s,%s,%s)
        """

        cursor.execute(insert_query, (test_run_no, original_response, actual_response, ideal_response, difference,original_run_no,original_prompt, execution_time))
        conn.commit()
        print(f"Test results detail inserted successfully with run number: {test_run_no}")

    except Exception as e:
        print(f"Error inserting test results detail: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def save_test_results(test_map,model,total_tests,passed_tests,failed_tests,pass_rate,average_execution_time):
    print(f"average_execution_time-{average_execution_time}")
    test_run_no = insert_test_results_data(model,total_tests,passed_tests,failed_tests,pass_rate,average_execution_time)
    for test in test_map.values():
        print(f"test['execution_time']-{test['execution_time']}")
        insert_test_results_detail_data(model,test_run_no,test['original_response'],test['actual_response'],test['ideal_response'],test['idealResponse_changes'],test['original_run_no'],test['original_prompt'], test['execution_time'])
    
