import os
import requests
import json
from pydantic import BaseModel
from datetime import datetime



dirpath = os.path.dirname(__file__)

CHAT_SAVE_PATH = "static/chats"
TEMPLATE_PATH = "static/templates"

dirpath += "/"
os.makedirs(dirpath + CHAT_SAVE_PATH, exist_ok=True)
os.makedirs(dirpath + TEMPLATE_PATH, exist_ok=True)

# DeepSeek API configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = "sk-731921a5623e4c99a19176290b05f9a2"


class ChatRequest(BaseModel):
    message: str
    path: str


class CharacterInfo(BaseModel):
    name: str
    relationship: str
    favorite_color: str


def replace_template(new_content: str) -> bool:
    try:
        filepath = os.path.join(TEMPLATE_PATH, "character_info_template.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error replacing template: {e}")
        return False


def check_file_exists(category: str, filename: str) -> bool:
    """
    Checks if the specified file exists in the directory.

    Args:
        category (str): The category where the file belong.
        filename (str): The filename of the file to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    if category == 'templates':
        file_path = os.path.join(TEMPLATE_PATH, filename)
    elif category == 'chats':
        file_path = os.path.join(CHAT_SAVE_PATH, filename)
    return os.path.exists(dirpath + file_path)


def fill_template(character_info: CharacterInfo) -> str:
    # Read template
    filename = 'character_info_template.txt'
    filepath = os.path.join(TEMPLATE_PATH, filename)
    with open(dirpath + filepath, "r", encoding="utf-8") as f:
        template_content = f.read()

    # Replace placeholders
    filled_content = template_content.replace("*NAME_PLACEHOLDER*", character_info.name)
    filled_content = filled_content.replace("*RELATIONSHIP_PLACEHOLDER*", character_info.relationship)
    filled_content = filled_content.replace("*LOCATION_PLACEHOLDER*", character_info.favorite_color)

    return filled_content


def initiate_query_deepseek(character_info: CharacterInfo) -> str:
    filled_text = fill_template(character_info)

    dict_data = {
    "messages": [
        {
        "content": filled_text,
        "role": "system"
        },
        {
        "content": "请开始对话。",
        "role": "user"
        }
    ],
    "model": "deepseek-chat",
    "frequency_penalty": 0,
    "max_tokens": 2048,
    "presence_penalty": 0,
    "response_format": {
        "type": "text"
    },
    "stop": None,
    "stream": False,
    "stream_options": None,
    "temperature": 1,
    "top_p": 1,
    "tools": None,
    "tool_choice": "none",
    "logprobs": False,
    "top_logprobs": None
    }

    payload = json.dumps(dict_data)

    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
    }

    response = requests.request("POST", DEEPSEEK_API_URL, headers=headers, data=payload)
    dict_data['messages'].append(response.json()['choices'][0]['message'])

    # filename = f"{character_info.name}.json"
    filename = "character.json"
    filepath = os.path.join(CHAT_SAVE_PATH, filename)

    with open(dirpath + filepath, 'w') as f:
        json.dump(dict_data, f)

    # response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content'], filepath
    else:
        return f"Error from DeepSeek: {response.text}"


def query_deepseek(message: str, history_filepath: str) -> str:
    with open(dirpath + history_filepath) as f:
        dict_data = json.load(f)

    dict_data['messages'].append(
        {
            "content": message,
            "role": "user" 
        }
    )

    payload = json.dumps(dict_data)

    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
    }

    response = requests.request("POST", DEEPSEEK_API_URL, headers=headers, data=payload)

    dict_data['messages'].append(response.json()['choices'][0]['message'])

    with open(dirpath + history_filepath, 'w') as f:
        json.dump(dict_data, f)

    # response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content']
    else:
        return f"Error from DeepSeek: {response.text}"