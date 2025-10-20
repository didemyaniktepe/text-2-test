from .base_command import ActionCommand
import logging

logger = logging.getLogger(__name__)

class NavigateCommand(ActionCommand):
    
    def __init__(self, page, url: str, description: str, locator: str):
        super().__init__(page, "", description, locator)
        self.url = url
    
    async def execute(self) -> bool:
        try:
            logger.info(f"Navigating to: {self.url}")
            await self.page.goto(self.url)
            await self.page.wait_for_load_state("networkidle", timeout=30000) 
            
            self.executed = True
            self.success = True
            logger.info(f"Successfully navigated to: {self.url}")
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            self.executed = True
            self.success = False
            return False


class ReloadCommand(ActionCommand):
    
    async def execute(self) -> bool:
        try:
            logger.info("Reloading page")
            await self.page.reload()
            await self.page.wait_for_load_state("networkidle", timeout=30000)   
            
            self.executed = True
            self.success = True
            logger.info("Page reloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Page reload failed: {e}")
            self.executed = True
            self.success = False
            return False