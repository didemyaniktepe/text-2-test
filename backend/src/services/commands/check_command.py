from .base_command import ActionCommand
import logging

logger = logging.getLogger(__name__)

import logging
from typing import Optional
from playwright.async_api import TimeoutError as PWTimeoutError
from src.utils.locator_resolver import resolve_locator

logger = logging.getLogger(__name__)

async def _is_checked(loc) -> Optional[bool]:
    
    try:
        return await loc.is_checked()
    except Exception:
        try:
            aria = await loc.get_attribute("aria-checked")
            if aria is not None:
                return aria.lower() in ("true", "mixed", "on", "1")
            
            checked_attr = await loc.get_attribute("checked")
            return checked_attr is not None
        except Exception:
            return None  

async def _ensure_checked(loc) -> bool:
    state = await _is_checked(loc)
    if state is True:
        return True

    
    try:
        await loc.check()
    except Exception as e:
        logger.debug(f"loc.check() not supported, fallback to click: {e}")
        try:
            await loc.click()
        except Exception as e2:
            logger.error(f"click fallback failed: {e2}")
            return False

    final = await _is_checked(loc)
    return final is True or final is None  

async def _ensure_unchecked(loc) -> bool:
    state = await _is_checked(loc)
    if state is False:
        return True

    try:
        await loc.uncheck()
    except Exception as e:
        logger.debug(f"loc.uncheck() not supported, fallback to click: {e}")
        try:
            await loc.click()
        except Exception as e2:
            logger.error(f"click fallback failed: {e2}")
            return False

    final = await _is_checked(loc)
    return final is False or final is None

class CheckCommand(ActionCommand):
    async def execute(self) -> bool:
        try:
            if self._should_skip_checkbox_action():
                return False

            loc = await self.get_locator_with_fallback()

            try:
                await loc.wait_for(state="visible", timeout=10000)
            except PWTimeoutError as e:
                logger.warning(f"CheckCommand: not visible yet, continuing: {e}")

            logger.info(f"Checking element: {self.selector}")
            ok = await _ensure_checked(loc)

            await self.post_execute_wait()

            self.executed = True
            self.success = bool(ok)
            if ok:
                logger.info("Successfully ensured checked state")
            else:
                logger.error("Failed to ensure checked state")
            return bool(ok)

        except Exception as e:
            logger.error(f"Check command failed: {e}")
            self.executed = True
            self.success = False
            return False

    def _should_skip_checkbox_action(self) -> bool:
        skip_indicators = [
            "no checkbox", "no visible checkbox", "no checkboxes",
            "no visible checkboxes", "no tasks", "no items"
        ]
        return any(ind in self.description.lower() for ind in skip_indicators)


class UncheckCommand(ActionCommand):
    async def execute(self) -> bool:
        try:
            loc = await self.get_locator_with_fallback()

            try:
                await loc.wait_for(state="visible", timeout=10000)
            except PWTimeoutError as e:
                logger.warning(f"UncheckCommand: not visible yet, continuing: {e}")

            logger.info(f"Unchecking element: {self.selector}")
            ok = await _ensure_unchecked(loc)

            await self.post_execute_wait()

            self.executed = True
            self.success = bool(ok)
            if ok:
                logger.info("Successfully ensured unchecked state")
            else:
                logger.error("Failed to ensure unchecked state")
            return bool(ok)

        except Exception as e:
            logger.error(f"Uncheck command failed: {e}")
            self.executed = True
            self.success = False
            return False