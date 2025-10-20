from playwright.async_api import Page
from .base_command import ActionCommand
from .fill_command import FillCommand, FillSubmitCommand
from .click_command import ClickCommand
from .check_command import CheckCommand, UncheckCommand
from .select_command import SelectCommand
from .navigation_commands import NavigateCommand, ReloadCommand
from .input_commands import ClearInputCommand, TypeCommand, PressKeyCommand
from .smart_commands import SmartClickCommand, ToggleCommand, SubmitFormCommand, CloseModalCommand
import logging

logger = logging.getLogger(__name__)

class CommandFactory:   
    
    @staticmethod
    def create_command(page: Page, selector: str, description: str, action_type: str, locator: str = None) -> ActionCommand:
        if action_type == "fill_submit":
            return FillSubmitCommand(page, selector, description, locator)
        elif action_type == "fill":
            return FillCommand(page, selector, description, locator)
        elif action_type == "click":
            return ClickCommand(page, selector, description, locator)
        elif action_type == "check":
            return CheckCommand(page, selector, description, locator)
        elif action_type == "uncheck":
            return UncheckCommand(page, selector, description, locator)
        elif action_type == "select":
            return SelectCommand(page, selector, description, locator)
            
        elif action_type == "navigate":
            url = CommandFactory._extract_url_from_description(description)
            return NavigateCommand(page, url, description, locator)
        elif action_type == "reload":
            return ReloadCommand(page, selector, description, locator)
            
        elif action_type == "clear_input":
            return ClearInputCommand(page, selector, description, locator)
        elif action_type == "type":
            delay = CommandFactory._extract_delay_from_description(description)
            return TypeCommand(page, selector, description, delay, locator)
        elif action_type == "press_key":
            key = CommandFactory._extract_key_from_description(description)
            return PressKeyCommand(page, key, description, selector, locator)
            
        elif action_type == "smart_click":
            return SmartClickCommand(page, selector, description, locator)
        elif action_type == "toggle":
            return ToggleCommand(page, selector, description, locator)
        elif action_type == "submit_form":
            return SubmitFormCommand(page, selector, description, locator)
        elif action_type == "close_modal":
            return CloseModalCommand(page, selector, description, locator)
            
        else:
            logger.warning(f"Unknown action type '{action_type}', defaulting to click")
            return ClickCommand(page, selector, description, locator)
    
    @staticmethod
    def _extract_url_from_description(description: str) -> str:
        import re
        url_pattern = r'(?:https?://|www\.|/)[^\s]+'
        match = re.search(url_pattern, description)
        return match.group(0) if match else ""
    
    @staticmethod 
    def _extract_text_from_description(description: str) -> str:
        import re
        quotes_matches = re.findall(r'["\']([^"\']+)["\']', description)
        return quotes_matches[-1] if quotes_matches else ""
    
    @staticmethod
    def _extract_count_from_description(description: str) -> int:
        import re
        count_match = re.search(r'\b(\d+)\b', description)
        return int(count_match.group(1)) if count_match else 1
    
    @staticmethod
    def _extract_delay_from_description(description: str) -> int:
        import re
        delay_match = re.search(r'delay\s*(\d+)', description.lower())
        return int(delay_match.group(1)) if delay_match else 100
    
    @staticmethod
    def _extract_key_from_description(description: str) -> str:
        import re
        
        key_mappings = {
            'enter': 'Enter',
            'tab': 'Tab', 
            'escape': 'Escape',
            'space': 'Space',
            'arrow up': 'ArrowUp',
            'arrow down': 'ArrowDown',
            'arrow left': 'ArrowLeft',
            'arrow right': 'ArrowRight',
            'ctrl+a': 'Control+A',
            'ctrl+c': 'Control+C',
            'ctrl+v': 'Control+V'
        }
        
        description_lower = description.lower()
        for pattern, key in key_mappings.items():
            if pattern in description_lower:
                return key
        
        key_match = re.search(r'["\']([^"\']+)["\']', description)
        return key_match.group(1) if key_match else 'Enter'
        
