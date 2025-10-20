
from typing import List
from src.domain.test.entities.next_step import parse_json_from_response, NextStep
from src.infrastructure.openai.test_step_client import TestStepClient
import logging

logger = logging.getLogger(__name__)


class TestStepPlanner:
    def __init__(self, test_step_client: TestStepClient):
        self.test_step_client = test_step_client

    def plan(self,vision_analysis: str,remaining_scenario: str,dom_data: str,completed_steps: List[str],scenario: str) -> NextStep:
        response = self.test_step_client.generate_test_step(
            vision_analysis, dom_data, remaining_scenario, completed_steps, scenario
        )
        return parse_json_from_response(response)