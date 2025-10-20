from typing import Dict, List, Any
from src.utils.element_utils import format_completed_steps

class TestCodePrompt:
    @staticmethod
    def create(test_steps: List[Dict[str, Any]], scenario: str, url: str) -> str:
        steps_info = format_completed_steps(test_steps)

        return f"""
You are a senior Playwright engineer. 
Output ONLY runnable JavaScript code (CommonJS). 

INPUTS:
- SCENARIO: {scenario}
- URL: {url}
- STEPS: {steps_info}

Rules:
- Import: const {{ test, expect }} = require('@playwright/test');
- Single test. No test.use, no waitForTimeout.
- Use locator mapping strictly:
  getByRole(...) -> page.getByRole(...)
  getByText(...) -> page.getByText(...)
  getByLabel(...) -> page.getByLabel(...)
  locator(...) -> page.locator(...)
  frameLocator(...) -> page.frameLocator(...)
  locator('<IFRAME>').contentLocator('<INNER>') -> page.frameLocator('<IFRAME>').locator('<INNER>')
  Else -> page.locator('<raw>')
- Actions:
  click -> await L.click()
  fill -> await expect(L).toBeVisible(); await L.fill(<value>)
  check -> await L.check()
  uncheck -> await L.uncheck()
  select (native) -> await L.selectOption(<valueOrLabel>)
  select (custom) -> await L.click(); await page.getByRole('option', {{ name: <label> }}).click()
  fill_submit -> await L.fill(<value>); await L.press('Enter')
- Smart waits:
  await expect(L).toBeVisible() before interacting; await expect(L).toBeEnabled() for inputs/buttons.
  After navigation: await expect(page).toHaveURL(/.+/)
- Assertions are mandatory: if none provided, assert success via URL/text/count that proves outcome.

OUTPUT FORMAT (JS only):
const {{ test, expect }} = require('@playwright/test');

test('{scenario}', async ({{ page }}) => {{
  await page.goto('{url}');
  // Implement STEPS exactly in order using mapped locator APIs, smart waits, and assertions.
}});
"""