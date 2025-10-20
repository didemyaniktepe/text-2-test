import logging
import re
from typing import Any, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)
@dataclass
class TableElement:
    role: str
    name: str
    action: str
    selector: str
    tooltip: bool = False
    popup: bool = False
    menu_id: str = None
    element_type: str = None
    attributes: dict = None

@dataclass
class TableData:
    headers: List[str]
    filters: List[TableElement]
    row_checkboxes: List[TableElement]
    cells: List[TableElement]
    other_elements: List[TableElement]

    @staticmethod
    def parse(table_str: str) -> 'TableData':
        headers = []
        filters = []
        row_checkboxes = []
        cells = []
        other_elements = []
        
        for line in table_str.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('headers:'):
                headers = [h.strip() for h in line.replace('headers:', '').split(',')]
                continue
                
            parts = line.split(' | ')
            if len(parts) < 4:
                continue
                
            role = parts[0]
            name = parts[1]
            action = parts[2]
            selector = parts[3]
            
            attributes = {}
            tooltip = False
            popup = False
            menu_id = None
            element_type = None
            
            if role == 'img' and 'action-buttons' in selector:
                element_type = 'img'
                if 'data-pd-tooltip' in selector:
                    tooltip = True
                    attributes['data-pd-tooltip'] = 'true'
                if 'aria-controls' in name:
                    popup = True
                    menu_id = name.split("'")[1] if "'" in name else None
            
            element = TableElement(
                role=role,
                name=name,
                action=action,
                selector=selector,
                tooltip=tooltip,
                popup=popup,
                menu_id=menu_id,
                element_type=element_type,
                attributes=attributes if attributes else None
            )
            
            if '(filter)' in name:
                filters.append(element)
            elif role == 'checkbox' and 'row' in name:
                row_checkboxes.append(element)
            elif 'row' in name:
                cells.append(element)
            else:
                other_elements.append(element)
        
        return TableData(
            headers=headers,
            filters=filters,
            row_checkboxes=row_checkboxes,
            cells=cells,
            other_elements=other_elements
        )
    
    def format(self) -> str:
        lines = []
        
        if self.headers:
            lines.append("\nTABLE HEADERS:")
            lines.append(f"headers: {', '.join(self.headers)}")
        
        if self.filters:
            lines.append("\nFILTER ELEMENTS:")
            for el in self.filters:
                lines.append(f"{el.role} | {el.name} | {el.action} | {el.selector}")
        
        if self.row_checkboxes:
            lines.append("\nROW CHECKBOXES:")
            for el in self.row_checkboxes:
                lines.append(f"{el.role} | {el.name} | {el.action} | {el.selector}")
        
        if self.cells:
            lines.append("\nTABLE CELLS AND INTERACTIVE ELEMENTS:")
            for el in self.cells:
                parts = [el.role]
                
                if el.element_type == 'img' and el.tooltip:
                    parts[0] = 'MENU ICON'
                    if el.tooltip:
                        parts.append('has tooltip')
                    if el.popup:
                        parts.append('has popup menu')
                    if el.menu_id:
                        parts.append(f"controls: '{el.menu_id}'")
                
                parts.extend([el.name, el.action, el.selector])
                lines.append(" | ".join(parts))
        
        if self.other_elements:
            lines.append("\nOTHER TABLE ELEMENTS:")
            for el in self.other_elements:
                parts = [el.role]
                
                if el.element_type == 'img' and el.tooltip:
                    parts[0] = 'MENU ICON'
                    if el.tooltip:
                        parts.append('has tooltip')
                    if el.popup:
                        parts.append('has popup menu')
                    if el.menu_id:
                        parts.append(f"controls: '{el.menu_id}'")
                
                parts.extend([el.name, el.action, el.selector])
                lines.append(" | ".join(parts))
        
        return "\n".join(lines)

