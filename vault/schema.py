import json
from pathlib import Path

# 定義 Vault 資料結構
class VaultSchema:
    def __init__(self, schema_path):
        self.schema_path = schema_path
        self.schema = {}

        if Path(schema_path).exists():
            with open(schema_path, 'r') as f:
                self.schema = json.load(f)

    def save(self):
        with open(self.schema_path, 'w') as f:
            json.dump(self.schema, f, indent=4)

    def update_schema(self, data: dict):
        self.schema.update(data)
        self.save()

    def get_schema(self):
        return self.schema
