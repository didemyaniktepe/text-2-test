
from typing import AsyncIterator
from src.domain.test.entities.test_case import TestCase
from src.domain.test.value_objects.test_status import TestStatus
from src.infrastructure.playwright.playwright_client import PlaywrightClient
from src.infrastructure.repositories.test_case_repository import TestCaseRepository


class TestRunner:
    def __init__(self, playwright_client: PlaywrightClient, test_case_repository: TestCaseRepository):
        self.playwright_client = playwright_client
        self.test_case_repository = test_case_repository

    async def run(self, test_case: TestCase) -> AsyncIterator[TestStatus]:
        try:
            async for status in self.playwright_client.run(test_case):
                test_case.status = status
                self.test_case_repository.save(test_case)
                yield status
        except Exception:
            test_case.status = TestStatus.FAILED
            self.test_case_repository.save(test_case)
            yield test_case.status
