import logging
from openai import OpenAI
from src.infrastructure.config.settings import OpenAISettings

logger = logging.getLogger(__name__)

class BaseOpenAIClient:

    def __init__(self, settings: OpenAISettings):
        self.settings = settings
        self.provider = settings.provider.lower()

        if self.provider == "deepseek":
            api_key = settings.deepseek_api_key
            base_url = settings.deepseek_base_url
            self.model = settings.deepseek_model
        elif self.provider == "openai":
            api_key = settings.api_key
            base_url = settings.base_url
                
            self.model = (
                settings.vision_model
                if self.__class__.__name__ == "VisionAnalysisClient"
                else settings.model
            )
        else:
            api_key = settings.api_key
            base_url = settings.base_url
            self.model = settings.model

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        logger.info("BaseOpenAIClient initialized (provider=%s, model=%s)", settings.provider, self.model)
    
    def _format_messages(self, messages: list) -> list:
        if self.provider != "deepseek":
            return messages
            
        return [
            {"role": "assistant" if msg["role"] == "system" else msg["role"], 
             "content": msg["content"]} 
            for msg in messages
        ]

    def _make_chat_completion(self, messages: list, target_model: str, **kwargs) -> str:
        logger.debug(f"Sending chat completion request to API with model: {target_model}")
        
        formatted_messages = self._format_messages(messages)
        response = self.client.chat.completions.create(
            model=target_model,
            messages=formatted_messages,
            **kwargs
        )
            
        logger.debug(f"Response received: {response}")
        return response.choices[0].message.content
            
