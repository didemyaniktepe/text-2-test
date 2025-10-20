# dom_extractor.py
import json
import logging
from typing import Dict, Any, Tuple
import os
import time
from pathlib import Path

from src.utils.dom_compressor import compress_dom
from src.utils.element_utils import format_elements_for_ai

logger = logging.getLogger(__name__)


async def _freeze_overlays(page) -> None:
    await page.add_style_tag(content="""
      * { animation: none !important; transition: none !important; }
      input, textarea { caret-color: transparent !important; }
    """)
    await page.evaluate("""
      (function(){
        if (window.__overlayFreeze__) return;
        const stop = e => { try { e.stopImmediatePropagation(); } catch(_) {} };
        const events = ['mousedown','mouseup','click','pointerdown','pointerup',
                        'focusout','blur','scroll','wheel','touchstart','touchend'];
        const entries = [];
        for (const ev of events) {
          document.addEventListener(ev, stop, true);
          entries.push([ev, stop]);
        }
        window.__overlayFreeze__ = { entries };
      })();
    """)


async def _unfreeze_overlays(page) -> None:
    await page.evaluate("""
      (function(){
        const f = window.__overlayFreeze__;
        if (!f || !f.entries) return;
        for (const [ev, stop] of f.entries) {
          document.removeEventListener(ev, stop, true);
        }
        delete window.__overlayFreeze__;
      })();
    """)


async def screenshot_preserve_overlays(page, path: str, full_page: bool = True) -> None:
    await _freeze_overlays(page)
    try:
      await page.screenshot(
          path=path,
          full_page=full_page,
          animations="disabled",
          caret="hide",
      )
    finally:
      await _unfreeze_overlays(page)


class DOMExtractor:

    def __init__(self):
        v2_path = os.path.join(os.path.dirname(__file__), "dom_extractor.v2.js")
        self._extractor_v2_js = Path(v2_path).read_text(encoding="utf-8")

        v1_path = os.path.join(os.path.dirname(__file__), "dom_extractors.js")
        self._extractor_v1_js = Path(v1_path).read_text(encoding="utf-8")

    async def _ensure_extractor_v2(self, page) -> None:
        await page.add_init_script(self._extractor_v2_js)
        exists = await page.evaluate("typeof window.__extractPageForPlaywright === 'function'")
        if not exists:
            await page.add_script_tag(content=self._extractor_v2_js)

    async def _ensure_extractor_v1(self, page) -> None:
        await page.add_init_script(self._extractor_v1_js)
        exists = await page.evaluate("typeof extractAllVisibleElements === 'function'")
        if not exists:
            await page.add_script_tag(content=self._extractor_v1_js)

    async def extract_dom_from_page(self, page) -> Tuple[str, str]:
        dom_data_v2 = await self._extract_dom_data_v2(page)
        dom_data_v1 = await self._extract_dom_data_v1(page)

        screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshots_dir, f"debug_screenshot_{int(time.time())}.png")
        try:
            await screenshot_preserve_overlays(page, screenshot_path, full_page=True)
            if not os.path.exists(screenshot_path):
                logger.error(f"Screenshot was not created at {screenshot_path}")
                await page.screenshot(path=screenshot_path, full_page=True)
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            try:
                await page.screenshot(path=screenshot_path, full_page=True)
            except Exception as e2:
                logger.error(f"Fallback screenshot also failed: {str(e2)}")

        dom_data_v2_clean = dom_data_v2.get('domDataV2', []) if dom_data_v2 else []
        compressed = {
            "v2": {
                "domDataV2": dom_data_v2_clean,
            },
            "v1": format_elements_for_ai(dom_data_v1) if dom_data_v1 else None
        }
        compressed_str = json.dumps(compressed, ensure_ascii=False, indent=2)
        return compressed_str, screenshot_path

    async def _extract_dom_data_v1(self, page) -> Dict[str, Any]:
        try:
            await self._ensure_extractor_v1(page)

            title = await page.title()
            meta_description = await page.evaluate("extractMetaDescription()")
            form_elements = await page.evaluate("extractFormElements()")
            interactive_elements = await page.evaluate("extractInteractiveElements()")
            page_structure = await page.evaluate("extractPageStructure()")
            navigation = await page.evaluate("extractNavigation()")
            elements_with_selectors = await page.evaluate("extractElementsWithPlaywrightSelectors()")
            modals_and_popups = await page.evaluate("extractModalsAndPopups()")
            tables = await page.evaluate("extractTables()")
            dynamic_content = await page.evaluate("extractDynamicContent()")
            visible_elements = await page.evaluate("extractAllVisibleElements()")
            return {
                "url": page.url,
                "title": title,
                "meta_description": meta_description,
                "forms": form_elements,
                "interactive_elements": interactive_elements,
                "page_structure": page_structure,
                "navigation": navigation,
                "elements_with_selectors": elements_with_selectors,
                "modals_and_popups": modals_and_popups,
                "tables": tables,
                "dynamic_content": dynamic_content,
                "visible_elements": visible_elements
            }
        except Exception as e:
            logger.error(f"Error during DOM data extraction: {str(e)}")
            raise

    async def _extract_dom_data_v2(self, page) -> Dict[str, Any]:
        try:
            await self._ensure_extractor_v2(page)
            try:
                await page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                logger.warning("Network idle timeout")
            await page.wait_for_timeout(500)  
            
            dom_data_v2 = await page.evaluate(
                """async () => window.__extractPageForPlaywright({
                      onlyInteractives: true,
                      includeHidden: false,
                      waitForTables: true
                   })"""
            )
            return dom_data_v2 or {}
        except Exception as e:
            logger.warning(f"V2 extractor failed: {e}")
            return {}