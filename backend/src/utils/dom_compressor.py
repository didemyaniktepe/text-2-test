from collections import defaultdict
from typing import Dict, Any, List, Tuple
import re

DEFAULT_TOKEN_BUDGET = 1800        
MAX_PER_BUCKET_BASE = 18           
NAME_MIN_LEN = 2

ROLE_SCORE = {
    "combobox": 100,
    "textbox": 90,
    "link": 80,
    "button": 70,
    "columnheader": 60,
    "checkbox": 50,
}

def norm_space(s: str | None) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def bucket_name(el: Dict[str, Any]) -> str:
    role = (el.get("Role") or "").lower()
    tag = (el.get("Tag") or "").lower()
    name = norm_space(el.get("Name"))
    if role == "button" and name in {"Dashboard","Vehicles","All","Groups","Events","Archive","Reports","Notifications","Documents","Users"}:
        return "nav_buttons"
    if role == "textbox" and name.lower() == "search":
        return "global_search"
    if role == "columnheader":
        return "table_headers"
    if el.get("grid") is not None:
        return "table_filters_row"
    if role == "link":
        return "table_links"
    if role == "button" and re.fullmatch(r"\d+", name or ""):
        return "pagination"
    if role == "combobox" and name in {"All time","10"}:
        return "toolbar_comboboxes"
    if role == "button":
        return "buttons_other"
    if role == "textbox":
        return "textboxes_other"
    if role == "combobox":
        return "comboboxes_other"
    return f"other_{role or tag or 'unknown'}"

def nice_selector(el: Dict[str, Any]) -> str:
    sels = el.get("selectors", [])
    
    by_testid = next((s for s in sels if s.get("type") == "testId"), None)
    if by_testid:
        return by_testid["value"]

    by_label = next((s for s in sels if s.get("type") == "label"), None)
    if by_label:
        return by_label["value"]

    by_role = next((s for s in sels if s.get("type") == "role"), None)
    if by_role:
        return by_role["value"]
    
    by_placeholder = next((s for s in sels if s.get("type") == "placeholder"), None)
    if by_placeholder:
        return by_placeholder["value"]
    
    by_id = next((s for s in sels if s.get("type") == "id"), None)
    if by_id:
        return by_id["value"]


    return el.get("Locator") or (sels[0]["value"] if sels else "")

def label_for(el: Dict[str, Any]) -> str:
    name = norm_space(el.get("Name"))
    text = norm_space(el.get("Text"))
    role = el.get("Role") or el.get("Tag") or "el"
    if name:
        return name
    if text:
        return text
    return f"{role}".strip()

def key_for(el: Dict[str, Any]) -> Tuple[str, str, str]:
    return (
        norm_space(el.get("Role") or el.get("Tag") or ""),
        norm_space(el.get("Name") or el.get("Text") or ""),
        norm_space(el.get("Locator") or "")
    )

def is_interactable(el: Dict[str, Any]) -> bool:
    state = el.get("state", {})
    return bool(state.get("visible", False)) and el.get("Interactability") == "Interactable"

def score(el: Dict[str, Any]) -> int:
    base = ROLE_SCORE.get((el.get("Role") or "").lower(), 40)
    if el.get("controlKind") in {"select", "fill", "check"}:
        base += 10
    if el.get("grid"):
        base += 5
    if len(label_for(el)) >= 3:
        base += 2
    return base

def dedupe(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for el in elements:
        if not is_interactable(el):
            continue
        if (el.get("Role") == "textbox") and norm_space(el.get("Name")).lower() == "search":
            if el.get("grid") is None and any(e.get("Role")=="textbox" and norm_space(e.get("Name")).lower()=="search" and e.get("grid") is None for e in out):
                continue
        k = key_for(el)
        if k in seen:
            continue
        seen.add(k)
        out.append(el)
    return out

def compress_dom(dom_data: Dict[str, Any], token_budget: int = DEFAULT_TOKEN_BUDGET) -> str:
    elements = dom_data.get("elements", [])
    elements = dedupe(elements)

    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for el in elements:
        buckets[bucket_name(el)].append(el)

    for k in buckets:
        buckets[k].sort(key=score, reverse=True)

    total_items = sum(len(v) for v in buckets.values())
    scale = max(0.4, min(1.0, token_budget / max(900, 12 * total_items)))
    max_per_bucket = max(6, int(MAX_PER_BUCKET_BASE * scale))

    output_lines = []


    headers = [label_for(el) for el in buckets.get("table_headers", [])[:max_per_bucket]]
    if headers:
        output_lines.append(f"headers: {', '.join(headers)}")
        output_lines.append("")

    for el in buckets.get("table_filters_row", [])[:max_per_bucket]:
        name = label_for(el)
        role = el.get("Role") or el.get("Tag")
        action = "select" if role == "combobox" else "fill"
        selector = nice_selector(el)
        grid = el.get("grid", {})
        col_idx = grid.get("col", 0)
        field = grid.get("field")
        
        if field:
            selector = f"locator('thead tr').nth(1).locator('[data-field=\"{field}\"]')"
        else:
            selector = f"locator('thead tr').nth(1).locator('th, td').nth({col_idx}).getByRole('{role}')"
            
        output_lines.append(f"{role} | {name} (filter) | {action} | {selector}")


    row_elements = [el for el in elements if isinstance(el.get("grid"), dict) and el["grid"].get("section") == "body"]
    for el in row_elements[:max_per_bucket * 2]:
        grid = el.get("grid", {})
        row_idx = grid.get("row", 0)
        field = grid.get("field")
        role = el.get("Role") or el.get("Tag")
        name = label_for(el)
        
        if role == "checkbox":
            output_lines.append(f"checkbox | row {row_idx + 1}: checkbox | check | locator('tbody tr').nth({row_idx}).getByRole('checkbox')")
        elif field:
            output_lines.append(f"cell | row {row_idx + 1}: {field} | click | locator('tbody tr').nth({row_idx}).locator('[data-field=\"{field}\"]')")
        else:
            action = "select" if role == "combobox" else "check" if role == "checkbox" else "click"
            output_lines.append(f"{role} | row {row_idx + 1}: {name} | {action} | locator('tbody tr').nth({row_idx}).getByRole('{role}', {{ name: '{name}' }})")


    for el in buckets.get("nav_buttons", [])[:max_per_bucket]:
        name = label_for(el)
        selector = nice_selector(el)
        output_lines.append(f"button | {name} | click | {selector}")


    for bucket_type in ["global_search", "textboxes_other", "comboboxes_other", "buttons_other"]:
        for el in buckets.get(bucket_type, [])[:max_per_bucket]:
            name = label_for(el)
            role = el.get("Role") or el.get("Tag")
            action = "select" if role == "combobox" else "fill" if role == "textbox" else "click"
            selector = nice_selector(el)
            output_lines.append(f"{role} | {name} | {action} | {selector}")

    return "\n".join([ln for ln in output_lines if ln.strip()])