def format_elements_for_ai(dom_data: dict) -> str:
    interactive_elements = dom_data.get('interactive_elements', [])[:50]
    visible_elements = dom_data.get('visible_elements', {})
    dynamic_content = dom_data.get('dynamic_content', {}) 
    tables = dom_data.get('tables', {})
    forms = dom_data.get('forms', [])
    
    formatted_sections = []
    
    if forms:
        forms_section = _format_form_elements(forms)
        formatted_sections.append(forms_section)
    
    if dynamic_content:
        dynamic_section = _format_dynamic_content(dynamic_content)
        formatted_sections.append(dynamic_section)
        
    if interactive_elements:
        interactive_section = _format_interactive_elements(interactive_elements)
        formatted_sections.append(interactive_section)
    
    visible_section = _format_visible_elements(visible_elements)
    if visible_section:
        formatted_sections.append(visible_section)
        
    if tables:
        tables_section = _format_tables(tables)
        formatted_sections.append(tables_section)
    
    return "\n".join(formatted_sections) if formatted_sections else "No interactive elements found"

def _format_interactive_elements(elements: list) -> str:
    formatted = ["INTERACTIVE ELEMENTS:"]
    for i, elem in enumerate(elements, 1):
        element_description = _format_single_element(elem, i)
        formatted.append(element_description)
    return "\n".join(formatted)

