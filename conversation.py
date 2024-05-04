import anthropic
from datetime import datetime

from claude_api import chat_completion
from database_functions import *
from prompts import *

tools = get_tools(get_database_schema_string(),
                  get_database_definitions())


def format_chat_history(chat_history: list[tuple[str, str]], query: str) -> list[tuple[str, str]]:
    formatted_chat_history = []
    for ch in chat_history:
        formatted_chat_history.append({
            'role': 'user',
            'content': ch[0]
        })
        formatted_chat_history.append({
            'role': 'assistant',
            'content': ch[1]
        })
    formatted_chat_history.append({
        "role": "user",
        "content": query
    })
    return formatted_chat_history


def handle_chat_completion(chat_history: list[list]) -> list[list]:
    query = chat_history[-1][0]
    print(f'User query -> {query}')
    formatted_chat_history = format_chat_history(chat_history[:-1], query)
    response = chat_completion(
        messages=formatted_chat_history,
        max_tokens=512,
        system=get_system_prompt(),
        tools=tools
    )
    flag = False
    for content in response.content:
        if type(content) == anthropic.types.beta.tools.tool_use_block.ToolUseBlock:
            flag = True
    if flag:
        for content in response.content:
            if type(content) == anthropic.types.beta.tools.tool_use_block.ToolUseBlock:
                tool_call = content
                break
        function_name = tool_call.name
        function_args = tool_call.input
        if function_name == 'ask_database':
            sql_query = function_args['query']
            print(f'SQL Query -> {sql_query}')
            sql_response = run_execute_database_query(sql_query)
            print(f'SQL Response -> {sql_response}')
            if len(sql_response) == 0:
                formatted_chat_history = [{
                    "role": "user",
                    "content": get_failed_sql_query_system_prompt(query, formatted_chat_history)
                }]
                second_response = chat_completion(
                    messages=formatted_chat_history,
                    max_tokens=512,
                    system=get_system_prompt()
                )
                chat_history[-1][1] = second_response.content[0].text
                print(f'Response -> {second_response.content[0].text}')
                return chat_history
            else:
                formatted_chat_history = get_successed_sql_query_system_prompt(
                    sql_response)
                second_response = chat_completion(
                    messages=formatted_chat_history,
                    max_tokens=1024,
                    system=get_system_prompt()
                )
                chat_history[-1][1] = second_response.content[0].text
                print(f'Response -> {second_response.content[0].text}')
                return chat_history
    else:
        chat_history[-1][1] = response.content[0].text
        print(f'Response -> {response.content[0].text}')
        return chat_history


def handle_user_query(message: str, chat_history: list[tuple]) -> tuple:
    chat_history += [[message, None]]
    return '', chat_history
