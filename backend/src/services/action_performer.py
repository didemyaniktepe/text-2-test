from playwright.async_api import Page
from .commands.command_factory import CommandFactory
import logging

logger = logging.getLogger(__name__)


class ActionPerformer:

    def __init__(self):
        self.command_history = []

    async def perform_action(self, page: Page, selector: str, description: str, action_type: str, locator: str = "") -> tuple[bool, str, str]:
        command = CommandFactory.create_command(page, selector, description, action_type, locator)
        success = await command.execute()
        await self._wait_for_stability(page, description, action_type)
        used_selector = getattr(command, 'used_selector', selector)
        resolved_locator = getattr(command, 'resolved_locator', "")
        
        if resolved_locator:
            resolved_locator_str = str(resolved_locator)
        else:
            resolved_locator_str = ""
            
        return success, used_selector, resolved_locator_str
    
    async def _wait_for_stability(self, page, description, action_type):
        if self._is_navigation_action(description, action_type):
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=5000)
            except:
                pass
            await page.wait_for_timeout(2000)
        else:
            await page.wait_for_timeout(1000)
        
    def _is_navigation_action(self, description, action_type):
        navigation_actions = ['click', 'submit']
        navigation_keywords = ['login', 'submit', 'sign in', 'continue', 'next', 'enter']
        
        return (action_type.lower() in navigation_actions and 
                any(keyword in description.lower() for keyword in navigation_keywords))