def _format_single_element(elem: dict, index: int) -> str:
    if isinstance(elem, str):
        return f"{index}. {elem}"
        
    elem_type = elem.get('type', 'unknown') or 'unknown'
    role = (elem.get('role') or elem_type or 'unknown').upper()
    
    if (role == 'IMG' or 'img' in str(elem.get('selector', '')).lower()) and \
       any(key in str(elem.get('selector', '')).lower() for key in ['action-buttons', 'data-pd-tooltip']):
        desc_parts = [f"{index}. MENU ICON"]
        if elem.get('tooltip'):
            desc_parts.append('has tooltip')
        if elem.get('popup'):
            desc_parts.append('has popup menu')
        if elem.get('menuId'):
            desc_parts.append(f"controls: '{elem.get('menuId')}'")
    else:
        desc_parts = [f"{index}. {role}"]
    
    text = elem.get('text', '')
    input_type = elem.get('inputType', '')
    label = elem.get('label', '')
    
    if elem.get('expanded'):
        desc_parts.append("EXPANDED")
    if elem.get('disabled'):
        desc_parts.append("DISABLED")

    if elem.get('frameworks'):
        frameworks = elem.get('frameworks', {})
        for fw_name, fw_classes in frameworks.items():
            if fw_classes and len(fw_classes) > 0:
                desc_parts.append(f"{fw_name}: {', '.join(fw_classes)}")
        if frameworks.get('custom'):
            desc_parts.append(f"custom: {', '.join(frameworks['custom'])}")

    contexts = []
    if elem.get('inToolbar'):
        contexts.append(f"toolbar-{elem.get('section')}" if elem.get('section') else 'toolbar')
    if elem.get('inMenu'):
        contexts.append('menu')
    if elem.get('inNavigation'):
        contexts.append('navigation')
    if elem.get('inForm'):
        contexts.append('form')
    if elem.get('inDialog'):
        contexts.append('dialog')
    if contexts:
        desc_parts.append(f"context: {' > '.join(contexts)}")

    if elem.get('hasIcon'):
        icon_info = []
        if elem.get('iconType'):
            icon_info.append(elem.get('iconType'))
        desc_parts.append(f"icon: {', '.join(icon_info)}")
    if elem.get('tooltip'):
        desc_parts.append(f"tooltip: '{elem.get('tooltip')}'")

    if elem.get('actions'):
        actions = [action for action, is_active in elem['actions'].items() if is_active]
        if actions:
            desc_parts.append(f"action: {', '.join(actions)}")

    if elem.get('importance'):
        importance = [level for level, is_active in elem['importance'].items() if is_active]
        if importance:
            desc_parts.append(f"importance: {', '.join(importance)}")

    if elem.get('ariaAttributes'):
        aria_attrs = [f"{k}: {v}" for k, v in elem['ariaAttributes'].items()]
        if aria_attrs:
            desc_parts.append(f"aria: {', '.join(aria_attrs)}")
    if elem.get('dataAttributes'):
        data_attrs = [f"{k}: {v}" for k, v in elem['dataAttributes'].items()]
        if data_attrs:
            desc_parts.append(f"data: {', '.join(data_attrs)}")

    if elem.get('selectors'):
            selectors = elem['selectors']
            if isinstance(selectors, list) and all(isinstance(s, dict) for s in selectors):
                best_selector = None
                
                if elem.get('inToolbar'):
                    toolbar_selectors = [s for s in selectors if s.get('type') in ['toolbar-custom', 'toolbar-button']]
                    if toolbar_selectors:
                        best_selector = toolbar_selectors[0]['selector']
                    elif elem.get('frameworks', {}).get('custom'):
                        custom_class = elem['frameworks']['custom'][0]
                        best_selector = f"getByRole('toolbar').locator('button.{custom_class}')"
                
                elif elem.get('inNavigation'):
                    nav_selectors = [s for s in selectors if s.get('type') == 'nav-custom']
                    if nav_selectors:
                        best_selector = nav_selectors[0]['selector']
                
                elif elem.get('inMenu'):
                    menu_selectors = [s for s in selectors if s.get('type') == 'menu-custom']
                    if menu_selectors:
                        best_selector = menu_selectors[0]['selector']
                
                elif elem.get('inDialog'):
                    dialog_selectors = [s for s in selectors if s.get('type') == 'dialog-custom']
                    if dialog_selectors:
                        best_selector = dialog_selectors[0]['selector']
                
                elif elem.get('inForm'):
                    form_selectors = [s for s in selectors if s.get('type') == 'form-custom']
                    if form_selectors:
                        best_selector = form_selectors[0]['selector']
                
                if not best_selector:
                    custom_selectors = [s for s in selectors if s.get('type') == 'custom-class']
                    if custom_selectors:
                        best_selector = custom_selectors[0]['selector']
                
                if not best_selector:
                    text_selectors = [s for s in selectors if s.get('type') in ['text', 'tooltip']]
                    if text_selectors:
                        best_selector = text_selectors[0]['selector']
                
                if not best_selector:
                    data_selectors = [s for s in selectors if s.get('type') == 'data-attrs']
                    if data_selectors:
                        best_selector = data_selectors[0]['selector']
                
                if best_selector:
                    desc_parts.append(f"selector: {best_selector}")
                else:
                    desc_parts.append(f"selectors: {' | '.join(s['selector'] for s in selectors[:2])}")
            elif isinstance(selectors, list):
                desc_parts.append(f"selectors: {' | '.join(str(s) for s in selectors[:2])}")
            elif isinstance(selectors, str):
                desc_parts.append(f"selector: {selectors}")
    
    if elem_type.lower() == 'img':
        if elem.get('id'):
            desc_parts.append(f"id: '{elem.get('id')}'")
        if elem.get('data-pd-tooltip'):
            desc_parts.append("has tooltip")
        classes = elem.get('className', '').split()
        relevant_classes = [c for c in classes if 'menu' in c.lower() or 'pointer' in c.lower()]
        if relevant_classes:
            desc_parts.append(f"classes: '{' '.join(relevant_classes)}'")
        if elem.get('menuParent'):
            desc_parts.append(f"in menu: '{elem.get('menuParent')}'")
        if elem.get('tooltipText'):
            desc_parts.append(f"tooltip: '{elem.get('tooltipText')}'")
    
    if 'selectors' in elem and isinstance(elem['selectors'], list):
        for selector in elem['selectors']:
            if isinstance(selector, dict) and 'menuContext' in selector:
                menu_context = selector['menuContext']
                if menu_context:
                    desc_parts.append(f"in {menu_context}")
    
    if text:
        desc_parts.append(f"text: '{text}'")
    if input_type:
        desc_parts.append(f"type: '{input_type}'")
    if label:
        desc_parts.append(f"label: '{label}'")
    
    if 'selector' in elem:
        selector = elem['selector']
        if isinstance(selector, dict):
            selector = selector.get('selector', '')
        desc_parts.append(f"selector: {selector}")
    elif 'selectors' in elem and elem['selectors']:
        selectors = elem['selectors']
        if isinstance(selectors, list):
            filtered_selectors = []
            for s in selectors[:2]:
                if isinstance(s, dict):
                    sel = s.get('selector', '')
                    if sel:
                        filtered_selectors.append(sel)
                elif isinstance(s, str):
                    filtered_selectors.append(s)
            if filtered_selectors:
                desc_parts.append(f"selectors: {' | '.join(filtered_selectors)}")
        else:
            desc_parts.append(f"selector: {selectors}")
    
    return " | ".join(desc_parts)

