from datetime import datetime, timezone
import uuid
import logging

from src.domain.test.entities.test_case import TestCase
from src.domain.test.value_objects.test_status import TestStatus
from src.domain.exceptions.test_exceptions import TestNotFoundError
from src.infrastructure.repositories.test_case_repository import TestCaseRepository
from src.services.test_generator_service import TestGenerator
from src.services.test_runner_service import TestRunner

logger = logging.getLogger(__name__)

class TestCaseService:
    def __init__(self, test_generator: TestGenerator, test_runner: TestRunner, repository: TestCaseRepository):
        self.test_generator = test_generator
        self.test_runner = test_runner
        self.repository = repository

    async def create(self, scenario: str, url: str, folder_name: str = "") -> TestCase:
        test_id = str(uuid.uuid4())
        test_code = await self.test_generator.generate(scenario, url, folder_name)
            
        test_case = TestCase(
                id=test_id,
                url=url,
                scenario=scenario,
                generated_script=test_code,
                created_at=datetime.now(timezone.utc),
                status=TestStatus.PENDING
        )
            
        self.repository.save(test_case)
        return test_case

    async def run_test_by_id(self, test_id: str):
        try:
            test_case = self.repository.get_by_id(test_id)
            async for status in self.test_runner.run(test_case):
                yield status
        except TestNotFoundError as e:
            logger.error(f"Test case not found: {test_id}")
            raise e
        except Exception as e:
            logger.error(f"Test execution failed for {test_id}: {str(e)}", exc_info=True)
            raise e