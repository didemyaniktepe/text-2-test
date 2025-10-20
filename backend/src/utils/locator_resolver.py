import re
from typing import Any, Optional, TypeAlias

# Keep runtime free of optional deps; provide structural types for annotations
Page: TypeAlias = Any
Locator: TypeAlias = Any

ROLE_ID_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*id:\s*'([^']+)'\s*}\)")
ROLE_NAME_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*name:\s*'([^']+)'\s*}\)")
ROLE_NAME_NTH_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*name:\s*'([^']+)'\s*}\)\.nth\((\d+)\)")
ROLE_NAME_FIRST_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*name:\s*'([^']+)'\s*}\)\.first\(\)")
ROLE_NAME_LAST_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*name:\s*'([^']+)'\s*}\)\.last\(\)")

ROLE_NAME_CHAIN_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*name:\s*'([^']+)'\s*}\)\.locator\('([^']+)'\)")
ROLE_NAME_CHAIN_FIRST_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*name:\s*'([^']+)'\s*}\)\.locator\('([^']+)'\)\.first\(\)")
ROLE_NAME_CHAIN_LAST_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*name:\s*'([^']+)'\s*}\)\.locator\('([^']+)'\)\.last\(\)")
ROLE_NAME_CHAIN_NTH_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*name:\s*'([^']+)'\s*}\)\.locator\('([^']+)'\)\.nth\((\d+)\)")
ROLE_NAME_CHAIN_FILTER_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*name:\s*'([^']+)'\s*}\)\.locator\('([^']+)'\)\.filter\(\{\s*([^}]+)\s*\}\)")

ROLE_CONTROLS_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*ariaControls:\s*'([^']+)'\s*}\)")
ROLE_SIMPLE_RE = re.compile(r"getByRole\('([^']+)'\)")
ROLE_NTH_RE = re.compile(r"getByRole\('([^']+)'\)\.nth\((\d+)\)")
ROLE_FIRST_RE = re.compile(r"getByRole\('([^']+)'\)\.first\(\)")
ROLE_LAST_RE = re.compile(r"getByRole\('([^']+)'\)\.last\(\)")
ROLE_FILTER_TEXT_RE = re.compile(r"getByRole\('([^']+)'\)\.filter\(\{\s*hasText:\s*'([^']+)'\s*\}\)")
ROLE_FILTER_CLASS_RE = re.compile(r"getByRole\('([^']+)'\)\.filter\(\{\s*hasClass:\s*'([^']+)'\s*\}\)")
ROLE_FILTER_HAS_RE = re.compile(r"getByRole\('([^']+)'\)\.filter\(\{\s*has:\s*(?:page\.)?locator\('([^']+)'\)\s*\}\)")
ROLE_FILTER_MULTI_HAS_RE = re.compile(r"getByRole\('([^']+)'\)((?:\.filter\(\{\s*has:\s*(?:page\.)?locator\('([^']+)'\)\s*\}\))+)")
ROLE_LOCATOR_CHAIN_RE = re.compile(r"getByRole\('([^']+)'\)\.locator\('([^']+)'\)")
ROLE_FILTER_AND_RE = re.compile(r"getByRole\('([^']+)'\)\.filter\(\{\s*hasClass:\s*'([^']+)'\s*\}\)\.and\(page\.locator\('([^']+)'\)\)")
ROLE_AND_COMPLEX_RE = re.compile(r"getByRole\('([^']+)',\s*\{\s*name:\s*'([^']+)'\s*\}\)\.and\(page\.getByText\('([^']+)'\)\.locator\('([^']+)'\)\.getByRole\('([^']+)'\)\)")
ROLE_NESTED_RE = re.compile(r"getByRole\('([^']+)'\)\.getByRole\('([^']+)',\s*{\s*class:\s*'([^']+)'\s*}\)")
ROLE_COMPLEX_CHAIN_RE = re.compile(r"getByRole\('([^']+)'\)\.locator\('([^']+):has-text\(\"([^\"]+)\"\)'\)")
ROLE_SELECT_OPTION_RE = re.compile(r"getByRole\('([^']+)',\s*{\s*name:\s*'([^']+)'\s*}\)\.selectOption\('([^']+)'\)")
LABEL_RE = re.compile(r"getByLabel\('([^']+)'\)")
PLACEHOLDER_RE = re.compile(r"getByPlaceholder\('([^']+)'\)")
TESTID_RE = re.compile(r"getByTestId\('([^']+)'\)")
TEXT_RE = re.compile(r"getByText\('([^']+)'\)")