def _add_element_attributes(desc_parts: list, elem: dict) -> None:
    attributes = [
        ('text', 'text'),
        ('id', 'id'),
        ('placeholder', 'placeholder'),
        ('inputType', 'type')
    ]
    for attr_key, attr_label in attributes:
        attr_value = elem.get(attr_key, '')
        if attr_value:
            desc_parts.append(f"{attr_label}: '{attr_value}'")

def _format_visible_elements(visible_elements: dict) -> str:
    sections = []
    buttons = visible_elements.get('buttons', [])
    if buttons:
        button_section = _format_buttons(buttons)
        sections.append(button_section)
    inputs = visible_elements.get('inputs', [])
    if inputs:
        input_section = _format_inputs(inputs)
        sections.append(input_section)
    return "\n".join(sections)

def _format_buttons(buttons: list) -> str:
    lines = [f"\nBUTTONS AVAILABLE: {len(buttons)} button(s)"]
    for i, btn in enumerate(buttons[:3], 1):
        btn_text = btn.get('text', '')
        if btn_text:
            lines.append(f"  {i}. '{btn_text}'")
    return "\n".join(lines)

def _format_inputs(inputs: list) -> str:
    lines = [f"\nINPUTS AVAILABLE: {len(inputs)} input(s)"]
    for i, inp in enumerate(inputs[:3], 1):
        inp_type = inp.get('inputType', 'text')
        lines.append(f"  {i}. {inp_type} input")
    return "\n".join(lines)

