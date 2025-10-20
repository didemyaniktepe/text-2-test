from dataclasses import dataclass
import json
from typing import Optional

from src.utils.json_utils import extract_json_from_markdown_block

@dataclass
class NextStep:
    description: str
    scenario_complete: bool
    remaining_scenario: str


def parse_json_from_response(response: str) -> NextStep:
    json_str = extract_json_from_markdown_block(response)
    data = json.loads(json_str)
    return NextStep(
        description=data.get("description", ""),
        scenario_complete=data.get("scenario_complete", False),
        remaining_scenario=data.get("remaining_scenario", "")
    )
