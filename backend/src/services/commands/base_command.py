from abc import ABC, abstractmethod
from playwright.async_api import Page
import logging
import re

logger = logging.getLogger(__name__)

class ActionCommand(ABC):
    
    def __init__(self, page: Page, selector: str, description: str, locator: str):
        self.page = page
        self.selector = selector
        self.description = description
        self.locator = locator
        self.used_selector = None
        self.resolved_locator = None
        self.executed = False
        self.success = False
        self.selector_parts = self._parse_selector(selector)
        
    def _parse_selector(self, selector: str):
        try:
            if not self._is_playwright_selector(selector):
                return None

            selector_type_match = re.match(r'(\w+)\(', selector)
            if not selector_type_match:
                return None
            
            selector_type = selector_type_match.group(1)
            
            params_match = re.match(r'\w+\((.*)\)$', selector)
            if not params_match:
                return None
            
            params_str = params_match.group(1)
            
            return {
                'type': selector_type,
                'params': params_str
            }
        except Exception as e:
            logger.error(f"Error parsing selector '{selector}': {e}")
            return None
            
    def _is_playwright_selector(self, selector: str) -> bool:
        playwright_patterns = [
            r'^getByRole\(',
            r'^getByText\(',
            r'^getByLabel\(',
            r'^getByTestId\(',
            r'^getByPlaceholder\(',
            r'^getByAltText\(',
            r'^getByTitle\(',
            r'^locator\('
        ]
        
        for pattern in playwright_patterns:
            if re.match(pattern, selector):
                return True
                
        if '.' in selector and any(method in selector for method in ['filter', 'nth', 'first', 'last']):
            return True
            
        return False
        
    @abstractmethod
    async def execute(self) -> bool:
        pass
    
    async def validate_selector(self) -> bool:
        try:
            if self.selector_parts:
                selector_type = self.selector_parts['type']
                
                if selector_type == 'getByRole':
                    count = await self.page.evaluate(f"""() => {{
                        try {{
                            return document.querySelectorAll('[role]').length > 0;
                        }} catch (e) {{
                            return false;
                        }}
                    }}""")
                    return count
                elif selector_type == 'getByText':
                    text_param = self.selector_parts['params'].strip("'").strip('"')
                    count = await self.page.evaluate(f"""() => {{
                        try {{
                            return document.body.textContent.includes('{text_param}');
                        }} catch (e) {{
                            return false;
                        }}
                    }}""")
                    return count
                elif selector_type == 'locator':
                    try:
                        css_selector = self.selector_parts['params'].strip("'").strip('"')
                        if css_selector.startswith('#') or css_selector.startswith('.'):
                            await self.page.wait_for_selector(css_selector, timeout=5000)
                            return True
                    except:
                        pass
                
                logger.info(f"Skipping validation for Playwright selector: {self.selector}")
                return True
            
            await self.page.wait_for_selector(self.selector, timeout=10000)
            return True
        except Exception as e:
            logger.error(f"Selector validation failed for '{self.selector}': {e}")
            return False
    
    async def post_execute_wait(self):
        try:
            await self.page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass
    
    def should_skip_action(self) -> bool:
        skip_indicators = [
            "no visible buttons", "no buttons", "no checkboxes",
            "no visible checkboxes", "no tasks", "no items",
            "initial state", "no interactions yet"
        ]
        
        return any(indicator in self.description.lower() for indicator in skip_indicators)
    
    async def get_locator_with_fallback(self):
        try:
            from src.utils.locator_resolver import resolve_locator
            primary_loc = resolve_locator(self.page, self.selector)

            loc = await self._ensure_single_match(primary_loc)
            await loc.wait_for(state="visible", timeout=3000)
            logger.info(f"Using primary selector: {self.selector}")
            self.used_selector = self.selector
            self.resolved_locator = loc
            return loc

        except Exception as primary_e:
            logger.warning(f"Primary selector failed: {primary_e}")

            if self.locator:
                try:
                    from src.utils.locator_resolver import resolve_locator
                    fallback_loc = resolve_locator(self.page, self.locator)
                    loc = await self._ensure_single_match(fallback_loc)
                    await loc.wait_for(state="visible", timeout=3000)
                    logger.info(f"Using fallback locator: {self.locator}")
                    self.used_selector = self.locator
                    self.resolved_locator = loc
                    return loc
                except Exception as fallback_e:
                    logger.warning(f"Fallback locator failed: {fallback_e}")

            if self.locator:
                try:
                    css_selector = self.locator.replace("locator('", "").replace("')", "")
                    
                    css_loc = self.page.locator(css_selector)
                    count = await css_loc.count()
                    
                    if count == 0 and 'data-testid=' in css_selector:
                        data_test_selector = css_selector.replace('data-testid=', 'data-test=')
                        css_loc = self.page.locator(data_test_selector)
                        count = await css_loc.count()
                        if count > 0:
                            logger.info(f"Found element with data-test fallback: {data_test_selector}")
                            css_selector = data_test_selector
                    
                    if count > 1:
                        logger.info(f"Multiple elements found ({count}), using first one")
                        self.used_selector = css_selector
                        self.resolved_locator = css_loc.first
                        return css_loc.first
                    elif count > 0:
                        self.used_selector = css_selector
                        self.resolved_locator = css_loc
                        return css_loc
                except Exception as css_e:
                    logger.error(f"CSS selector also failed: {css_e}")

            if not any(x in self.selector for x in ['getBy', 'locator(']):
                css_loc = self.page.locator(self.selector)
                count = await css_loc.count()
                if count > 1:
                    logger.info(f"Multiple elements found ({count}), using first one")
                    self.used_selector = self.selector
                    self.resolved_locator = css_loc.first
                    return css_loc.first
                self.used_selector = self.selector
                self.resolved_locator = css_loc
                return css_loc

            logger.error(f"Cannot use Playwright selector as CSS: {self.selector}")
            raise Exception(f"All selector strategies failed for: {self.selector}")

    async def _ensure_single_match(self, loc):
        try:
            count = await loc.count()
        except Exception:
            return loc

        if count == 1:
            return loc

        desc = (self.description or '').lower()

        try:
            name_match = re.search(r"name\s*:\s*['\"]([^'\"]+)['\"]", self.selector)
            if name_match:
                exact = name_match.group(1)
                refined = loc.filter(has_text=re.compile(rf"^\s*{re.escape(exact)}\s*$", re.IGNORECASE))
                if await refined.count() >= 1:
                    return refined.first
        except Exception:
            pass

        if any(tok in desc for tok in [' new ', 'new ', ' new', '(new)']):
            try:
                refined = loc.filter(has_text=re.compile(r"\bnew\b", re.IGNORECASE))
                if await refined.count() >= 1:
                    return refined.first
            except Exception:
                pass

        try:
            return loc.first
        except Exception:
            return loc