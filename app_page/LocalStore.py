import os
import json

class LocalStore:
    def __init__(self, path='app.json') -> None:
        self.json_path = path

    def _load_json(self):
        if not os.path.exists(self.json_path):
            return {}
        try:
            with open(self.json_path, 'r', encoding="utf-8") as json_file:
                return json.load(json_file)
        except json.JSONDecodeError:
            return {}

    def _save_json(self, data):
        try:
            dir_path = os.path.dirname(self.json_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(self.json_path, 'w', encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except IOError as e:
            print(f"Error saving data: {e}")
            return False

    # 获取全部数据
    def getAll(self):
        return self._load_json()

    # 获取单个数据
    def get(self, key=None):
        data = self._load_json()
        if key is None:
            return data
        return data.get(key, None)

    # 删除数据
    def delete(self, key):
        data = self._load_json()
        if key in data:
            data.pop(key)
            return self._save_json(data)
        else:
            print(f"No data found for key: {key}")
            return False

    # 保存数据
    def save(self, key, value=None):
        data = self._load_json()
        
        if isinstance(key, str):
            data[key] = value
        elif isinstance(key, dict):
            data.update(key)
        elif isinstance(key, list):
            data = key
        
        return self._save_json(data)