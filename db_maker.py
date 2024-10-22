"""
Script to make a database from a csv file

"""


import pandas as pd
import sqlite3

class DatabaseMaker:
    
    def __init__(self, db_name):
        self.db_name = db_name
        
        
    def csv_to_sqlite(self, csv_file, table_name):
        """
        Reads a CSV file and converts it into a SQLite database table.
        
        Args:
            csv_file (str): The path to the CSV file.
            table_name (str): The name of the table to create in the SQLite database.
            
        Returns:
            None
        """
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file)
        
        # Connect to the SQLite database (it will create the database file if it doesn't exist)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Infer the schema based on the DataFrame columns and data types
        self.create_table_from_df(df, table_name, cursor)
        
        # Insert CSV data into the SQLite table
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # Commit and close the connection
        conn.commit()
        conn.close()
        print(f"Data loaded into '{table_name}' table in '{self.db_name}' SQLite database.")

    def create_table_from_df(self, df, table_name, cursor):
        """
        Creates a table in the SQLite database based on the DataFrame schema.
        
        Args:
            df (pandas.DataFrame): The DataFrame containing the data to be loaded into the table.
            table_name (str): The name of the table to create in the SQLite database.
            cursor (sqlite3.Cursor): The cursor object used to execute SQL commands.
        """
        # Get column names and types
        col_types = []
        for col in df.columns:
            dtype = df[col].dtype
            if dtype == 'int64':
                col_type = 'INTEGER'
            elif dtype == 'float64':
                col_type = 'REAL'
            else:
                col_type = 'TEXT'
            col_types.append(f'"{col}" {col_type}')
        
        # Create the table schema
        col_definitions = ", ".join(col_types)
        create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({col_definitions});'
        # print(create_table_query)
        
        # Execute the table creation query
        cursor.execute(create_table_query)
        print(f"Table '{table_name}' created with schema: {col_definitions}")

    def run_sql_query(self, query):
        """
        Executes a SQL query on a SQLite database and returns the results.

        Args:
            query (str): The SQL query to run.

        Returns:
            list: Query result as a list of tuples, or an empty list if no results or error occurred.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            conn.commit()  # Ensure changes are saved for write operations
            conn.close()
            return results if results else []
        except sqlite3.Error as e:
            # Print the error message and re-raise the exception
            print(f"An error occurred while executing the query: {e}")
            raise  # Re-raise the exception to be handled by the caller

# Example usage
db_maker = DatabaseMaker("data1.db")
db_maker.csv_to_sqlite("data/data1.csv", "health")

