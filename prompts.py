from datetime import datetime


def get_tools(database_schema_string: str, database_definitions: str) -> list[dict]:
    tools = [
        {
            "name": "ask_database",
            "description": "Use this function to answer user questions about Production data. Input should be a fully formed MySQL query.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f'''Generate a PostgreSQL query to extract information based on a user's question. \
                        
# Parameters: \
# - Database Schema: {database_schema_string} \
# - Data Definitions: {database_definitions} \
# - Current Date: Use today's date as {datetime.now()} where needed in the query. \

# Instructions: \
# 1. Construct an SQL query using only the tables and columns listed in the provided schema. \
# 2. When comparing string use LIKE to maximise the search. \
# 2. Ensure the query avoids assumptions about non-existent columns. \
# 3. Consider performance and security best practices, such as avoiding SQL injection risks. \
# 4. Format the query in plain text for direct execution in a PostgreSQL database. \

# Example Query: \
# If the user asks for the number of employees in each department, the query should look like this: \
# "SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;"'''
                    }
                },
                "required": ["query"],
            }
        }
    ]
    return tools


def get_failed_sql_query_system_prompt(query: str, formatted_chat_history: list[dict]) -> str:
    failed_sql_query_system_prompt = f'''Consider yourself as a helpful data analyst of Netcom Learning, use the chat history and query to reply. \

# Parameters:
# - Query: {query}
# - Chat history: {formatted_chat_history}. \

# Instructions: \
# 1. Don't generate information, say you don't have answer to this question. \
# 2. Never use your own knowledge in the answer. \
# 3. Never mention other online sources of learning.'''
    return failed_sql_query_system_prompt


def get_successed_sql_query_system_prompt(sql_response: str) -> list[dict[str, str]]:
    successed_sql_query_messages = [
        {
            "role": "user",
            "content": f"""Explain PostgreSQL data in natural language, \
            
# Parameters: \
# - SQL data: {sql_response}

# Instructions: \
# 1. Keep the response short and concise and never mention id of the PostgreSQL database. \
# 2. If needed consider today's date as {datetime.now().strftime("%b %d, %Y")}. \
# 3. If there is a course URL in the SQL data then use "https://www.netcomlearning.com/" to provide it in the answer otherwise don't mention the URL in the awnser. \
# 4. Never mention that you are reading information from a SQL Database."""
        }
    ]
    return successed_sql_query_messages


def get_system_prompt() -> str:
    system_prompt = "You are a data analyst of Netcom Learning. You help user get information about the database."
    return system_prompt
