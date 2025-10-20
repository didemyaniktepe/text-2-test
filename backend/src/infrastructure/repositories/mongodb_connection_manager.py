import logging
import certifi
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from src.infrastructure.config.settings import MongoDBSettings

logger = logging.getLogger(__name__)


class MongoDBConnectionManager:
    def __init__(self, settings: MongoDBSettings):
        try:
            self.settings = settings
            self.client: MongoClient = MongoClient(
                settings.url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                tlsCAFile=certifi.where()
            )
            self.db: Database = self.client[settings.db_name]
            self.client.admin.command('ping')
            logger.info(f"MongoDB connection established successfully to database: {settings.db_name}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during MongoDB connection: {e}")
            raise

    def get_collection(self, collection_name: str) -> Collection:
        try:
            collection = self.db[collection_name]
            logger.debug(f"Collection '{collection_name}' accessed successfully")
            return collection
        except Exception as e:
            logger.error(f"Error accessing collection '{collection_name}': {e}")
            raise

    def is_connected(self) -> bool:
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    def get_database_info(self) -> dict:
        try:
            return {
                'database_name': self.db.name,
                'collections': self.db.list_collection_names(),
                'server_info': self.client.server_info()
            }
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {}

    def close(self):
        try:
            if self.client:
                self.client.close()
                logger.info("MongoDB connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
