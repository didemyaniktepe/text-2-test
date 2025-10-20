import logging
import re
from .base_command import ActionCommand
from playwright.async_api import Locator


logger = logging.getLogger(__name__)


class SelectCommand(ActionCommand):
    DEFAULT_TIMEOUTS = {
        'element_visible': 1000,
        'element_enabled': 500,
        'scroll_into_view': 500,
        'click': 800,
        'option_visible': 300,
        'option_click': 500,
        'post_select_wait': 50
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeouts = self.DEFAULT_TIMEOUTS.copy()
        
        config_timeouts = kwargs.get('timeouts', {})
        if isinstance(config_timeouts, dict):
            self.timeouts.update(config_timeouts)

    async def execute(self) -> bool:
        try:
            option = self._extract_option_from_description()
            if not option:
                logger.error(f"No option found to select in description: '{self.description}'")
                return False

            loc: Locator = await self.get_locator_with_fallback()
            logger.info(f"Using locator: {loc}")
            
            try:
                tag = await loc.evaluate("el => el.tagName")
                class_name = await loc.evaluate("el => el.className")
                data_attrs = await loc.evaluate("""el => {
                    const attrs = {};
                    for (const attr of el.attributes) {
                        if (attr.name.startsWith('data-')) {
                            attrs[attr.name] = attr.value;
                        }
                    }
                    return attrs;
                }""")
                logger.debug(f"Element details - Tag: {tag}, Class: {class_name}, Data attrs: {data_attrs}")
            except Exception as e:
                logger.debug(f"Failed to get element details: {e}")

            if not await self.validate_selector():
                logger.warning(f"Selector validation failed for: {self.selector}")
                logger.warning("Will attempt to proceed with selection, but this may fail")

            logger.info(f"Attempting to select option '{option}' using selector: {self.selector}")

            is_native = await self._is_native_select(loc)
            logger.debug(f"Element identified as {'native' if is_native else 'custom'} select")

            if '.selectOption(' in self.selector:
                await self._select_on_native(loc, option)
            else:
                if is_native:
                    await self._select_on_native(loc, option)
                else:
                    logger.debug("Attempting custom select handling")
                    await self._open_dropdown_if_needed(loc)
                    selected = await self._select_from_overlay(option)
                    if not selected:
                        logger.debug("Overlay selection failed, trying within-control selection")
                        selected = await self._select_from_within_control(loc, option)
                    if not selected:
                        raise RuntimeError(f"Failed to select option '{option}' - option not found in dropdown")

            await self.post_execute_wait()
            self.executed = True
            self.success = True
            logger.info(f"Successfully selected option '{option}'")
            return True

        except Exception as e:
            logger.error(f"Select command failed for option '{option if 'option' in locals() else 'unknown'}'")
            logger.error(f"Error details: {str(e)}")
            if 'loc' in locals():
                try:
                    is_visible = await loc.is_visible()
                    is_enabled = await loc.is_enabled()
                    logger.error(f"Element state - Visible: {is_visible}, Enabled: {is_enabled}")
                except Exception as e2:
                    logger.error(f"Failed to get element state: {e2}")
            
            self.executed = True
            self.success = False
            return False

    async def _is_native_select(self, loc: Locator) -> bool:
        try:
            tag = await loc.evaluate("el => el.tagName") 
            if (tag or "").lower() == "select":
                return True
            
            role = await loc.evaluate("el => el.getAttribute('role')")
            if role == "combobox":
                tag = await loc.evaluate("el => el.tagName")
                if (tag or "").lower() == "select":
                    return True
                return False
            
            class_name = await loc.evaluate("el => el.className")
            native_select_classes = [
                "single-option-selector",
                "native-select",
                "form-select",
                "select-input"
            ]
            if class_name and any(cls in (class_name or "").lower() for cls in native_select_classes):
                tag = await loc.evaluate("el => el.tagName")
                return (tag or "").lower() == "select"
            
            data_option = await loc.evaluate("el => el.getAttribute('data-option')")
            if data_option and data_option.startswith("option"):
                tag = await loc.evaluate("el => el.tagName")
                return (tag or "").lower() == "select"
                
            if any(cls in (class_name or "").lower() for cls in ["dropdown", "select", "combobox"]):
                return False
                
            return False
        except Exception as e:
            logger.debug(f"Error in _is_native_select: {e}")
            return False

    async def _select_on_native(self, loc: Locator, option_text: str) -> None:
        logger.info(f"Attempting to select '{option_text}' from native select")
        
        try:
            options = await loc.evaluate("""el => {
                return Array.from(el.options).map(opt => ({
                    value: opt.value,
                    text: opt.text,
                    label: opt.label
                }));
            }""")
            logger.debug(f"Available options: {options}")
        except Exception as e:
            logger.debug(f"Failed to get available options: {e}")
            options = []
        
        try:
            await loc.select_option(label=option_text)
            logger.info(f"Successfully selected by exact label: {option_text}")
            return
        except Exception as e1:
            logger.debug(f"select_option by exact label failed: {e1}")
        
        for value in [option_text, option_text.lower()]:
            try:
                await loc.select_option(value=value)
                logger.info(f"Successfully selected by value: {value}")
                return
            except Exception as e2:
                logger.debug(f"select_option by value failed for '{value}': {e2}")
        
        try:
            data_option = await loc.evaluate("el => el.getAttribute('data-option')")
            if data_option:
                await loc.select_option({"data-option": data_option})
                logger.info(f"Successfully selected by data-option: {data_option}")
                return
        except Exception as e3:
            logger.debug(f"select_option by data-option failed: {e3}")
        
        try:
            await loc.select_option(label=option_text.lower())
            logger.info(f"Successfully selected by case insensitive label: {option_text.lower()}")
            return
        except Exception as e4:
            logger.debug(f"select_option by case insensitive label failed: {e4}")
        
        try:
            await loc.select_option(label=option_text, exact=False)
            logger.info(f"Successfully selected by partial label: {option_text}")
            return
        except Exception as e5:
            logger.debug(f"select_option by partial label failed: {e5}")
        
        try:
            await loc.select_option(option_text)
            logger.info(f"Successfully selected by direct text: {option_text}")
            return
        except Exception as e6:
            error_msg = f"All select_option methods failed. Available options were: {options}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e6

    async def _open_dropdown_if_needed(self, loc: Locator) -> None:
        await loc.wait_for(state="visible", timeout=self.timeouts['element_visible'])
        try:
            await loc.scroll_into_view_if_needed(timeout=self.timeouts['scroll_into_view'])
        except Exception:
            pass
        try:
            await loc.focus()
        except Exception:
            pass
        
        try:
            is_open = await loc.evaluate("el => el.getAttribute('aria-expanded') === 'true'")
            if is_open:
                logger.info("Dropdown already open")
                return
        except Exception:
            pass
            
        try:
            await loc.click(timeout=self.timeouts['click'])
            await self.page.wait_for_timeout(self.timeouts['post_select_wait'])
        except Exception as e1:
            logger.debug(f"open click failed, retrying after scroll: {e1}")
            try:
                await loc.scroll_into_view_if_needed(timeout=self.timeouts['scroll_into_view'])
                await loc.click(timeout=self.timeouts['click'])
                await self.page.wait_for_timeout(self.timeouts['post_select_wait'])
            except Exception as e2:
                logger.debug(f"second open click failed, force clicking: {e2}")
                await loc.click(timeout=self.timeouts['click'], force=True)
                await self.page.wait_for_timeout(self.timeouts['post_select_wait'])

    async def _select_from_overlay(self, option_text: str) -> bool:
        page = self.page
        exact = option_text

        try:
            await page.wait_for_timeout(self.timeouts['post_select_wait'])
        except Exception:
            pass

        candidates = [
            page.get_by_role("option", name=exact),
            page.get_by_role("menuitem", name=exact),
            page.get_by_text(exact, exact=True),
            page.locator("[role='listbox'] [role='option']").filter(has_text=re.compile(rf"^{re.escape(exact)}$")),
            page.locator(".p-dropdown-panel .p-dropdown-items .p-dropdown-item").get_by_text(exact, exact=True),
            page.locator(".p-multiselect-panel .p-multiselect-items .p-multiselect-item").get_by_text(exact, exact=True),
            page.locator(".MuiPopover-root .MuiList-root [role='option']").get_by_text(exact, exact=True),
            page.locator(".ant-select-dropdown [role='option'], .ant-select-item-option-content").get_by_text(exact, exact=True),
            page.locator("[role='combobox'] + [role='listbox'] [role='option']").get_by_text(exact, exact=True),
            page.locator(".dropdown-menu, .dropdown-content").get_by_text(exact, exact=True),
            page.locator("[data-testid*='option'], [data-testid*='item']").get_by_text(exact, exact=True),
            page.locator(".single-option-selector option").filter(has_text=re.compile(rf"^{re.escape(exact)}$")),
        ]

        for cand in candidates:
            try:
                target = cand.first
                await target.wait_for(state="visible", timeout=self.timeouts['option_visible'])
                await target.scroll_into_view_if_needed(timeout=self.timeouts['scroll_into_view'])
                await target.hover()
                await target.click(timeout=self.timeouts['option_click'])
                logger.info(f"Successfully selected option '{exact}' with selector: {cand}")
                return True
            except Exception as e:
                logger.debug(f"Failed to select with candidate: {e}")
                continue
        return False

    async def _select_from_within_control(self, loc: Locator, option_text: str) -> bool:
        try:
            option = loc.locator(f"text={option_text}")
            await option.first.wait_for(state="visible", timeout=self.timeouts['option_visible'])
            await option.first.click(timeout=self.timeouts['option_click'])
            return True
        except Exception as e:
            logger.debug(f"Failed to select from within control: {e}")
            return False

    def _extract_option_from_description(self) -> str:
        text = self.description

        q = re.findall(r"['\"]([^'\"]+)['\"]", text)
        if q:
            opt = q[-1].strip()
            opt = re.sub(r"^size\s+", "", opt, flags=re.IGNORECASE)
            logger.info(f"Extracted option (quoted): '{opt}'")
            return opt

        m = re.search(
            r"(?:select|choose|pick|seç)\s+['\"]?(.+?)['\"]?\s+(?:from|in|on|under)\s+['\"]?.+?['\"]?",
            text, re.IGNORECASE
        )
        if m:
            opt = m.group(1).strip()
            if opt:
                opt = re.sub(r"^size\s+", "", opt, flags=re.IGNORECASE)
                logger.info(f"Extracted option (from/in-pattern): '{opt}'")
                return opt

        m2 = re.search(r"(?:select|choose|pick|seç)\s+(.+)$", text, re.IGNORECASE)
        if m2:
            opt = m2.group(1).strip()
            opt = re.split(r"\s+(?:from|in|on|under)\s+", opt, flags=re.IGNORECASE)[0].strip()
            if opt:
                opt = re.sub(r"^size\s+", "", opt, flags=re.IGNORECASE)
                logger.info(f"Extracted option (simple): '{opt}'")
                return opt

        logger.warning(f"No option extracted from: '{self.description}'")
        return ""
