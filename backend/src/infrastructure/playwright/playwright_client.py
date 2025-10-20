import asyncio
import logging
import os
from pathlib import Path
from typing import AsyncIterator

from src.domain.exceptions.test_exceptions import TestExecutionError
from src.domain.test.entities.test_case import TestCase
from src.domain.test.value_objects.test_status import TestStatus
from src.infrastructure.config.settings import PlaywrightSettings
from src.infrastructure.playwright.config import get_playwright_config_template
from src.infrastructure.repositories.test_case_repository import TestCaseRepository



class PlaywrightClient:
    def __init__(self, settings: PlaywrightSettings, 
                 test_case_repository: TestCaseRepository):
        self.settings = settings
        self.test_case_repository = test_case_repository

    def get_project_root(self) -> Path:
        return Path(__file__).resolve().parents[3]

    def _prepare_test_file(self, test_case: TestCase) -> Path:
        try:
            test_dir = self.get_project_root() / "src" / "db" / "generated"
            os.makedirs(test_dir, exist_ok=True)

            test_file = test_dir / f"test_{test_case.id}.spec.js"
            with open(test_file, "w") as f:
                f.write(test_case.generated_script)

            config_content = get_playwright_config_template()

            config_file = test_dir / "playwright.config.js"
            if not os.path.exists(config_file):
                with open(config_file, "w") as f:
                    f.write(config_content.format(
                        headless=str(self.settings.headless).lower(),
                        slow_mo=self.settings.slow_mo,
                        viewport_width=self.settings.viewport_width,
                        viewport_height=self.settings.viewport_height,
                        reporter=self.settings.reporter,
                        timeout=self.settings.timeout
                    ))
            return test_file

        except Exception as e:
            error_msg = f"Failed to prepare test files: {str(e)}"
            raise TestExecutionError(error_msg)

    async def run(self, test_case: TestCase) -> AsyncIterator[TestStatus]:
        try:
            test_case.status = TestStatus.RUNNING
            yield test_case.status

            test_file = self._prepare_test_file(test_case)

            with open(test_file, 'r') as f:
                test_script = f.read()

            with open(test_file, 'w') as f:
                f.write(test_script)

            cmd = [
                "npx",
                "playwright",
                "test",
                str(test_file),
                "--headed",
                "--debug",
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=test_file.parent
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                test_case.status = TestStatus.SUCCESS
            else:
                test_case.status = TestStatus.FAILED

            yield test_case.status

        except Exception as e:
            test_case.status = TestStatus.FAILED
            yield test_case.status
            
            