LOCATOR_START_RE = re.compile(r"locator\('([^']+)'\)")
LOCATOR_CHAIN_RE = re.compile(r"\.locator\('([^']+)'\)")

GRID_INFO_RE = re.compile(r"\[table=(\d+)\s*r=(\d+)\s*c=(\d+)\]")
HAS_TEXT_RE = re.compile(r":has-text\([\"']([^\"']+)[\"']\)")
FILTER_HAS_TEXT_RE = re.compile(r"\.filter\(\{\s*hasText:\s*/(.+?)/([a-z]*)\s*\}\)")
NTH_RE = re.compile(r"\.nth\((\d+)\)")

PRIMEVUE_ITEM_RE = re.compile(r"locator\('\.p-overlaypanel \.option-item:has-text\(\"([^\"]+)\"\)'\)")
PRIMEVUE_ITEM_FILTER_RE = re.compile(r"locator\('\.p-overlaypanel'\)\.locator\('\.option-item'\)\.filter\(\{{\s*hasText:\s*'([^']+)'\s*\}\}\)\.first\(\)")

GETBYROLE_CHAIN_RE = re.compile(r"\.getByRole\('([^']+)'(?:\s*,\s*{[^}]*name:\s*'([^']+)'[^}]*})?\)")
GETBYTEXT_CHAIN_RE = TEXT_RE

def _js_regex_to_py(pattern: str, flags_str: str) -> re.Pattern:
    pattern = pattern.replace("\\\\", "\\")
    flags = 0
    if 'i' in flags_str: flags |= re.IGNORECASE
    if 'm' in flags_str: flags |= re.MULTILINE
    if 's' in flags_str: flags |= re.DOTALL
    return re.compile(pattern, flags)
    
