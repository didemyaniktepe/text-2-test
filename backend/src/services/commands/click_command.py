import re
from src.utils.locator_resolver import resolve_locator
from playwright.async_api import Locator
from .base_command import ActionCommand
import logging

logger = logging.getLogger(__name__)

class ClickCommand(ActionCommand):
    async def execute(self) -> bool:
        try:
            if self.should_skip_action():
                return False

            loc: Locator = await self.get_locator_with_fallback()

            if not await self.validate_selector():
                logger.warning(f"Selector validation failed, but continuing with click: {self.selector}")

            if await self._is_submission_with_enter(loc):
                return await self._handle_submission(loc)

            logger.info(f"Clicking element: {self.selector}")
            logger.info(f"Resolved locator =========:  {loc}")
            await self._smart_click(loc)

            await self.post_execute_wait()

            self.executed = True
            self.success = True
            logger.info("Successfully clicked.")
            return True

        except Exception as e:
            logger.error(f"Click command failed: {e}")
            self.executed = True
            self.success = False
            return False

    async def _option_click(self, text: str) -> bool:
        try:
            # First wait for any overlay panel to be visible
            overlay = self.page.locator('.p-overlaypanel, .p-menu-overlay, .p-contextmenu')
            await overlay.wait_for(state='visible', timeout=5000)
            
            selectors = [
                f'.overlay-menu .menu-item:has-text("{text}")',
                f'.menu-item span:text-is("{text}")',
                
                f'.p-overlaypanel .option-item:has-text("{text}")',
                f'.p-menu-overlay .p-menuitem:has-text("{text}")',
                
                f'.p-overlaypanel-content span:text-is("{text}")',
                f'.p-menuitem-text:text-is("{text}")',
                
                f'.p-overlaypanel .option-item:has(.option-text:text="{text}")',
                f'.p-menu-overlay .p-menuitem:has(.p-menuitem-text:text="{text}")',
                
                f'.p-overlaypanel-content .option-item:has-text("{text}")',
                f'.p-menu-list .p-menuitem:has-text("{text}")'
            ]
            
            for selector in selectors:
                try:
                    logger.info(f"Trying selector: {selector}")
                    element = self.page.locator(selector)
                    
                    if await element.count() > 0:
                        visible_element = element.first
                        await visible_element.wait_for(state='visible', timeout=5000)
                        
                        is_visible = await visible_element.evaluate("""el => {
                            const rect = el.getBoundingClientRect();
                            return rect.top >= 0 &&
                                   rect.left >= 0 &&
                                   rect.bottom <= window.innerHeight &&
                                   rect.right <= window.innerWidth;
                        }""")
                        
                        if not is_visible:
                            await visible_element.scroll_into_view_if_needed()
                            await self.page.wait_for_timeout(500)
                        
                        await visible_element.hover()
                        await self.page.wait_for_timeout(500)
                        await visible_element.click(timeout=5000)
                        logger.info(f"Successfully clicked option with selector: {selector}")
                        return True
                        
                except Exception as e:
                    logger.warning(f"Failed to click with selector '{selector}': {e}")
                    continue
            
            return False
        except Exception as e:
            logger.error(f"Option click failed: {e}")
            return False

    async def _smart_click(self, loc: Locator) -> None:
        try:
            logger.info(f"Smart clicking element: {loc}")
            
            if '-menu' in self.selector:
                logger.info("Detected menu button")
                try:
                    await loc.wait_for(state='attached', timeout=5000)
                    
                    await loc.evaluate("""el => {
                        el.style.opacity = '1';
                        el.style.visibility = 'visible';
                        el.style.display = 'inline-block';
                        
                        const parent = el.parentElement;
                        if (parent) {
                            parent.style.opacity = '1';
                            parent.style.visibility = 'visible';
                            parent.style.display = 'flex';
                        }
                    }""")
                    
                    await loc.hover()
                    await self.page.wait_for_timeout(500)
                    await loc.click(force=true, timeout=5000)
                    
                    menu = self.page.locator('.p-overlaypanel, .p-menu-overlay')
                    await menu.wait_for(state='visible', timeout=5000)
                    return
                except Exception as e:
                    logger.warning(f"Menu button click failed: {e}")
            
            if '.p-overlaypanel' in self.selector:
                text_match = re.search(r':has-text\("([^"]+)"\)', self.selector)
                if text_match:
                    text = text_match.group(1)
                    logger.info(f"Found option text: {text}")
                    if await self._option_click(text):
                        return
                    logger.warning("Option click failed, falling back to normal click")
            
            quoted_text = re.findall(r"['\"](.*?)['\"]", self.description)
            target_text = quoted_text[0] if quoted_text else None
            
            if target_text:
                logger.info(f"Looking for element with text: {target_text}")
                filtered_loc = loc.filter(has_text=target_text)
                if await filtered_loc.count() > 0:
                    logger.info(f"Found element with text: {target_text}")
                    loc = filtered_loc.first
                else:
                    logger.warning(f"No element found with text: {target_text}, falling back to original selector")
            
            await loc.wait_for(state="visible", timeout=10000)
            
            tag_name = await loc.evaluate("el => el.tagName.toLowerCase()")
            
            if tag_name == "img" or await loc.get_attribute('data-pd-tooltip') == 'true':
                logger.info("Detected special image element")
                
                is_menu_trigger = await loc.evaluate("""el => {
                    return el.id === 'details-more-menu' ||
                           el.hasAttribute('data-pd-tooltip') ||
                           (el.closest('.action-buttons') && el.tagName.toLowerCase() === 'img');
                }""")
                
                if is_menu_trigger:
                    logger.info("Detected menu trigger image")
                    if await self._image_click(loc):
                        return
                    
                # If not a menu trigger or menu trigger click failed, try normal image click
                if await self._image_click(loc):
                    return
            
            try:
                if hasattr(loc, "is_enabled") and not await loc.is_enabled():
                    logger.warning("Element is not enabled")
            except Exception:
                pass

            try:
                await loc.click(timeout=10000)
                return
            except Exception as e1:
                logger.warning(f"Normal click failed, trying scroll+click: {e1}")

            try:
                await loc.scroll_into_view_if_needed(timeout=5000)
                await loc.click(timeout=10000)
                return
            except Exception as e2:
                logger.warning(f"Scroll+click failed, trying force click: {e2}")

            await loc.click(timeout=10000, force=True)
            
        except Exception as e:
            logger.error(f"Smart click failed with error: {e}")
            try:
                await loc.click(timeout=10000, force=True)
            except Exception as final_e:
                logger.error(f"Final click attempt failed: {final_e}")
                raise

    async def _is_submission_with_enter(self, loc: Locator) -> bool:
        if not self._is_submission_action():
            return False

        try:
            tag = await loc.evaluate("el => el.tagName") 
            tag = (tag or "").lower()
            if tag != "input":
                return False

            inp_type = await loc.get_attribute("type")
            inp_type = (inp_type or "").lower()
            if inp_type not in ("text", "email", "search"):
                return False

            try:
                form = loc.locator("xpath=ancestor::form[1]")
                if await form.count() > 0:
                    submit_btn = form.locator("button[type='submit'], [type='submit']")
                    if await submit_btn.count() > 0 and await submit_btn.first.is_visible():
                        return False
            except Exception:
                pass

            return True
        except Exception:
            return False

    async def _handle_submission(self, loc: Locator) -> bool:
        try:
            logger.info(f"Using Enter for submission on: {self.selector}")
            await loc.press("Enter")
            logger.info("Successfully pressed Enter for submission")
            await self.post_execute_wait()
            return True
        except Exception as e:
            logger.error(f"Enter submission failed: {e}")
            return False

    async def _image_click(self, loc: Locator) -> bool:
        try:
            is_menu_trigger = await loc.evaluate("""el => {
                const isMenuTrigger = el.id === 'details-more-menu' ||
                                    el.hasAttribute('data-pd-tooltip') ||
                                    (el.closest('.action-buttons') && el.tagName.toLowerCase() === 'img') ||
                                    el.hasAttribute('aria-haspopup') ||
                                    el.hasAttribute('aria-controls');
                
                if (isMenuTrigger) {
                    // Make sure the element and its container are visible
                    const actionButtons = el.closest('.action-buttons');
                    if (actionButtons) {
                        actionButtons.style.opacity = '1';
                        actionButtons.style.visibility = 'visible';
                        actionButtons.style.display = 'flex';
                    }
                }
                
                return isMenuTrigger;
            }""")
            
            if is_menu_trigger:
                logger.info("Detected menu trigger button")
                try:
                    await loc.evaluate("""el => {
                        el.style.opacity = '1';
                        el.style.visibility = 'visible';
                        el.style.display = 'inline-block';
                        
                        const actionButtons = el.closest('.action-buttons');
                        if (actionButtons) {
                            actionButtons.style.opacity = '1';
                            actionButtons.style.visibility = 'visible';
                            actionButtons.style.display = 'flex';
                        }
                    }""")
                    
                    await loc.hover()
                    await self.page.wait_for_timeout(500)
                    await loc.click(force=True, timeout=5000)
                    
                    overlay = self.page.locator('.p-overlaypanel')
                    await overlay.wait_for(state='visible', timeout=5000)
                    return True
                    
                except Exception as e:
                    logger.warning(f"Direct click failed: {e}, trying parent")
                    try:
                        parent = loc.locator("xpath=ancestor::*[@role='button' or @class[contains(., 'button')] or contains(@class, 'clickable')][1]")
                        if await parent.count() > 0:
                            await parent.hover()
                            await self.page.wait_for_timeout(500)
                            await parent.click(force=True, timeout=5000)
                            await overlay.wait_for(state='visible', timeout=5000)
                            return True
                    except Exception as parent_e:
                        logger.warning(f"Parent click failed: {parent_e}")
            
            is_svg_image = await loc.evaluate("""el => {
                let parent = el.parentElement;
                while (parent) {
                    if (parent.tagName.toLowerCase() === 'svg') {
                        return true;
                    }
                    parent = parent.parentElement;
                }
                return false;
            }""")
            
            if is_svg_image:
                logger.info("Image is inside SVG, looking for clickable wrapper")
                wrapper = loc.locator("xpath=ancestor::*[@role='button' or @class[contains(., 'button')] or @class[contains(., 'clickable')] or @class[contains(., 'menu-item')]][1]")
                
                if await wrapper.count() > 0:
                    logger.info("Found clickable wrapper, using it for click")
                    await wrapper.hover()
                    await self.page.wait_for_timeout(500)
                    await wrapper.click(timeout=10000)
                    return True
            
            parent = loc.locator("..")
            
            parent_clickable = await parent.evaluate("""el => {
                const style = window.getComputedStyle(el);
                return style.pointerEvents !== 'none' && 
                       style.display !== 'none' && 
                       style.visibility !== 'hidden' &&
                       (el.tagName.toLowerCase() === 'a' || 
                        el.tagName.toLowerCase() === 'button' ||
                        el.onclick || 
                        el.getAttribute('role') === 'button' ||
                        el.className.includes('button') ||
                        el.className.includes('clickable') ||
                        el.className.includes('menu-item'));
            }""")
            
            if parent_clickable:
                logger.info("Parent element is clickable, clicking parent instead")
                await parent.hover()
                await self.page.wait_for_timeout(500)
                await parent.click(timeout=10000)
                return True
                
        except Exception as parent_e:
            logger.warning(f"Parent click failed: {parent_e}, falling back to image click")
        
        try:
            await loc.hover()
            await self.page.wait_for_timeout(500)
            
            try:
                await loc.click(timeout=10000, force=True)
                return True
            except Exception as force_e:
                logger.warning(f"Force click failed: {force_e}")
            
            try:
                await loc.evaluate("""el => {
                    const clickEvent = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    el.dispatchEvent(clickEvent);
                    
                    el.click();
                }""")
                return True
            except Exception as js_e:
                logger.warning(f"JavaScript click failed: {js_e}")
            
            try:
                await parent.evaluate("""el => {
                    const clickEvent = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    el.dispatchEvent(clickEvent);
                    el.click();
                }""")
                return True
            except Exception as parent_js_e:
                logger.warning(f"Parent JavaScript click failed: {parent_js_e}")
                
        except Exception as e:
            logger.error(f"All image click strategies failed: {e}")
        
        return False

    def _is_submission_action(self) -> bool:
        submission_keywords = [
            "add", "submit", "create", "save", "send", "post",
            "register", "sign up", "login", "log in", "search",
            "go", "continue", "next", "confirm", "apply"
        ]
        description_lower = self.description.lower()
        return any(k in description_lower for k in submission_keywords)