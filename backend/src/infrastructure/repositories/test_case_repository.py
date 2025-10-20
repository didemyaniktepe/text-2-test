import logging
from datetime import datetime
from pymongo.collection import Collection

from src.domain.test.entities.test_case import TestCase
from src.domain.test.value_objects.test_status import TestStatus
from src.domain.exceptions.test_exceptions import TestNotFoundError
from src.infrastructure.repositories.mongodb_connection_manager import MongoDBConnectionManager

logger = logging.getLogger(__name__)


class TestCaseRepository:
    def __init__(self, connection_manager: MongoDBConnectionManager):
        self.connection_manager = connection_manager
        self.collection: Collection = connection_manager.get_collection('test_cases')
        logger.info("TestCaseRepository initialized")

    def save(self, test_case: TestCase) -> None:
        test_data = {
            'id': test_case.id,
            'url': test_case.url,
            'scenario': test_case.scenario,
            'generated_script': test_case.generated_script,
            'created_at': test_case.created_at.isoformat(),
            'status': test_case.status.name
        }
        self.collection.update_one(
            {'id': test_case.id},
            {'$set': test_data},
            upsert=True
        )
        logger.debug(f"Test case saved to MongoDB - ID: {test_case.id}")

    def get_by_id(self, test_id: str) -> TestCase:
        test_data = self.collection.find_one({'id': test_id})
        if not test_data:
            logger.error(f"Test case not found in MongoDB with ID: {test_id}")
            raise TestNotFoundError(f"Test case not found with ID: {test_id}")

        return TestCase(
            id=test_data['id'],
            url=test_data['url'],
            scenario=test_data['scenario'],
            generated_script=test_data['generated_script'],
            created_at=datetime.fromisoformat(test_data['created_at']),
            status=TestStatus[test_data['status']]
        )