def resolve_locator(page: Page, selector: str) -> Locator:
    s = selector.strip()
    print(f"DEBUG: resolve_locator called with selector: '{s}'")
    
    has_chain = any(t in s for t in ['.nth(', '.first(', '.last(', '.locator('])
    
    if 'details-more-menu' in s or '[data-pd-tooltip="true"]' in s or '.action-buttons img' in s and not has_chain:
        if s.startswith('locator('):
            s = s[8:-1].strip("'\"")
        return page.locator(s)
    
    if s.endswith('-menu') and ('#' in s or 'details-' in s):
        return page.locator(s)
    
    if s.startswith('img#') or s.startswith('img.') and not has_chain:
        return page.locator(s)
    
    if '#' in s and any(tag in s.split('#')[0] for tag in ['img', 'button', 'a']) and not s.startswith('locator('):
        return page.locator(s)
    
    
        
    m = ROLE_NTH_RE.fullmatch(s)
    if m:
        role, nth = m.groups()
        return page.locator(f'[role="{role}"]').nth(int(nth))

    m = ROLE_FIRST_RE.fullmatch(s)
    if m:
        role = m.group(1)
        try:
            return page.get_by_role(role).first
        except Exception:
            return page.locator(f'internal:role={role}').first

    m = ROLE_LAST_RE.fullmatch(s)
    if m:
        role = m.group(1)
        try:
            return page.get_by_role(role).last
        except Exception:
            return page.locator(f'internal:role={role}').last

    def _handle_role_chain(page: Page, role: str, name: str, chain: str, modifier: Optional[str] = None, filter_expr: Optional[str] = None) -> Locator:
        try:
            base = page.get_by_role(role, name=name)
        except Exception:
            base = page.locator(f'internal:role={role}[name="{name}"i]')
            
        loc = base.locator(chain)
        
        if filter_expr:
            if 'hasNot' in filter_expr:
                match = re.search(r"hasNot:\s*'([^']+)'", filter_expr)
                if match:
                    selector = match.group(1)
                    loc = loc.filter(has=f":not({selector})")
            elif 'hasText' in filter_expr:
                match = re.search(r"hasText:\s*'([^']+)'", filter_expr)
                if match:
                    text = match.group(1)
                    loc = loc.filter(has_text=text)
        
        if modifier == 'first':
            return loc.first
        elif modifier == 'last':
            return loc.last
        elif modifier and modifier.startswith('nth:'):
            return loc.nth(int(modifier.split(':')[1]))
            
        return loc

    m = ROLE_NAME_NTH_RE.fullmatch(s)
    if m:
        role, name, nth = m.groups()
        try:
            return page.get_by_role(role, name=name).nth(int(nth))
        except Exception:
            return page.locator(f'internal:role={role}[name="{name}"i]').nth(int(nth))

    m = ROLE_NAME_FIRST_RE.fullmatch(s)
    if m:
        role, name = m.groups()
        try:
            return page.get_by_role(role, name=name).first
        except Exception:
            return page.locator(f'internal:role={role}[name="{name}"i]').first

    m = ROLE_NAME_LAST_RE.fullmatch(s)
    if m:
        role, name = m.groups()
        try:
            return page.get_by_role(role, name=name).last
        except Exception:
            return page.locator(f'internal:role={role}[name="{name}"i]').last

    m = ROLE_NAME_CHAIN_FIRST_RE.fullmatch(s)
    if m:
        role, name, chain = m.groups()
        return _handle_role_chain(page, role, name, chain, modifier='first')
        
    m = ROLE_NAME_CHAIN_LAST_RE.fullmatch(s)
    if m:
        role, name, chain = m.groups()
        return _handle_role_chain(page, role, name, chain, modifier='last')
        
    m = ROLE_NAME_CHAIN_NTH_RE.fullmatch(s)
    if m:
        role, name, chain, nth = m.groups()
        return _handle_role_chain(page, role, name, chain, modifier=f'nth:{nth}')
    
    m = ROLE_ID_RE.fullmatch(s)
    if m:
        role, element_id = m.groups()
        return page.locator(f'[role="{role}"][id="{element_id}"]')
    
    m = ROLE_NAME_CHAIN_FILTER_RE.fullmatch(s)
    if m:
        role, name, chain, filter_expr = m.groups()
        return _handle_role_chain(page, role, name, chain, filter_expr=filter_expr)
        
    m = ROLE_NAME_CHAIN_RE.fullmatch(s)
    if m:
        role, name, chain = m.groups()
        return _handle_role_chain(page, role, name, chain)

    m = ROLE_FILTER_TEXT_RE.fullmatch(s)
    if m:
        role, text = m.groups()
        return page.get_by_role(role).filter(has_text=text)

    m = ROLE_FILTER_CLASS_RE.fullmatch(s)
    if m:
        role, class_name = m.groups()
        return page.get_by_role(role).filter(has_class=class_name)

    m = ROLE_LOCATOR_CHAIN_RE.fullmatch(s)
    if m:
        role, selector = m.groups()
        return page.get_by_role(role).locator(selector)

    m = ROLE_FILTER_MULTI_HAS_RE.fullmatch(s)
    if m:
        role = m.group(1)
        filters_chain = m.group(2)
        loc = page.get_by_role(role)
        
        filter_matches = re.finditer(r"\.filter\(\{\s*has:\s*(?:page\.)?locator\('([^']+)'\)\s*\}\)", filters_chain)
        for filter_match in filter_matches:
            selector = filter_match.group(1)
            loc = loc.filter(has=page.locator(selector))
        return loc

    m = ROLE_AND_COMPLEX_RE.fullmatch(s)
    if m:
        role1, name1, text, locator_path, role2 = m.groups()
        try:
            first_loc = page.get_by_role(role1, name=name1)
            second_loc = page.get_by_text(text).locator(locator_path).get_by_role(role2)
            return first_loc.and_(second_loc)
        except Exception:
            first_loc = page.locator(f'internal:role={role1}[name="{name1}"i]')
            second_loc = page.locator(f'text="{text}"').locator(locator_path).locator(f'internal:role={role2}')
            return first_loc.and_(second_loc)

    m = ROLE_FILTER_AND_RE.fullmatch(s)
    if m:
        role, class_name, selector = m.groups()
        return page.get_by_role(role).filter(has_class=class_name).filter(has=page.locator(selector))

    m = ROLE_NESTED_RE.fullmatch(s)
    if m:
        outer_role, inner_role, class_name = m.groups()
        return page.get_by_role(outer_role).get_by_role(inner_role).filter(has_class=class_name)

    m = ROLE_COMPLEX_CHAIN_RE.fullmatch(s)
    if m:
        role, selector_base, text = m.groups()
        return page.get_by_role(role).locator(f'{selector_base}:has-text("{text}")')

    m = ROLE_SELECT_OPTION_RE.fullmatch(s)
    if m:
        role, name, option = m.groups()
        try:
            return page.get_by_role(role, name=name)
        except Exception:
            return page.locator(f'internal:role={role}[name="{name}"i]')

    m = ROLE_FILTER_HAS_RE.fullmatch(s)
    if m:
        role, selector = m.groups()
        return page.get_by_role(role).filter(has=page.locator(selector))

    m = ROLE_NAME_RE.fullmatch(s)
    if m:
        role, name = m.groups()
        try:
            return page.get_by_role(role, name=name)
        except Exception:
            return page.locator(f'internal:role={role}[name="{name}"i]')

    m = ROLE_CONTROLS_RE.fullmatch(s)
    if m:
        role, controls = m.groups()
        return page.locator(f'[role="{role}"][aria-controls="{controls}"]')

    m = ROLE_SIMPLE_RE.fullmatch(s)
    if m:
        role = m.group(1)
        try:
            return page.get_by_role(role)
        except Exception:
            return page.locator(f'internal:role={role}')

    m = LABEL_RE.fullmatch(s)
    if m:
        return page.get_by_label(m.group(1))

    m = PLACEHOLDER_RE.fullmatch(s)
    if m:
        return page.get_by_placeholder(m.group(1))

    m = TESTID_RE.fullmatch(s)
    if m:
        test_id = m.group(1)
        try:
            return page.get_by_test_id(test_id)
        except Exception:
            return page.locator(f'[data-test="{test_id}"]')

    m = TEXT_RE.fullmatch(s)
    if m:
        return page.get_by_text(m.group(1))

    if s.startswith("getByText('"):
        text_start_m = re.match(r"getByText\('([^']+)'\)", s)
        if text_start_m:
            loc = page.get_by_text(text_start_m.group(1))

            for chain_m in LOCATOR_CHAIN_RE.finditer(s):
                selector_part = chain_m.group(1)
                has_text_m = HAS_TEXT_RE.search(selector_part)
                if has_text_m:
                    text_val = has_text_m.group(1)
                    base_selector = selector_part[:has_text_m.start()]
                    loc = loc.locator(base_selector).filter(has_text=text_val)
                else:
                    loc = loc.locator(selector_part)

            for role_m in GETBYROLE_CHAIN_RE.finditer(s):
                role, name = role_m.groups()
                try:
                    loc = loc.get_by_role(role, name=name) if name else loc.get_by_role(role)
                except Exception:
                    if name:
                        loc = loc.locator(f'internal:role={role}[name="{name}"i]')
                    else:
                        loc = loc.locator(f'internal:role={role}')

            for txt_m in GETBYTEXT_CHAIN_RE.finditer(s):
                txt = txt_m.group(1)
                loc = loc.get_by_text(txt)

            nth_m = NTH_RE.search(s)
            if nth_m:
                loc = loc.nth(int(nth_m.group(1)))

            return loc
    
    m = PRIMEVUE_ITEM_FILTER_RE.fullmatch(s)
    if m:
        text = m.group(1)
        return page.locator('.p-overlaypanel').locator('.option-item').filter(has_text=text).first()

    if 'p-overlaypanel' in s and ':has-text' in s:
        text_match = re.search(r':has-text\("([^"]+)"\)', s)
        if text_match:
            text = text_match.group(1)
            if '.first()' in s:
                return page.locator(f'.p-overlaypanel .option-item:has-text("{text}")').first
            else:
                return page.locator(f'.p-overlaypanel .option-item:has-text("{text}")')

    m = PRIMEVUE_ITEM_RE.fullmatch(s)
    if m:
        text = m.group(1)
        return page.locator(f'.p-overlaypanel .option-item:has-text("{text}")')


    m = re.fullmatch(r"locator\('([^']+)'\)\.contentLocator\('([^']+)'\)", s)
    if m:
        iframe_sel, inner_sel = m.groups()
        return page.frame_locator(iframe_sel).locator(inner_sel)

    m = LOCATOR_START_RE.match(s)
    if m:
        root = m.group(1)
        print(f"DEBUG: LOCATOR_START_RE matched, root: '{root}'")
        loc = page.locator(root)
            
        has_text_m = HAS_TEXT_RE.search(root)
        if has_text_m:
            text = has_text_m.group(1)
            base_selector = root[:has_text_m.start()]
            loc = page.locator(base_selector).filter(has_text=text)
        
        for chain_m in LOCATOR_CHAIN_RE.finditer(s):
            selector = chain_m.group(1)
            has_text_m = HAS_TEXT_RE.search(selector)
            if has_text_m:
                text = has_text_m.group(1)
                base_selector = selector[:has_text_m.start()]
                loc = loc.locator(base_selector).filter(has_text=text)
            else:
                loc = loc.locator(selector)
        
        grid_m = GRID_INFO_RE.search(s)
        if grid_m:
            _, row_idx, col_idx = map(int, grid_m.groups())
            loc = loc.locator('tr').nth(row_idx).locator('td').nth(col_idx)
        
        for has_text_m in FILTER_HAS_TEXT_RE.finditer(s):
            body, flags = has_text_m.groups()
            loc = loc.filter(has_text=_js_regex_to_py(body, flags))
        
        for role_m in GETBYROLE_CHAIN_RE.finditer(s):
            role, name = role_m.groups()
            try:
                loc = loc.get_by_role(role, name=name) if name else loc.get_by_role(role)
            except Exception:
                if name:
                    loc = loc.locator(f'internal:role={role}[name="{name}"i]')
                else:
                    loc = loc.locator(f'internal:role={role}')
        
        for txt_m in GETBYTEXT_CHAIN_RE.finditer(s):
            txt = txt_m.group(1)
            loc = loc.get_by_text(txt)
        
        nth_m = NTH_RE.search(s)
        if nth_m:
            loc = loc.nth(int(nth_m.group(1)))
        
        print(f"DEBUG: Returning resolved locator")
        return loc


    gb_flex = re.match(r"getByRole\(\s*(['\"])([^'\"]+)\1\s*(?:,\s*\{([^}]*)\})?\s*\)$", s)
    if gb_flex:
        role = gb_flex.group(2)
        body = gb_flex.group(3) or ''

        name_q = re.search(r"name\s*:\s*(['\"])\s*([^'\"]+)\s*\1", body)
        name_rx = re.search(r"name\s*:\s*/(.+?)/([a-z]*)", body)
        try:
            if name_q:
                name_val = name_q.group(2)
                return page.get_by_role(role, name=name_val)
            if name_rx:
                pattern = _js_regex_to_py(name_rx.group(1), name_rx.group(2))
                return page.get_by_role(role, name=pattern)
            return page.get_by_role(role)
        except Exception:
            if name_q:
                name_val = name_q.group(2)
                return page.locator(f'internal:role={role}[name="{name_val}"i]')
            return page.locator(f'internal:role={role}')

    print(f"DEBUG: No pattern matched, falling back to page.locator('{s}')")
    return page.locator(s)