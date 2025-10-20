import logging
from typing import Any, Dict, List

from src.prompts import TestCodePrompt
from .base_openai_client import BaseOpenAIClient
from src.infrastructure.config.settings import OpenAISettings

logger = logging.getLogger(__name__)

class TestCodeGeneratorClient(BaseOpenAIClient):
    
    def __init__(self, settings: OpenAISettings):
        super().__init__(settings)
        logger.info("TestCodeGeneratorClient initialized using %s model", self.model)
    
    def generate_test_code(self, test_steps: List[Dict[str, Any]], scenario: str, url: str) -> str:
        prompt = TestCodePrompt.create(test_steps, scenario, url)
        print(f"DEBUG: Prompt: {prompt}")
        messages = [
            {"role": "system", "content": "You are a test automation expert. Return ONLY the test code without any explanation, comments or markdown formatting."},
            {"role": "user", "content": prompt}
        ]
        response = self._make_chat_completion(
            messages=messages,
            target_model=self.model,
            temperature=0.7
        )
        print(f"DEBUG: Response: {response}")
        logger.info("Successfully generated test code")
        return response
