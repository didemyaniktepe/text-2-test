import json
import re

def extract_json_from_markdown_block(text: str) -> str:
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text  


def parse_response(response: str) -> tuple[str, str, str]:
    selector = ""
    action_type = ""
    locator = ""
    
    lines = response.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("SELECTOR:"):
            selector = line.replace("SELECTOR:", "").strip()
        elif line.startswith("ACTION_TYPE:"):
            action_type = line.replace("ACTION_TYPE:", "").strip()
        elif line.startswith("LOCATOR:"):
            locator = line.replace("LOCATOR:", "").strip()
            
    return selector, action_type, locator
