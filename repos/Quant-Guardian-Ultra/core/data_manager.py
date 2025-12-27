import json
import os
import csv

class DataManager:
    @staticmethod
    def load_json(path, default=None):
        if default is None:
            default = {}
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            return default
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default

    @staticmethod
    def save_json(path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def save_history(path, data_list):
        if not data_list:
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        file_exists = os.path.exists(path)

        with open(path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['symbol', 'price', 'pred'])

            for item in data_list:
                writer.writerow([
                    item.get('symbol'),
                    item.get('price'),
                    item.get('pred')
                ])
