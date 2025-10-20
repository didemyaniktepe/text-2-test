import json
from datetime import datetime
from pathlib import Path

def log_prompt_to_file(description: str, prompt: str, response: str = None, prompt_type: str = "element_selector"):
    log_dir = Path("backend/logs/prompts")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prompt_type}_{timestamp}.json"
    
    log_data = {
        "timestamp": timestamp,
        "description": description,
        "prompt": prompt,
        "response": response
    }
    
    with open(log_dir / filename, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)