def _format_dynamic_content(dynamic_content: dict) -> str:
    dropdowns = dynamic_content.get('dropdowns', [])
    if not dropdowns:
        return ""
    
    dropdown_lines = ["DROPDOWN MENUS & OVERLAY PANELS:"]
    count = 0
    
    for dropdown in dropdowns:
        trigger = dropdown.get('trigger', {})
        trigger_text = trigger.get('text', '').strip()
        menu_items = dropdown.get('menuItems', [])
        dropdown_type = dropdown.get('type', 'dropdown')
        is_visible = dropdown.get('isVisible', True)
        panel_id = dropdown.get('panelId', '') or ""
        overlay_type = dropdown.get('overlayType', '')
        trigger_classes = trigger.get('classes', '').split()
        
        if not menu_items:
            continue
            
        count += 1
        if count > 5:
            break
            
        overlay_info = []
        if 'p-overlaypanel' in trigger_classes:
            overlay_info.append('PrimeVue OverlayPanel')
        elif 'p-dropdown' in trigger_classes:
            overlay_info.append('PrimeVue Dropdown')
        elif 'modal' in trigger_classes:
            overlay_info.append('Modal Dialog')
        
        if dropdown.get('position') == 'fixed':
            overlay_info.append('fixed position')
        elif dropdown.get('position') == 'absolute':
            overlay_info.append('absolute position')
        
        if dropdown.get('zIndex'):
            overlay_info.append(f"z-index: {dropdown.get('zIndex')}")
        
        detailed_items = []
        for item in menu_items[:5]:
            item_detail = {
                'text': item.get('text', '').strip(),
                'tag': item.get('tagName', '').lower(),
                'classes': item.get('classes', ''),
                'clickable': item.get('isClickable', False),
                'role': item.get('role', ''),
                'data_attrs': item.get('dataAttributes', {}),
                'selectors': item.get('selectors', [])
            }
            
            if item_detail['text']:
                item_info = []
                item_info.append(f"'{item_detail['text']}'")
                
                attrs = []
                if item_detail['role']:
                    attrs.append(f"role={item_detail['role']}")
                if item_detail['clickable']:
                    attrs.append('clickable')
                if item_detail['classes']:
                    relevant_classes = [c for c in item_detail['classes'].split() 
                                     if 'item' in c.lower() or 'option' in c.lower()]
                    if relevant_classes:
                        attrs.append(f"class={relevant_classes[0]}")
                if attrs:
                    item_info.append(" | ".join(attrs))
                
                best_selectors: List[str] = []
                best_selectors.append(f'text="{item_detail["text"]}"')
                if 'p-overlaypanel' in trigger_classes and item_detail['text']:
                    text_esc = item_detail['text'].replace('"', '\\"')
                    best_selectors.insert(0, f'locator(".p-overlaypanel .option-text:has-text(\\"{text_esc}\\")").first()')
                    best_selectors.insert(0, f'locator(".p-overlaypanel .option-item:has-text(\\"{text_esc}\\")").first()')
                if item_detail['selectors']:
                    for selector in item_detail['selectors'][:3]:
                        if isinstance(selector, dict):
                            if selector.get('selector'):
                                best_selectors.append(selector['selector'])
                        elif isinstance(selector, str):
                            best_selectors.append(selector)
                
                if best_selectors:
                    item_info.append(f"selectors=[{' | '.join(best_selectors)}]")
                
                detailed_items.append(' | '.join(item_info))
        
        header_parts = []
        if overlay_info:
            header_parts.extend(overlay_info)
        if trigger_text:
            header_parts.append(f"trigger='{trigger_text}'")
        if panel_id:
            header_parts.append(f"id='{panel_id}'")
        
        best_overlay_selector = None
        if 'p-overlaypanel' in trigger_classes:
            best_overlay_selector = "locator('.p-overlaypanel')"
        elif panel_id:
            best_overlay_selector = f"locator('#{panel_id}')"
        elif overlay_type == 'menu':
            best_overlay_selector = "getByRole('menu')"
        elif overlay_type == 'dialog':
            best_overlay_selector = "getByRole('dialog')"
        
        visibility_note = " (VISIBLE)" if is_visible else " (HIDDEN)"
        type_display = f"{overlay_type.upper() if overlay_type else dropdown_type.upper()}"
        
        line = [
            f"{count}. {type_display}{visibility_note} | {' | '.join(header_parts)}",
            f"selector: {best_overlay_selector}" if best_overlay_selector else None,
            "ITEMS:",
            *[f"  - {item}" for item in detailed_items]
        ]
        
        dropdown_lines.append('\n'.join(filter(None, line)))
        dropdown_lines.append('-' * 50)
    
    return "\n".join(dropdown_lines) if count > 0 else ""

