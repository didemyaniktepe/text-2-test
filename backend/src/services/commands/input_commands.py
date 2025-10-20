import re
from .base_command import ActionCommand
import logging

logger = logging.getLogger(__name__)

class ClearInputCommand(ActionCommand):
    
    async def execute(self) -> bool:
        try:
            if not await self.validate_selector():
                return False
            
            await self.page.fill(self.selector, "")
            
            await self.page.focus(self.selector)
            await self.page.keyboard.press("Control+A")
            await self.page.keyboard.press("Delete")
            
            self.executed = True
            self.success = True
            return True
            
        except Exception as e:
            logger.error(f"Clear input failed: {e}")
            self.executed = True
            self.success = False
            return False


class TypeCommand(ActionCommand):
    
    def __init__(self, page, selector: str, description: str, delay: int = 100, locator: str = ""):
        super().__init__(page, selector, description, locator)
        self.delay = delay
    
    async def execute(self) -> bool:
        try:
            text = self._extract_text_from_description()
            if not text:
                logger.error(f"No text found to type in: '{self.description}'")
                return False
                
            if not await self.validate_selector():
                return False
                
            await self.page.focus(self.selector)
            await self.page.type(self.selector, text, delay=self.delay)
            
            self.executed = True
            self.success = True
            return True
            
        except Exception as e:
            logger.error(f"Type command failed: {e}")
            self.executed = True
            self.success = False
            return False
    
    def _extract_text_from_description(self) -> str:
        quotes_matches = re.findall(r'["\']([^"\']+)["\']', self.description)
        if quotes_matches:
            return quotes_matches[-1]
        
        patterns = [r'(?:type|write)\s+(.+?)(?:\s+(?:in|into|to)\s|$)']
        for pattern in patterns:
            match = re.search(pattern, self.description, re.IGNORECASE)
            if match:
                return match.group(1).strip().strip('"\'')
        
        return ""


class PressKeyCommand(ActionCommand):
    
    def __init__(self, page, key: str, description: str, selector: str = "", locator: str = ""):
        super().__init__(page, selector, description, locator)
        self.key = key
    
    async def execute(self) -> bool:
        try:
            if self.selector:
                loc = await self.get_locator_with_fallback()
                logger.info(f"Pressing '{self.key}' on element: {self.selector}")
                logger.info(f"Resolved locator =========:  {loc}")
                await loc.press(self.key)
            else:
                logger.info(f"Pressing '{self.key}' globally")
                await self.page.keyboard.press(self.key)
            
            await self.post_execute_wait()
            
            self.executed = True
            self.success = True
            logger.info(f"Successfully pressed key: '{self.key}'")
            return True
            
        except Exception as e:
            logger.error(f"Press key failed: {e}")
            self.executed = True
            self.success = False
            return False