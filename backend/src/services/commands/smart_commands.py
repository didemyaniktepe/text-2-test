from .base_command import ActionCommand
import logging

logger = logging.getLogger(__name__)

class SmartClickCommand(ActionCommand):
    
    async def execute(self) -> bool:
        try:
            logger.info(f"Smart clicking element: {self.selector}")
            
            if await self._try_standard_click():
                return True
            
            if await self._try_force_click():
                return True
                
            if await self._try_javascript_click():
                return True
                
            if await self._try_coordinate_click():
                return True
                
            logger.error(f"All click methods failed for: {self.selector}")
            self.executed = True
            self.success = False
            return False
            
        except Exception as e:
            logger.error(f"Smart click failed: {e}")
            self.executed = True
            self.success = False
            return False
    
    async def _try_standard_click(self) -> bool:
        try:
            await self.page.wait_for_selector(self.selector, timeout=5000)
            await self.page.click(self.selector)
            logger.info("Standard click succeeded")
            self.executed = True
            self.success = True
            return True
        except:
            logger.warning("Standard click failed, trying alternatives")
            return False
    
    async def _try_force_click(self) -> bool:
        try:
            await self.page.click(self.selector, force=True)
            logger.info("Force click succeeded")
            self.executed = True
            self.success = True
            return True
        except:
            logger.warning("Force click failed")
            return False
    
    async def _try_javascript_click(self) -> bool:
        try:
            await self.page.evaluate(f'document.querySelector("{self.selector}").click()')
            logger.info("JavaScript click succeeded")
            self.executed = True
            self.success = True
            return True
        except:
            logger.warning("JavaScript click failed")
            return False
    
    async def _try_coordinate_click(self) -> bool:
        try:
            element = await self.page.query_selector(self.selector)
            if element:
                box = await element.bounding_box()
                if box:
                    x = box['x'] + box['width'] / 2
                    y = box['y'] + box['height'] / 2
                    await self.page.mouse.click(x, y)
                    logger.info("Coordinate click succeeded")
                    self.executed = True
                    self.success = True
                    return True
        except:
            logger.warning("Coordinate click failed")
            return False


class ToggleCommand(ActionCommand):
    
    async def execute(self) -> bool:
        try:
            if not await self.validate_selector():
                return False
                
            logger.info(f"Toggling element: {self.selector}")
            
            current_state = await self._get_toggle_state()
            logger.info(f"Current toggle state: {current_state}")
            
            await self.page.click(self.selector)
            
            await self.page.wait_for_timeout(500)
            new_state = await self._get_toggle_state()
            
            if new_state != current_state:
                logger.info(f"Toggle successful: {current_state} → {new_state}")
                self.executed = True
                self.success = True
                return True
            else:
                logger.warning("Toggle state did not change")
                self.executed = True
                self.success = False
                return False
                
        except Exception as e:
            logger.error(f"Toggle failed: {e}")
            self.executed = True
            self.success = False
            return False
    
    async def _get_toggle_state(self) -> bool:
        try:
            element = await self.page.query_selector(self.selector)
            
            aria_checked = await element.get_attribute('aria-checked')
            if aria_checked:
                return aria_checked.lower() == 'true'

            checked = await element.get_attribute('checked')
            if checked is not None:
                return True
            
            class_name = await element.get_attribute('class') or ""
            active_indicators = ['active', 'on', 'enabled', 'checked', 'selected']
            return any(indicator in class_name.lower() for indicator in active_indicators)
            
        except:
            return False


class SubmitFormCommand(ActionCommand):
    
    async def execute(self) -> bool:
        try:
            if not await self.validate_selector():
                return False
                
            logger.info(f"Submitting form: {self.selector}")
            
            if await self._try_submit_button():
                return True
                
            if await self._try_enter_key():
                return True
                
            if await self._try_javascript_submit():
                return True
            
            logger.error("All form submission methods failed")
            self.executed = True
            self.success = False
            return False
            
        except Exception as e:
            logger.error(f"Form submission failed: {e}")
            self.executed = True
            self.success = False
            return False
    
    async def _try_submit_button(self) -> bool:
        try:
            submit_selectors = [
                f'{self.selector} input[type="submit"]',
                f'{self.selector} button[type="submit"]',
                f'{self.selector} button:has-text("Submit")',
                f'{self.selector} button:has-text("Send")',
                f'{self.selector} .submit-btn',
                f'{self.selector} .btn-submit'
            ]
            
            for submit_selector in submit_selectors:
                try:
                    await self.page.wait_for_selector(submit_selector, timeout=2000)
                    await self.page.click(submit_selector)
                    logger.info(f"Submit button clicked: {submit_selector}")
                    self.executed = True
                    self.success = True
                    return True
                except:
                    continue
            
            return False
        except:
            return False
    
    async def _try_enter_key(self) -> bool:
        try:
            await self.page.press(self.selector, 'Enter')
            logger.info("Form submitted with Enter key")
            self.executed = True
            self.success = True
            return True
        except:
            return False
    
    async def _try_javascript_submit(self) -> bool:
        try:
            await self.page.evaluate(f'document.querySelector("{self.selector}").submit()')
            logger.info("Form submitted with JavaScript")
            self.executed = True
            self.success = True
            return True
        except:
            return False


class CloseModalCommand(ActionCommand):
    
    async def execute(self) -> bool:
        try:
            logger.info(f"Closing modal/popup: {self.selector}")
            
            if await self._try_close_button():
                return True
                
            if await self._try_escape_key():
                return True
                
            if await self._try_overlay_click():
                return True
                
            if await self._try_javascript_close():
                return True
            
            logger.error("All modal close methods failed")
            self.executed = True
            self.success = False
            return False
            
        except Exception as e:
            logger.error(f"Close modal failed: {e}")
            self.executed = True
            self.success = False
            return False
    
    async def _try_close_button(self) -> bool:
        try:
            close_selectors = [
                f'{self.selector} .close',
                f'{self.selector} .modal-close',
                f'{self.selector} [aria-label="Close"]',
                f'{self.selector} button:has-text("×")',
                f'{self.selector} button:has-text("Close")',
                f'{self.selector} .btn-close'
            ]
            
            for close_selector in close_selectors:
                try:
                    await self.page.wait_for_selector(close_selector, timeout=2000)
                    await self.page.click(close_selector)
                    logger.info(f"Close button clicked: {close_selector}")
                    self.executed = True
                    self.success = True
                    return True
                except:
                    continue
                    
            return False
        except:
            return False
    
    async def _try_escape_key(self) -> bool:
        try:
            await self.page.keyboard.press('Escape')
            logger.info("Modal closed with Escape key")
            await self.page.wait_for_timeout(500)
            
            modal_visible = await self.page.is_visible(self.selector)
            if not modal_visible:
                self.executed = True
                self.success = True
                return True
            return False
        except:
            return False
    
    async def _try_overlay_click(self) -> bool:
        try:
            overlay_selectors = [
                f'{self.selector}-overlay',
                f'{self.selector.replace("-modal", "-overlay")}',
                '.modal-overlay',
                '.overlay'
            ]
            
            for overlay_selector in overlay_selectors:
                try:
                    await self.page.click(overlay_selector)
                    logger.info(f"Overlay clicked: {overlay_selector}")
                    self.executed = True
                    self.success = True
                    return True
                except:
                    continue
            return False
        except:
            return False
    
    async def _try_javascript_close(self) -> bool:
        try:
            await self.page.evaluate(f'document.querySelector("{self.selector}").style.display = "none"')
            logger.info("Modal hidden with JavaScript")
            self.executed = True
            self.success = True
            return True
        except:
            return False