def _format_form_elements(forms: list) -> str:
    if not forms:
        return ""
        
    formatted_lines = ["FORM ELEMENTS:"]
    
    for form_idx, form in enumerate(forms, 1):
        form_id = form.get('id', '')
        form_method = form.get('method', 'POST')
        inputs = form.get('inputs', [])
        buttons = form.get('buttons', [])
        
        form_header = [f"\nFORM #{form_idx}"]
        if form_id:
            form_header.append(f"ID: {form_id}")
        form_header.append(f"METHOD: {form_method}")
        formatted_lines.append(" | ".join(form_header))
        
        if inputs:
            formatted_lines.append("\nINPUT FIELDS:")
            for input_el in inputs:
                input_info = []
                
                input_type = input_el.get('type', 'text')
                input_name = input_el.get('name', '')
                input_label = input_el.get('label', '')
                is_required = input_el.get('required', False)
                is_primevue = input_el.get('isPrimeVue', False)
                component = input_el.get('component', '')
                
                if input_label:
                    input_info.append(f"Label: '{input_label}'")
                if input_name:
                    input_info.append(f"name='{input_name}'")
                input_info.append(f"type='{input_type}'")
                if is_required:
                    input_info.append("required")
                if is_primevue:
                    input_info.append(f"component='{component}'")
                
                selector = input_el.get('selector')
                if selector:
                    input_info.append(f"selector='{selector}'")
                
                formatted_lines.append(f"  - {' | '.join(input_info)}")
        
        if buttons:
            formatted_lines.append("\nBUTTONS:")
            for button in buttons:
                button_info = []
                
                button_text = button.get('text', '')
                button_type = button.get('type', 'button')
                is_disabled = button.get('disabled', False)
                is_primevue = button.get('isPrimeVue', False)
                variant = button.get('variant', 'default')
                
                if button_text:
                    button_info.append(f"Text: '{button_text}'")
                button_info.append(f"type='{button_type}'")
                if is_disabled:
                    button_info.append("disabled")
                if is_primevue:
                    button_info.append(f"variant='{variant}'")
                
                selector = button.get('selector')
                if selector:
                    button_info.append(f"selector='{selector}'")
                
                formatted_lines.append(f"  - {' | '.join(button_info)}")
        
        formatted_lines.append("-" * 50)
    
    return "\n".join(formatted_lines)

def _format_tables(tables: dict) -> str:
    if not isinstance(tables, str):
        return "No table data available"
    try:
        table_data = TableData.parse(tables)
        return table_data.format()
    except Exception as e:
        return f"Error formatting table data: {str(e)}"

def format_completed_steps(completed_steps: List[Dict[str, Any]]) -> str:
    steps_info = ""
    for i, step in enumerate(completed_steps, 1):
        if isinstance(step, dict):
            steps_info += f"""
Step {i}: {step.get('step_desc', 'Action')}
- Selector: {step.get('selector', 'N/A')}
- Resolved Locator: {step.get('resolved_locator', 'N/A')}
- Action Type: {step.get('action_type', 'N/A')}
- Vision Analysis: {step.get('vision_analysis', 'N/A')}
"""
    return steps_info

