import re
from typing import List

from .base_openai_client import BaseOpenAIClient
from src.infrastructure.config.settings import OpenAISettings
from src.prompts import ElementSelectorPrompt
from src.utils.json_utils import parse_response
from src.utils.prompt_logger import log_prompt_to_file
import logging

logger = logging.getLogger(__name__)

class ElementSelectorClient(BaseOpenAIClient):

    def __init__(self, settings: OpenAISettings):
        super().__init__(settings)
        logger.info("ElementSelectorClient initialized using %s model", self.model)

    def find_element(
        self, description: str, dom_data: str, vision_analysis: str
    ) -> tuple[str, str, str]:
        prompt_text = ElementSelectorPrompt.create(
            description, dom_data, vision_analysis
        )
        messages = [
            {"role": "system", "content": "Find the best selector for the element. "},
            {"role": "user", "content": [{"type": "text", "text": prompt_text}]},
        ]
        full_response = self._make_chat_completion(
            messages=messages, target_model=self.model, temperature=0.1, max_tokens=1000
        )
        selector, action_type, locator = parse_response(full_response)
        
        log_prompt_to_file(
            description=description,
            prompt=prompt_text,
            response=full_response,
            prompt_type="element_selector"
        )

        return selector, action_type, locator

    def find_element_for_failed_attempts(
        self, description: str, failed_attempts: List[dict]
    ) -> tuple[str, str, str]:
        prompt_text = ElementSelectorPrompt.create_for_failed_attempts(
            failed_attempts, description
        )
        messages = [
            {"role": "system", "content": "Find the best selector for the element. "},
            {"role": "user", "content": [{"type": "text", "text": prompt_text}]},
        ]
        full_response = self._make_chat_completion(
            messages=messages, target_model=self.model, temperature=0.1, max_tokens=1000
        )
        logger.error(f"Full response: {full_response}") 
        selector, action_type, locator = parse_response(full_response)
        logger.error(f"Selector: {selector}")
        logger.error(f"Action type: {action_type}")
        logger.error(f"Locator: {locator}")
        log_prompt_to_file(
            description=description,
            prompt=prompt_text,
            response=full_response,
            prompt_type="element_selector_retry"
        )
        
        return selector, action_type, locator
