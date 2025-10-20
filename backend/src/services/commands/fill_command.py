import re

from src.utils.locator_resolver import resolve_locator
from .base_command import ActionCommand
import logging

logger = logging.getLogger(__name__)

class FillCommand(ActionCommand):
    async def execute(self) -> bool:
        try:
            text = self._extract_text_from_description()
            if not text:
                logger.error(f"No text found to fill in: '{self.description}'")
                return False

            loc = await self.get_locator_with_fallback()
            logger.info(f"Resolved locator =========:  {loc}")
            try:
                await loc.wait_for(state="visible", timeout=10000)
            except Exception as e:
                logger.warning(f"Locator wait_for visible failed, continuing anyway: {e}")

            logger.info(f"Filling text '{text}' into: {self.selector}")
            try:
                await loc.click(timeout=3000)
            except Exception as e:
                logger.debug(f"Optional pre-click skipped: {e}")
            await loc.fill(text)

            self.executed = True
            self.success = True
            logger.info(f"Successfully filled text '{text}'")
            return True

        except Exception as e:
            logger.error(f"Fill command failed: {e}")
            self.executed = True
            self.success = False
            return False
    
    def _extract_text_from_description(self) -> str:
        quotes_matches = re.findall(r'["\']([^"\']+)["\']', self.description)
        if quotes_matches:
            text = quotes_matches[-1]
            logger.info(f"Extracted quoted text: '{text}'")
            return text
        
        with_match = re.search(r'with\s+(.+?)(?:\s+(?:in|into|to|field|input)\s|$)', self.description, re.IGNORECASE)
        if with_match:
            text = with_match.group(1).strip()
            logger.info(f"Extracted 'with' text: '{text}'")
            return text
            
        patterns = [r'(?:enter|type|fill|write)\s+(.+?)(?:\s+(?:in|into|to|field|input)\s|$)']
        for pattern in patterns:
            match = re.search(pattern, self.description, re.IGNORECASE)
            if match:
                text = match.group(1).strip().strip('"\'')
                logger.info(f"Extracted pattern text: '{text}'")
                return text
                
        logger.warning(f"No text extracted from: '{self.description}'")
        return ""


class FillSubmitCommand(FillCommand):
    async def execute(self) -> bool:
        try:
            text = self._extract_text_from_description()
            if not text:
                logger.error(f"No text found to fill in: '{self.description}'")
                return False

            loc = await self.get_locator_with_fallback()
            logger.info(f"Resolved locator =========:  {loc}")
            
            try:
                await loc.wait_for(state="visible", timeout=10000)
            except Exception as e:
                logger.warning(f"Locator not visible yet (continuing anyway): {e}")

            logger.info(f"Filling and submitting text '{text}' into: {self.selector}")
            await loc.fill(text)

            logger.info("Successfully filled text, now submitting via Enter...")
            try:
                await loc.press('Enter')
            except Exception as e:
                logger.warning(f"loc.press failed ({e}), falling back to page.keyboard")
                await self.page.keyboard.press('Enter')

            
            await self.post_execute_wait()

            self.executed = True
            self.success = True
            return True

        except Exception as e:
            logger.error(f"FillSubmit command failed: {e}")
            self.executed = True
            self.success = False
            return False