async def collect_page_elements_info(page, previous_selector: str, action_type: str, locator: str) -> dict:
    logger.error(f"Collecting page elements info for selector: {previous_selector} and action type: {action_type}")
    try:
        page_elements = {}
        roles = ["button", "link", "textbox", "checkbox", "radio", "combobox", 
                "listbox", "option", "dialog", "alert", "tab", "tabpanel", 
                "menu", "menuitem", "generic"]
        
        special_selectors = {
            "clickable_images": "img[id], img[class*='menu-item'], img[class*='action'], img[class*='button']",
            "menu_triggers": "[id*='menu'], [class*='menu-trigger'], [class*='dropdown-toggle']"
        }
        
        for role in roles:
            elements = await page.get_by_role(role).all()
            if elements:
                role_elements = []
                for element in elements:
                    label_text = await element.evaluate("""el => {
                        if (el.getAttribute('aria-label')) {
                            return el.getAttribute('aria-label');
                        }
                        
                        let labelText = '';
                        
                        if (el.id) {
                            const label = document.querySelector(`label[for="${el.id}"]`);
                            if (label) {
                                return label.textContent.trim();
                            }
                        }
                        
                        let parent = el.parentElement;
                        while (parent) {
                            if (parent.tagName.toLowerCase() === 'label') { 
                                const clone = parent.cloneNode(true);
                                const inputs = clone.querySelectorAll('input, select, textarea');
                                inputs.forEach(input => input.remove());
                                return clone.textContent.trim();
                            }
                            parent = parent.parentElement;
                        }
                        
                            
                        const labelledBy = el.getAttribute('aria-labelledby');
                        if (labelledBy) {
                            const labelElements = labelledBy.split(' ').map(id => document.getElementById(id));
                            return labelElements.map(el => el ? el.textContent : '').join(' ').trim();
                        }
                        
                        return '';
                    }""")

                    placeholder = await element.evaluate("el => el.getAttribute('placeholder')")

                    name_attr = await element.evaluate("el => el.getAttribute('name')")

                    class_info = await element.evaluate("""el => {
                        const classes = Array.from(el.classList);
                        const framework_classes = {
                            primevue: classes.filter(c => c.startsWith('p-')),
                            bootstrap: classes.filter(c => c.startsWith('btn-') || c.startsWith('form-') || c.startsWith('nav-')),
                            material: classes.filter(c => c.startsWith('mat-')),
                            tailwind: classes.filter(c => c.match(/^(bg-|text-|border-|rounded-|flex|grid|p-|m-)/)),
                            custom: classes.filter(c => 
                                !c.startsWith('p-') && 
                                !c.startsWith('btn-') && 
                                !c.startsWith('form-') && 
                                !c.startsWith('nav-') && 
                                !c.startsWith('mat-') &&
                                !c.match(/^(bg-|text-|border-|rounded-|flex|grid|p-|m-)/)
                            )
                        };
                        return {
                            all: classes,
                            categorized: framework_classes
                        };
                    }""")

                    element_data = await element.evaluate("""el => {
                        const data = {
                            id: el.id || null,
                            dataAttrs: {},
                            ariaAttrs: {},
                            otherAttrs: {}
                        };
                        
                        for (const attr of el.attributes) {
                            if (attr.name === 'class') continue;
                            
                            if (attr.name === 'id') {
                                data.id = attr.value;
                            }
                            else if (attr.name.startsWith('data-')) {
                                data.dataAttrs[attr.name] = attr.value;
                            }
                            else if (attr.name.startsWith('aria-')) {
                                data.ariaAttrs[attr.name] = attr.value;
                            }
                            else {
                                data.otherAttrs[attr.name] = attr.value;
                            }
                        }
                        return data;
                    }""")

                    inner_elements = []
                    if role == "dialog":
                        inner_elements = await element.evaluate("""el => {
                            const elements = [];
                            const walk = (node) => {
                                if (node.nodeType === 1) { 
                                    const info = {
                                        tag: node.tagName.toLowerCase(),
                                        text: node.textContent.trim(),
                                        required: node.hasAttribute('required'),
                                        id: node.id || null,
                                        classes: Array.from(node.classList),
                                        attributes: {}
                                    };
                                    
                                    for (const attr of node.attributes) {
                                        if (attr.name !== 'class') {
                                            info.attributes[attr.name] = attr.value;
                                        }
                                    }
                                    
                                    if (info.text && !info.text.includes('*') && !info.text.includes('Select')) {
                                        elements.push(info);
                                    }
                                    
                                    for (const child of node.children) {
                                        walk(child);
                                    }
                                }
                            };
                            walk(el);
                            return elements;
                        }""")

                    dropdown_options = []
                    if role == "combobox":
                        try:
                            listbox_id = element_data["ariaAttrs"].get("aria-controls", "")
                            if listbox_id:
                                options = await page.locator(f'#{listbox_id} [role="option"]').all()
                                for option in options:
                                    option_info = {
                                        "text": await option.text_content(),
                                        "value": await option.get_attribute("data-value"),
                                        "selected": await option.get_attribute("aria-selected") == "true"
                                    }
                                    dropdown_options.append(option_info)
                        except Exception:
                            pass  
                    toolbar_info = await element.evaluate("""el => {
                        const toolbar = el.closest('[role="toolbar"]');
                        if (toolbar) {
                            return {
                                role: toolbar.getAttribute('role'),
                                classes: Array.from(toolbar.classList),
                                dataAttrs: Object.fromEntries(
                                    Array.from(toolbar.attributes)
                                        .filter(attr => attr.name.startsWith('data-'))
                                        .map(attr => [attr.name, attr.value])
                                )
                            };
                        }
                        return null;
                    }""")

                    element_info = {
                        "role": role,
                        "text": await element.text_content(),
                        "visible": await element.is_visible(),
                        "html": await element.evaluate("el => el.outerHTML"),
                        "label": label_text if label_text else None,
                        "placeholder": placeholder if placeholder else None,
                        "name": name_attr if name_attr else None,
                        "id": element_data["id"],
                        "data_attributes": element_data["dataAttrs"],
                        "aria_attributes": element_data["ariaAttrs"],
                        "other_attributes": element_data["otherAttrs"],
                        "classes": class_info,
                        "inner_elements": inner_elements if inner_elements else None,
                        "options": dropdown_options if dropdown_options else None,
                        "parent_toolbar": toolbar_info
                    }
                    role_elements.append(element_info)
                page_elements[role] = role_elements
        
        custom_elements = await page.locator('.option-item').all()
        if custom_elements:
            custom_elements_info = []
            for element in custom_elements:
                element_info = {
                    "role": "custom",
                    "text": await element.text_content(),
                    "visible": await element.is_visible(),
                    "html": await element.evaluate("el => el.outerHTML"),
                    "attributes": await element.evaluate("""el => {
                        const attrs = {};
                        for (const attr of el.attributes) {
                            attrs[attr.name] = attr.value;
                        }
                        return attrs;
                    }""")
                }
                custom_elements_info.append(element_info)
            page_elements["custom"] = custom_elements_info

        for selector_type, selector in special_selectors.items():
            special_elements = await page.locator(selector).all()
            if special_elements:
                special_elements_info = []
                for element in special_elements:
                    element_info = {
                        "role": selector_type,
                        "text": await element.text_content(),
                        "visible": await element.is_visible(),
                        "html": await element.evaluate("el => el.outerHTML"),
                        "id": await element.get_attribute("id"),
                        "data_attributes": await element.evaluate("""el => {
                            const data = {};
                            for (const attr of el.attributes) {
                                if (attr.name.startsWith('data-')) {
                                    data[attr.name] = attr.value;
                                }
                            }
                            return data;
                        }"""),
                        "classes": await element.evaluate("el => Array.from(el.classList)"),
                        "parent_info": await element.evaluate("""el => {
                            const parent = el.parentElement;
                            return parent ? {
                                tag: parent.tagName.toLowerCase(),
                                classes: Array.from(parent.classList),
                                id: parent.id || null,
                                role: parent.getAttribute('role')
                            } : null;
                        }""")
                    }
                    special_elements_info.append(element_info)
                page_elements[selector_type] = special_elements_info
        
        logger.error(f"Selector: {previous_selector}")
        return {
            "selector": previous_selector,
            "locator": locator,
            "action_type": action_type,
            "page_elements": page_elements,
        }
    except Exception as e:
        return {
            "selector": previous_selector,
            "action_type": action_type,
            "locator": locator,
            "error": str(e)
        }


   
def clean_selector_response(selector: str) -> str:   
    if not selector:
        return selector
        
    selector = re.sub(r'```(?:css)?\s*\n?([^`]+?)\n?```', r'\1', selector, flags=re.DOTALL)
    
    selector = selector.replace('`', '')
    
    selector = re.sub(r'getByRole\(([^,]+),\s*{\s*name:\s*([^}]+)\s*}\)', r'getByRole(\1,{name:\2})', selector)
    
    nth_matches = re.finditer(r'\.nth\(\d+\)', selector)
    nth_parts = [m.group(0) for m in nth_matches]
    
    parts = re.split(r'\.nth\(\d+\)', selector)
    cleaned_parts = [re.sub(r'\s+', ' ', part).strip() for part in parts]
    
    final_selector = cleaned_parts[0]
    for i, nth_part in enumerate(nth_parts):
        if i + 1 < len(cleaned_parts):
            final_selector += nth_part + cleaned_parts[i + 1]
            
    return final_selector.strip()
    

