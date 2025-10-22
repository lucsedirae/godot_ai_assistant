# src/data_loader.py
import json


class DataLoader:
    def __init__(self, filepath):
        """Initialize and load JSON data from file."""
        self.filepath = filepath
        self.data = self._load_json()

    def _load_json(self):
        """Load and return JSON data from file."""
        try:
            with open(self.filepath, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: File '{self.filepath}' not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in '{self.filepath}'.")
            return {}

    def get(self, key, default=None):
        """Get value by key, with optional default."""
        return self.data.get(key, default)

    def get_all(self):
        """Return all data."""
        return self.data
