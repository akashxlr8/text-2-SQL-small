import os
import requests
import sqlite3
import numpy as np
import sqlparse
# import faiss
from groq import Groq
from litellm import completion
from db_maker import DatabaseMaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define constants for database and table names
DB_NAME = "healthcare.db"
TABLE_NAME = "healthcare"
CSV_FILE_PATH = "data/healthcare_dataset.csv"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JINA_API_KEY = os.getenv("JINA_API_KEY")
client = Groq(api_key=GROQ_API_KEY)  # Initialize the Groq client

# Initialize the FAISS index
dimension = 768  # Ensure this matches the dimension size for Groq embeddings
index = faiss.IndexFlatL2(dimension)  # L2 distance index

def get_embeddings(text):
    """
    Converts a text string into a vector embedding using Jina embeddings API.
    
    Args:
        text (str): The text string to convert.
    
    Returns:
        np.array: A vector representation of the text.
    """
    url = 'https://api.jina.ai/v1/embeddings'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JINA_API_KEY}'
    }
    data = {
        "model": "jina-embeddings-v2-base-en",
        "normalized": True,
        "embedding_type": "float",
        "input": [text]
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    # Extract the embedding from the response
    embedding = np.array(response_data['data'][0]['embedding'])
    return embedding

def get_table_schema(db_name, table_name):
    """
    Retrieves the schema (columns and data types) for a given table in the SQLite database.
    
    Args:
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table.
    
    Returns:
        list: A list of tuples with column name, data type, and other info.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Use PRAGMA to get the table schema
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()

    conn.close()
    return schema

def format_table_schema(table_schema):
    """
    Formats the table schema into a string suitable for inclusion in a prompt.
    """
    formatted_schema = []
    for col in table_schema:
        column_name = col[1]
        column_type = col[2]
        formatted_schema.append(f'"{column_name}" {column_type}')
    
    return ", ".join(formatted_schema)

def generate_llm_prompt(table_name, table_schema):
    """
    Generates a prompt with few-shot examples to provide context about a table's schema for LLM to convert natural language to SQL.
    Args:
        table_name (str): The name of the table.
        table_schema (list): A list of tuples where each tuple contains information about the columns in the table.
    
    Returns:
        str: The generated prompt to be used by the LLM.
    """
    formatted_schema = format_table_schema(table_schema)
    
    examples = """
    Example 1:
    Question: How many different types of medical conditions are there?
    SQL Query: SELECT DISTINCT "Medical Condition" FROM health;

    Example 2:
    Question: How many people are under the age of 45?
    SQL Query: SELECT COUNT(*) FROM health WHERE "Age" < 45;

    Example 3:
    Question: How many hospitals are there?
    SQL Query: SELECT COUNT(DISTINCT "Hospital") AS Total_Hospitals FROM health;
    """
    
    prompt = f"""You are an expert in writing SQL queries for relational databases. 
    You will be provided with a database schema, a few examples, and a natural 
    language question. Your task is to generate an accurate SQL query based on the user's question.

    The database has a table named '{table_name}' with the following schema:
    {formatted_schema}

    {examples}

    Please generate a SQL query based on the following natural language question. ONLY return the SQL query.
    """
    
    return prompt

def generate_sql_query(question):
    table_schema = get_table_schema(DB_NAME, TABLE_NAME)
    llm_prompt = generate_llm_prompt(TABLE_NAME, table_schema)
    
    user_prompt = """Question: {question}"""
    response = completion(
        api_key=GROQ_API_KEY,
        model="groq/llama3-8b-8192",
        messages=[
            {"content": llm_prompt.format(table_name=TABLE_NAME),"role": "system"}, 
            {"content": user_prompt.format(question=question),"role": "user"}],
        max_tokens=1000    
    )
    answer = response.choices[0].message.content

    query = answer.replace("```sql", "").replace("```", "")
    query = query.strip()
    print(query)
    return query

def execute_sql_query(query, user_question, attempt=1, max_attempts=30):
    """
    Executes the SQL query and handles errors by correcting the query if necessary.
    
    Args:
        query (str): The SQL query to execute.
        user_question (str): The original user question.
        Optional: attempt (int): The current attempt number (default is 1).
        Optional: max_attempts (int): The maximum number of attempts to correct the query (default is 3).
    
    Returns:
        list: The result of the SQL query as a list of tuples.
    """
    try:
        # Attempt to run the SQL query
        response = db_maker.run_sql_query(query)
        logging.info("Success in execute_sql_query")
        return response
    except sqlite3.Error as e:
        logging.error(f"Error in execute_sql_query (Attempt {attempt})")
        # Capture the error message
        error_message = str(e)
        logging.error(f"SQL Error: {error_message}")
        if attempt >= max_attempts:
            logging.error("Maximum correction attempts reached.")
            return []
        # Attempt to correct the query
        corrected_query = correct_sql_query(query, error_message, user_question)
        if corrected_query and is_valid_sql(corrected_query):
            logging.info(f"Retrying with corrected query: {corrected_query}")
            return execute_sql_query(corrected_query, user_question, attempt + 1, max_attempts)
        else:
            logging.error("Correction failed or corrected query is invalid.")
            return []

def correct_sql_query(query, error_message, user_question):
    """
    Analyzes the error message and attempts to correct the SQL query using the original user question.
    
    Args:
        query (str): The original SQL query.
        error_message (str): The error message from the failed query execution.
        user_question (str): The original user question.
    
    Returns:
        str: A corrected SQL query, or None if no correction is possible.
    """
    table_schema = get_table_schema(DB_NAME, TABLE_NAME)
    formatted_schema = format_table_schema(table_schema)
    
    prompt = f"""You are a Senior SQL Developer assisting a Junior Developer. 
    You are provided with the database schema, a natural language question, an incorrectly generated SQL query, and an error message. 
    Your task is to correct the SQL query based on the error message and the user's question.

    Database Schema:
    <schema>
    {formatted_schema}
    </schema>

    User Question:
    <question>
    {user_question}
    </question>

    Original SQL Query:
    <query>
    {query}
    </query>

    Error Message:
    <error>
    {error_message}
    </error>

    ONLY return the corrected SQL query. Do not include any additional text or explanations.
    """
    
    response = completion(
        api_key=GROQ_API_KEY,
        model="groq/llama3-8b-8192",
        messages=[
            {"content": prompt, "role": "system"}
        ],
        max_tokens=1500
    )
    
    corrected_query = response.choices[0].message.content.strip()
    logging.info(f"Corrected SQL Query: {corrected_query}")
    return corrected_query

def handle_user_question(user_question):
    """
    Handles the user's question by generating a SQL query and attempting to execute it.
    
    Args:
        user_question (str): The user's natural language question.
    
    Returns:
        list: The response to the user's question.
    """
    # Convert the user's question to an embedding
    # question_embedding = get_embeddings(user_question)
    
    # Generate the initial SQL query
    sql_query = generate_sql_query(user_question)
    
    # Execute the SQL query and handle errors
    response = execute_sql_query(sql_query, user_question)
    
    return response

def is_valid_sql(query):
    """
    Validates the SQL query syntax using sqlparse.
    """
    try:
        sqlparse.parse(query)
        return True
    except Exception as e:
        logging.error(f"SQL validation error: {e}")
        return False

if __name__ == "__main__":
    logging.info("Hello, World!")
    
    db_maker = DatabaseMaker(DB_NAME)
    db_maker.csv_to_sqlite(CSV_FILE_PATH, TABLE_NAME)
    
    while True:
        user_prompt = input("Enter your prompt: ")
        if user_prompt == "exit":
            break
        else:
            logging.info(f"User Prompt: {user_prompt}")
            answer = handle_user_question(user_prompt)
            print(answer)
    logging.info("Exiting...")

    # get_table_schema(DB_NAME, TABLE_NAME)




