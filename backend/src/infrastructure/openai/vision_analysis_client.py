import base64
from .base_openai_client import BaseOpenAIClient
from src.infrastructure.config.settings import OpenAISettings
import logging


logger = logging.getLogger(__name__)

class VisionAnalysisClient(BaseOpenAIClient):
    
    def __init__(self, settings: OpenAISettings):
        settings.provider = settings.vision_provider
        super().__init__(settings)
        logger.info("VisionAnalysisClient initialized using %s model", self.model)
        
    def analyze_screenshot(self, prompt_text: str, screenshot_path: str) -> str:
        messages = self.get_openai_messages(prompt_text, screenshot_path)
        response = self._make_chat_completion(
            messages=messages,
            target_model=self.model,
            temperature=0.1,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        return response
    
    def get_openai_messages(self, prompt_text: str, screenshot_path: str) -> list:
        with open(screenshot_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        messages = [
            {"role": "system", "content": "You are an expert UI analyst. Analyze screenshots and provide detailed descriptions of the visual interface."},
            {"role": "user", "content": [{"type": "text", "text": prompt_text},{"type": "image_url","image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}
        ]
        return messages
           
                    
                    
                    
                    