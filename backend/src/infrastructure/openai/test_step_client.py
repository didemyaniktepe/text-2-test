from typing import List
from src.infrastructure.config.settings import OpenAISettings
from src.infrastructure.openai.base_openai_client import BaseOpenAIClient
from src.services.vision_analysis_service import VisionAnalysisService
from src.prompts import TestStepPrompt
import logging

logger = logging.getLogger(__name__)

class TestStepClient(BaseOpenAIClient):
    def __init__(self, settings: OpenAISettings):
        super().__init__(settings)
        logger.info("TestStepClient initialized using %s model", self.model)
    
    def generate_test_step(self,vision_analysis: str,dom_data: str,remaining_scenario: str,completed_steps: List[str],scenario: str) -> str:
        test_step_prompt = TestStepPrompt.create(vision_analysis=vision_analysis, remaining_scenario=remaining_scenario,dom_data=dom_data,completed_steps=completed_steps,scenario=scenario)
        messages = [
            {"role": "system", "content": "You are a test automation expert. Plan the next step to complete the scenario."},
            {"role": "user", "content": test_step_prompt}
        ]
        response = self._make_chat_completion(
            messages=messages,
            target_model=self.model,
            temperature=0.7
        )
        return response
