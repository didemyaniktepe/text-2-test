from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..value_objects.test_status import TestStatus


@dataclass
class TestCase:
    id: str
    url: str
    scenario: str
    generated_script: str
    created_at: datetime
    status: TestStatus