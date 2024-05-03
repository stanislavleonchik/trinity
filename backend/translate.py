import json
import os
import requests
import dotenv
dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY")
folder_id = os.getenv("FOLDER_ID")
source_language_code = 'en'
target_language = 'ru'
speller = 'true'


def translate_collocations(texts):
    body = {
        "sourceLanguageCode": source_language_code,
        "targetLanguageCode": target_language,
        "texts": texts,
        "folderId": folder_id,
        "speller": speller,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key {0}".format(API_KEY)
    }

    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                             json=body,
                             headers=headers
                             )

    response_dict = response.json()

    if response.status_code == 200:
        return [coloc['text'] for coloc in response_dict.get('translations', [])]
    else:
        print(response.text)
        return []


def load_dictionary():
    try:
        with open("translations.json", 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_dictionary(dictionary):
    with open("translations.json", 'w', encoding='utf-8') as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)


def calculate_bounds(words, limit=5000):
    lengths = [len(word) for word in words]
    bounds, current_sum, last_index = [], 0, 0

    for i, length in enumerate(lengths):
        if current_sum + length + (1 if current_sum else 0) > limit:
            bounds.append((last_index, i))
            last_index = i
            current_sum = length
        else:
            current_sum += length + (1 if current_sum else 0)

    if last_index < len(words):
        bounds.append((last_index, len(words)))

    return bounds
