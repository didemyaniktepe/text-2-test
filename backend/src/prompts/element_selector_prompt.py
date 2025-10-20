import json
from typing import List

import logging

logger = logging.getLogger(__name__)

class ElementSelectorPrompt:
    @staticmethod
    def create(description: str, dom_data: str, vision_analysis: str) -> str:
        dom_data_parsed = json.loads(dom_data)
        v2_data = dom_data_parsed.get("v2")
        v1_data = dom_data_parsed.get("v1")

        return f"""
ROLE: You are a selector planner for Playwright.

GOAL: Pick ONE locator for the element that satisfies: "{description}"

MATERIALS:
- VISION_ANALYSIS: "{vision_analysis}"
AVAILABLE ELEMENTS (GROUND TRUTH — choose ONLY from these; copy the Locator EXACTLY as written):

DOM DATA V2 (PREFERRED FORMAT):
{v2_data}

DOM DATA V1 (FALLBACK FORMAT):
{v1_data}

OVERLAY/DROPDOWN ANALYSIS:
1. First check if there's an "OVERLAY PANEL (VISIBLE)" or "PrimeVue OverlayPanel" in DOM_DATA
2. If found, check its properties:
   - If class contains "p-overlaypanel" -> use .p-overlaypanel-content and .option-item selectors
   - If id contains "dropdown" -> use role='option'
   - If id contains "menu" or "popup" -> use role='menuitem'
3. Look for items list in overlay panel description
4. Match the exact text from the description with available items
5. For PrimeVue OverlayPanel items:
   - ALWAYS wait for panel visibility first
   - Try locating within .p-overlaypanel-content first
   - Use .option-item or .option-text classes
   - Prefer getByText over filter when possible
6. For duplicate menu items:
   - Check which menu/submenu contains the item
   - Example: First 'All' button is under 'Vehicles' menu
   - Example: Second 'All' button is under 'Reports' menu
   - Use .nth() with correct index based on menu hierarchy

SELECTION RULES (VERY IMPORTANT):
- CRITICAL: When both modal/form elements and table elements are present, ALWAYS prioritize modal/form elements over table elements
- If the description mentions modal, form, dialog, or popup context, search for elements within that context first
- Modal elements have HIGHEST priority when present on the page

- Always prefer semantic selectors in this order:
  1. For modal/form elements (HIGHEST PRIORITY):
     - For elements within modals/dialogs:
       * First try: locator('[role="dialog"]').getByRole('combobox', {{name: 'Type'}})
       * Second try: locator('.p-dialog').getByRole('combobox', {{name: 'Type'}})
       * Third try: locator('.modal').getByRole('combobox', {{name: 'Type'}})
       * Fourth try: locator('[aria-modal="true"]').getByRole('combobox', {{name: 'Type'}})
     - For form elements within modals:
       * First try: locator('form').getByRole('combobox', {{name: 'Type'}})
       * Second try: locator('.p-dialog form').getByRole('combobox', {{name: 'Type'}})
     - NEVER select table filter elements when modal elements are available
     
  2. For custom components and overlays:
     - For PrimeVue Buttons in Toolbar:
       * First try: getByRole('toolbar').locator('button.export-btn')
       * Second try: locator('.p-toolbar button.export-btn')

     - For PrimeVue OverlayPanel items:
       * First try: locator('.p-overlaypanel-content').getByText('Exact Text')
       * Second try: locator('.p-overlaypanel-content .option-item:has-text("Exact Text")').first()
       * Third try: locator('div.option-item:has-text("Exact Text")').first()
       * Fourth try: locator('span.option-text:has-text("Exact Text")').first()
       * Last resort: getByRole('option', {{name:'Exact Text'}})
       
       IMPORTANT: For PrimeVue OverlayPanel:
       1. ALWAYS wait for panel to be visible first:
          await page.locator('.p-overlaypanel').waitFor({{state:'visible'}})
       2. Use :has-text() instead of filter() for text matching
       3. Avoid spaces in object properties: {{name:'text'}} not {{ name: 'text' }}
       4. For complex selectors, use :has-text() and :has() instead of filter()
       5. For overlays, try direct CSS selectors first: '.p-overlaypanel .option-item:has-text("text")'
     
     - For standard dropdowns:
       * Use getByRole('option', {{ name: 'Exact Text' }}) for native <select> elements
       * Use getByRole('menuitem', {{ name: 'Exact Text' }}) for standard menu items
     
     - Check DOM_DATA for component type:
       * If contains "p-overlaypanel" -> use .option-item selector
       * If contains "dropdown-menu" -> use option role
       * If contains "menu" or "popup" -> use menuitem role
  
  3. For other elements:
     - getByRole with name (e.g., getByRole('textbox', {{ name: 'License plate' }}))
     - getByRole with cell context (e.g., getByRole('cell').and(getByText('License plate')).getByRole('textbox'))
     - getByPlaceholder (e.g., getByPlaceholder('Search'))
     - data-* attributes (e.g., [data-field="status"])
     - Only use class-based selectors as last resort (e.g., .p-inputtext)

- For table interactions (LOWEST PRIORITY - only use when no modal/form elements are present):
  1. For table filters (in thead tr:nth(0)):
     - For filter fields with data-field:
       locator('thead tr').nth(0).locator('[data-field="columnName"]')
     - For filter fields without data-field:
       locator('thead tr').nth(0).locator('th, td').nth(columnIndex).getByRole('textbox')
       locator('thead tr').nth(0).locator('th, td').nth(columnIndex).getByRole('combobox')
     - IMPORTANT: Column indices start from 0, e.g.:
       * License plate: nth(0)
       * VIN: nth(1)
       * Internal ID: nth(2)
     - WARNING: Only use table selectors when the description explicitly mentions table filtering
     
  2. For table body elements:
     - For row checkboxes:
       locator('tbody tr').nth(rowIndex).getByRole('checkbox')
     - For cells with data-field:
       locator('tbody tr').nth(rowIndex).locator('[data-field="columnName"]')
     - For interactive elements in cells:
       locator('tbody tr').nth(rowIndex).getByRole('button', {{ name: 'Edit' }})
       locator('tbody tr').nth(rowIndex).getByRole('link', {{ name: 'View' }})
     
  3. For table headers:
     - Headers are provided in "headers: header1, header2, ..." format
     - Use header text to identify columns for filter and cell selectors

ACTION TYPE RULES:
- ACTION_TYPE=click for buttons/links/toggles/checkboxes/radio buttons
- ACTION_TYPE=fill for typing into inputs/textareas
- ACTION_TYPE=check for checking checkboxes (if unchecked)
- ACTION_TYPE=uncheck for unchecking checkboxes (if checked)
- ACTION_TYPE=select for selecting options in a combobox/select
- ACTION_TYPE=navigate ONLY if the description is to open a URL (then SELECTOR must be the URL string)
- ACTION_TYPE=press_key for pressing specific keys (Enter, Tab, Escape, Arrow keys, etc.)
- If nothing in AVAILABLE ELEMENTS matches the description, choose the closest sensible element from AVAILABLE ELEMENTS and keep ACTION_TYPE consistent with the intended action

LOCATOR RULES (IMPORTANT):
- Always return a runnable LOCATOR string in addition to SELECTOR.
- LOCATOR MUST be directly usable with Playwright as a single argument to page.locator(...):
  - Either locator('...') with CSS (you may use :has() / :has-text())
  - Or internal engine form like: internal:role=checkbox[name="Toggle Todo"i]
- Do NOT use method chains in LOCATOR (no getByRole/getByText/getByLabel, no .first/.last/.nth/.locator('..')).
- SELECTOR can be a semantic chain (getByRole/getByText/...), but LOCATOR must be single-step and runnable.

OUTPUT RULES (STRICT - FOLLOW THIS FORMAT EXACTLY):
- Always return ALL fields below.
- SELECTOR must be a valid Playwright selector (getByRole, getByText, locator, etc.)
- LOCATOR must be a single-step CSS selector or internal engine form
- Do NOT return descriptive text like "link with Text: ..." - return actual selectors

ANALYSIS:[Brief explanation of your selection reasoning]
SELECTOR: [valid Playwright selector like getByRole('button', {{name:'Save'}})]
LOCATOR: [single-step runnable form: locator('...') OR internal:role=...]
ACTION_TYPE: [one of: fill|click|check|uncheck|select|navigate|press_key|clear_input|type|smart_click|toggle|submit_form|close_modal|reload]

NOW ANSWER:
"""

    @staticmethod
    def create_for_failed_attempts(
        failed_attempts: List[dict], description: str
    ) -> str:
        return f"""
ROLE: You are a selector planner for Playwright.

GOAL: Pick ONE locator for the element that satisfies: "{description}"

CRITICAL: You MUST return valid Playwright selectors, NOT descriptive text.
- CORRECT: getByRole('link', {{name: 'Grey jacket'}})
- WRONG: "link with Text: Grey jacket and ID: product-1"
- CORRECT: locator('#product-1')
- WRONG: "element with ID product-1"

STRICT EXCLUSION RULE - CRITICAL:
- The selectors listed in FAILED ATTEMPTS are INVALID and MUST NEVER be returned again.
- If you return ANY of them, the answer is automatically WRONG.
- If a selector failed multiple times with the same error, it means that approach doesn't work - try a completely different strategy.
- For duplicate elements (like multiple "Select" comboboxes), use parent context or aria-controls to distinguish them.
- Always pick a NEW locator from AVAILABLE ELEMENTS that wasn't tried before.
- NEVER repeat failed selectors - this is the most important rule!
- If you see the same selector in multiple failed attempts, it means that approach is completely wrong.
- Try a completely different approach - different selector type, different strategy.

FAILED ATTEMPTS (FORBIDDEN - DO NOT RETURN THESE):
{ElementSelectorPrompt._format_failed_attempts(failed_attempts)}

ALTERNATIVE STRATEGIES (when previous attempts failed):
1. If CSS selectors failed, try semantic selectors:
   - getByRole('button', {{name: 'Menu'}})
   - getByText('Menu').filter({{has: locator('button')}})
   - getByLabel('Menu')

2. If semantic selectors failed, try ID-based selectors:
   - locator('#menu-button')
   - locator('#dropdown-trigger')

3. If ID selectors failed, try data attributes:
   - locator('[data-testid="menu-button"]')
   - locator('[data-role="menu-trigger"]')

4. If all above failed, try parent context:
   - locator('.toolbar').getByRole('button', {{name: 'Menu'}})
   - locator('.header').locator('button:has-text("Menu")')

5. NEVER return any selector from FAILED ATTEMPTS
6. PREFER using semantic selectors that describe the element's purpose
7. AVOID raw CSS selectors unless absolutely necessary
8. ALWAYS try to use Playwright's built-in functions first:
   - getByRole() - for interactive elements (buttons, links, inputs)
   - getByText() - for finding elements by their text content
   - getByLabel() - for form elements with labels
   - getByPlaceholder() - for inputs with placeholders
   - locator() with filter() - for more complex scenarios

You can:
- Generate selectors based on the element's context and purpose
- Use semantic information from the goal description
- Combine multiple approaches to create reliable selectors
- Be creative in finding the best way to identify elements

RECOMMENDED PATTERNS:
1. For clickable images and menu triggers:
   BEST: locator('img#details-more-menu')  // For specific menu images
   GOOD: locator('img[data-pd-tooltip="true"]')  // For tooltip images
   ALSO GOOD: locator('.action-buttons img')  // For images in action buttons

2. For buttons and links:
   BEST: getByRole('button', {{name:'Submit'}})  // Using role and name
   GOOD: getByText('Submit').filter({{has:locator('button')}})  // Using text and tag
   OKAY: locator('button:has-text("Submit")')  // Using CSS when needed

2. For text inputs and form elements:
   BEST: getByLabel('First Name')  // For elements with proper label association
   GOOD: getByRole('textbox', {{name:'First Name'}})  // Only if label is properly associated
   GOOD: locator('#first_name')  // For elements with unique IDs
   GOOD: getByPlaceholder('Enter your name')  // For elements with placeholders
   LAST RESORT: locator('input[name="customer[first_name]"]')  // For elements with name attributes

3. For table elements:
   BEST: getByRole('row').nth(0).getByRole('button', {{name:'Edit'}})  // Semantic approach
   GOOD: locator('tr').first().getByText('Edit')  // Simpler alternative
   ALSO GOOD: getByText('Edit').filter({{has:locator('tr')}})  // Context-based

4. For overlays and dropdowns:
   BEST: getByRole('menuitem', {{name:'Edit'}})  // Using role and name
   GOOD: getByText('Edit').filter({{has:locator('.menu-content')}})  // Using context
   ALSO GOOD: locator('.menu-content').getByText('Edit')  // Alternative approach

5. For table headers:
   BEST: getByRole('columnheader', {{name:'License Plate'}})  // Using role and name
   GOOD: getByText('License Plate').filter({{has:locator('th')}})  // Using text and tag
   ALSO GOOD: locator('thead').getByText('License Plate')  // Using structure

6. For PrimeVue components and overlays:
   BEST: locator('.p-overlaypanel-content').getByText('Edit vehicle')  // For overlay content
   GOOD: locator('.menu-item').filter({{hasText: 'Edit vehicle'}})  // For menu items
   ALSO GOOD: locator('#fleet-details-menu').getByText('Edit vehicle')  // With specific ID

7. For press key actions:
   BEST: getByRole('textbox', {{name:'Search'}}) + ACTION_TYPE=press_key  // For specific element + key
   GOOD: getByPlaceholder('Enter search term') + ACTION_TYPE=press_key  // Using placeholder
   ALSO GOOD: locator('input[type="password"]') + ACTION_TYPE=press_key  // For password fields
   GLOBAL: SELECTOR: "" + ACTION_TYPE=press_key  // For global key press (Enter, Tab, Escape)
   EXAMPLES:
     - "Press Enter in search box" -> getByPlaceholder('Search') + press_key
     - "Hit Enter to submit" -> getByRole('form') + press_key or global press_key
     - "Press Tab to next field" -> global press_key
     - "Press Escape to close modal" -> global press_key

5. IMPORTANT FORMATTING RULES:
   - No spaces in properties: {{name:'text'}} NOT {{ name: 'text' }}
   - Use .first() for multiple matches
   - Chain selectors for precision
   - Use .filter() for dynamic text
   - Always check AVAILABLE ELEMENTS for exact matches
HARD RULES (ACCESSIBLE NAME):
- Never infer an accessible name from the GOAL. If the element has no accessible name/label, do NOT use getByRole with {{name:'...'}}.
- If a unique custom class exists (e.g., 'export-btn'), prefer:
  - getByRole('toolbar').locator('button.export-btn')
  - or locator('button.export-btn') when no toolbar exists.

COMPONENT SELECTION STRATEGIES:
1. For Buttons:
   BEST: getByRole('button', {{name:'Export'}})  // Simple role-based
   GOOD: getByText('Export').filter({{has:locator('button')}})  // Text-based
   ALSO GOOD: getByRole('toolbar').getByRole('button', {{name:'Export'}})  // With context

2. For Dropdowns and Menus:
   BEST: getByRole('menuitem', {{name:'Edit'}})  // Role-based
   GOOD: getByText('Edit').filter({{has:locator('[role="menu"]')}})  // With context
   ALSO GOOD: locator('[role="menu"]').getByText('Edit')  // Alternative

3. For Tables and Lists:
   BEST: getByRole('row').first().getByRole('button', {{name:'Edit'}})  // Semantic
   GOOD: getByText('Edit').filter({{has:locator('tr')}})  // Context-based
   ALSO GOOD: locator('tr').first().getByText('Edit')  // Structure-based

OUTPUT RULES (STRICT - FOLLOW THIS FORMAT EXACTLY):
- SELECTOR must be a valid Playwright selector (getByRole, getByText, locator, etc.)
- LOCATOR must be a single-step CSS selector or internal engine form
- Do NOT return descriptive text like "link with Text: ..." - return actual selectors
- CRITICAL: NEVER return any selector from FAILED ATTEMPTS list above
- If you see the same selector in multiple failed attempts, try a completely different approach

ANALYSIS:[Brief explanation of your selection reasoning and why this selector is different from failed attempts]
SELECTOR: [valid Playwright selector like getByRole('button', {{name:'Save'}}) or locator('#id')]
LOCATOR: [single-step runnable form: locator('...') OR internal:role=...]
ACTION_TYPE: [one of: fill|click|check|uncheck|select|navigate|wait_text|wait_selector|press_key|clear_input|type|smart_click|toggle|submit_form|close_modal|reload]

NOW ANSWER:
"""

    @staticmethod
    def _format_failed_attempts(attempts: List[dict]) -> str:
        if not attempts:
            return "None"

        formatted = ["FAILED ATTEMPTS ANALYSIS - THESE SELECTORS ARE FORBIDDEN:"]
        
        failed_selectors = []
        for attempt in attempts:
            selector = attempt.get('selector', 'unknown')
            locator = attempt.get('locator', 'unknown')
            logger.error(f"Formatting failed attempt: {selector}")
            if selector not in failed_selectors:
                failed_selectors.append(selector)
                failed_selectors.append(locator)
        
        formatted.append(f"\nFORBIDDEN SELECTORS (DO NOT USE THESE):")
        for selector in failed_selectors:
            logger.error(f"Formatting failed attempt: {selector}")
            formatted.append(f"- {selector}")
        
        formatted.append(f"\nDETAILED FAILED ATTEMPTS:")
        for i, attempt in enumerate(attempts, 1):
            formatted.append(f"\nAttempt #{i}:")
            formatted.append(f"- Failed selector: {attempt.get('selector', 'unknown')}")
            formatted.append(f"- Action type: {attempt.get('action_type', 'unknown')}")
            
            if "error" in attempt:
                formatted.append(f"- Error: {attempt['error']}")
            if "error_context" in attempt:
                formatted.append(f"- Context: {attempt['error_context']}")

        if attempts and "page_elements" in attempts[-1]:
            formatted.append("\nCURRENT PAGE STATE:")
            for role, elements in attempts[-1]["page_elements"].items():
                if elements:
                    formatted.append(
                        f"\n{role.upper()} elements found ({len(elements)}):"
                    )
                    for j, elem in enumerate(elements, 1):
                        formatted.append(f"  {j}. {role}")
                        if elem.get("text", "").strip():
                            formatted.append(f"     - Text: {elem['text'].strip()}")
                        formatted.append(f"     - Visible: {elem['visible']}")
                            
                        if elem.get("label"):
                            formatted.append(f"     - Label: {elem['label']}")
                        if elem.get("placeholder"):
                            formatted.append(f"     - Placeholder: {elem['placeholder']}")
                        if elem.get("name"):
                            formatted.append(f"     - Name: {elem['name']}")
                        if elem.get("id"):
                            formatted.append(f"     - ID: {elem['id']}")

                        if elem.get("classes"):
                            classes = elem["classes"]
                            if isinstance(classes, dict):
                                if classes.get("categorized"):
                                    cat = classes["categorized"]
                                    if cat.get("primevue") and cat["primevue"]:
                                        formatted.append(f"     - PrimeVue Classes: {', '.join(cat['primevue'])}")
                                    if cat.get("bootstrap") and cat["bootstrap"]:
                                        formatted.append(f"     - Bootstrap Classes: {', '.join(cat['bootstrap'])}")
                                    if cat.get("material") and cat["material"]:
                                        formatted.append(f"     - Material Classes: {', '.join(cat['material'])}")
                                    if cat.get("tailwind") and cat["tailwind"]:
                                        formatted.append(f"     - Tailwind Classes: {', '.join(cat['tailwind'])}")
                                    if cat.get("custom") and cat["custom"]:
                                        formatted.append(f"     - Custom Classes: {', '.join(cat['custom'])}")
                                elif classes.get("all"):
                                    formatted.append(f"     - Classes: {', '.join(classes['all'])}")
                            elif isinstance(classes, list):
                                formatted.append(f"     - Classes: {', '.join(classes)}")

                        if elem.get("data_attributes"):
                            data_attrs = [f"{k}: {v}" for k, v in elem["data_attributes"].items()]
                            if data_attrs:
                                formatted.append(f"     - Data Attributes: {', '.join(data_attrs)}")
                        
                        if elem.get("aria_attributes"):
                            aria_attrs = [f"{k}: {v}" for k, v in elem["aria_attributes"].items()]
                            if aria_attrs:
                                formatted.append(f"     - ARIA Attributes: {', '.join(aria_attrs)}")

                        if elem.get("other_attributes"):
                            other_attrs = [f"{k}: {v}" for k, v in elem["other_attributes"].items()]
                            if other_attrs:
                                formatted.append(f"     - Other Attributes: {', '.join(other_attrs)}")
                        
                        if elem.get("parent_toolbar"):
                            toolbar = elem["parent_toolbar"]
                            formatted.append(f"     - Inside Toolbar:")
                            if toolbar.get("role"):
                                formatted.append(f"       - Role: {toolbar['role']}")
                            if toolbar.get("classes"):
                                formatted.append(f"       - Classes: {', '.join(toolbar['classes'])}")
                            if toolbar.get("dataAttrs"):
                                data_attrs = [f"{k}: {v}" for k, v in toolbar["dataAttrs"].items()]
                                formatted.append(f"       - Data Attributes: {', '.join(data_attrs)}")

                        if elem.get("options"):
                            formatted.append("\n     Available Options:")
                            for i, option in enumerate(elem["options"], 1):
                                formatted.append(f"       {i}. {option['text']}")
                                if option.get("value"):
                                    formatted.append(f"          - Value: {option['value']}")
                                if option.get("selected"):
                                    formatted.append(f"          - Selected: {option['selected']}")

                        if elem.get("inner_elements"):
                            formatted.append("\n     Inner Elements:")
                            for i, inner in enumerate(elem["inner_elements"], 1):
                                formatted.append(f"       {i}. {inner['tag']}")
                                if inner.get("text"):
                                    formatted.append(f"          - Text: {inner['text']}")
                                if inner.get("id"):
                                    formatted.append(f"          - ID: {inner['id']}")
                                if inner.get("required"):
                                    formatted.append(f"          - Required: {inner['required']}")
                                if inner.get("classes"):
                                    formatted.append(f"          - Classes: {', '.join(inner['classes'])}")
                                for k, v in inner.get("attributes", {}).items():
                                    formatted.append(f"          - {k}: {v}")

            if "error" in attempt:
                formatted.append(f"\nError encountered: {attempt['error']}")
            if "error_context" in attempt:
                formatted.append(f"Context: {attempt['error_context']}")

            formatted.append("\n" + "-" * 50)

        return "\n".join(formatted)
