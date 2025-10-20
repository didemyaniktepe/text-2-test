from src.infrastructure.openai.vision_analysis_client import VisionAnalysisClient
from src.prompts.vision_analysis_prompt import VisionAnalysisPrompt
from typing import List
import logging
import os

logger = logging.getLogger(__name__)

class VisionAnalysisService:
    def __init__(self, vision_client: VisionAnalysisClient):
        self.vision_client = vision_client
    
    def analyze_screenshot(self, screenshot_path: str, remaining_scenario: str, scenario: str, completed_steps: List[str]) -> str:
        if not screenshot_path or not os.path.exists(screenshot_path):
            logger.error(f"Screenshot file not found: {screenshot_path}")
            return "Screenshot not available"
        
        prompt = VisionAnalysisPrompt.create(remaining_scenario, scenario, completed_steps)
        return self.vision_client.analyze_screenshot(prompt, screenshot_path)
