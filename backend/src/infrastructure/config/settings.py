from pydantic_settings import BaseSettings
from typing import List
import logging
from pathlib import Path


class LoggingSettings(BaseSettings):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"

    class Config:
        env_prefix = "LOGGING_"

    def configure(self) -> None:
        logging.basicConfig(
            level=getattr(logging, self.level),
            format=self.format,
            datefmt=self.date_format
        )


class OpenAISettings(BaseSettings):
    # provider: str = "deepseek"  
    provider: str = "openai"
    api_key: str = "API_KEY"
    model: str = "gpt-4o"  
    # model: str = "deepseek-chat"  

    base_url: str | None = None

    deepseek_api_key: str = "API_KEY"
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    vision_provider: str = "openai"
    vision_model: str = "gpt-4o"

    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60
    fine_tuned_model: str = "ft:gpt-3.5-turbo-0125:personal::BdHHhW16"

    class Config:
        env_prefix = "OPENAI_"
        extra = "allow"


class PlaywrightSettings(BaseSettings):
    headless: bool = False
    slow_mo: int = 2000
    viewport_width: int = 1280
    viewport_height: int = 720
    reporter: str = "list"
    timeout: int = 30000
    test_directory: str = "src/db/generated"
    browser: str = "chromium"
    headed: bool = False
    video: bool = False
    screenshot: str = "off"

    class Config:
        env_prefix = "PLAYWRIGHT_"



class APISettings(BaseSettings):
    api_v1_str: str = "/api/v1"
    project_name: str = "Text-to-Test"
    backend_cors_origins: List[str] = ["*"]

    class Config:
        env_prefix = "API_"


class MongoDBSettings(BaseSettings):
    url: str = "mongodb+srv://didem:RZcc2wQEnAZPHUT8@cluster0.7ao5na8.mongodb.net/"
    db_name: str = "text_to_test"
    collection_name: str = "test_cases"

    class Config:
        env_prefix = "MONGODB_"


class Settings(BaseSettings):
    environment: str = "development"
    logging: LoggingSettings = LoggingSettings()
    openai: OpenAISettings = OpenAISettings()
    playwright: PlaywrightSettings = PlaywrightSettings()
    api: APISettings = APISettings()
    mongodb: MongoDBSettings = MongoDBSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"

    def configure_logging(self) -> None:
        self.logging.configure()
        logger = logging.getLogger(__name__)
        logger.info(
            "Logging configured - Level: %s, Environment: %s",
            self.logging.level,
            self.environment
        )


def get_settings() -> Settings:
    settings = Settings()
    settings.configure_logging()
    return settings
