import json

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        print("Помилка: файл config.json не знайдено")
        return None
    except json.JSONDecodeError:
        print("Помилка: файл config.json містить некоректний JSON")
        return None
