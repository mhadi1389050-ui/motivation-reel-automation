import json
from datetime import datetime

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def save_output(data, output_path):
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Output saved: {output_path}")

def get_timestamp():
    return datetime.utcnow().isoformat() + "Z"
