import logging
from typing import List

from src.infrastructure.openai.element_selector_client import ElementSelectorClient
from src.utils.element_utils import clean_selector_response

logger = logging.getLogger(__name__)

class ElementSelector:
    def __init__(self, client: ElementSelectorClient):
        self.ai = client
    
    def find_selector(self, description: str, dom_data: str, vision_analysis: str, failed_attempts: List[dict]) -> tuple[str, str, str]:
        if failed_attempts:
            element_info = self.ai.find_element_for_failed_attempts(description, failed_attempts)
        else:
            element_info = self.ai.find_element(description, dom_data, vision_analysis)
        logger.info(f"Selector: {element_info[0]}")
        selector = clean_selector_response(element_info[0])
        logger.info(f"Cleaned selector: {selector}")
        logger.info(f"Locator: {element_info[2]}")
        return element_info[0], element_info[1], element_info[2]