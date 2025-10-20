
(function attachExtractorToWindow() {
  if (typeof window === 'undefined') return;

  const NOW = () => Date.now();
  const toArray = (x) => Array.from(x || []);
  const lower = (x) => (x || '').toString().toLowerCase();
  const squeeze = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const short = (s, n = 120) => { const t = squeeze(s); return t.length > n ? t.slice(0, n - 1) + '…' : t || null; };
  const esc = (s) => String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'");

  const hasHref = (el) => el.tagName === 'A' && el.hasAttribute('href');
  
  function v2Row(type, name, action, selector, elementInfo = {}) {
    return { 
      type, 
      name, 
      action, 
      selector,
      ...elementInfo
    };
  }

  function roleToV2Type(role, tag, element = null) {
    const r = (role || '').toLowerCase();
    const t = (tag || '').toLowerCase();
    const elementType = element?.type ? String(element.type).toLowerCase() : '';
    if (r === 'textbox' || t === 'textarea' || (t === 'input' && !['button','submit','reset','checkbox','radio','file','image'].includes(elementType))) return 'textbox';
    if (r === 'combobox' || t === 'select') return 'combobox';
    if (r === 'checkbox') return 'checkbox';
    if (r === 'radio') return 'radio';
    if (r === 'link') return 'link';
    if (r === 'button' || t === 'button' || (t === 'input' && ['button','submit','reset'].includes(elementType))) return 'button';
    return r || t || 'node';
  }

  function actionFromControlKind(kind) {
    switch (kind) {
      case 'fill': return 'fill';
      case 'select': return 'select';
      case 'check': return 'check';
      case 'uncheck': return 'uncheck';
      default: return 'click';
    }
  }

  function getBasicElementInfo(el) {
    return {
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      classes: el.className || null,
      name: el.name || null,
      type: el.type || null,
      placeholder: el.placeholder || null,
      value: el.value || null,
      text: squeeze(el.innerText || el.textContent || ''),
      role: el.getAttribute('role') || null,
      disabled: el.disabled || el.getAttribute('disabled') !== null,
      visible: isVisible(el)
    };
  }

  function selectorFor(el) {
    const role = roleOf(el);
    const name = getAccessibleName(el);
    if (role && name) return `getByRole('${esc(role)}',{ name:'${esc(name)}' })`;
    if (['INPUT','SELECT','TEXTAREA'].includes(el.tagName)) {
      const lbl = getLabel(el); if (lbl) return `getByLabel('${esc(lbl)}')`;
      if (el.placeholder) return `getByPlaceholder('${esc(el.placeholder)}')`;
    }
    if (el.id) return `locator('#${CSS.escape(el.id)}')`;
    return `locator('${(el.tagName||'').toLowerCase()}')`;
  }

  function pushUnique(arr, row) {
    if (!row || !row.selector) return;
    const key = `${row.type}|${row.name}|${row.action}|${row.selector}`;
    if (!arr.__set) arr.__set = new Set();
    if (!arr.__set.has(key)) { arr.__set.add(key); arr.push(row); }
  }

  function isVisible(el) {
    try {
      const st = getComputedStyle(el);
      if (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0') return false;
      const r = el.getBoundingClientRect();
      if (!r || r.width === 0 || r.height === 0) return false;
      return true;
    } catch { return false; }
  }

  function isInteractive(el) {
    const tag = lower(el.tagName);
    const role = el.getAttribute('role');
    if (['button', 'input', 'select', 'textarea', 'summary'].includes(tag)) return true;
    if (hasHref(el)) return true;
    if (role && ['button', 'link', 'combobox', 'menuitem', 'option', 'tab', 'switch', 'checkbox', 'radio'].includes(lower(role))) return true;
    if (el.onclick != null || el.getAttribute('onclick') != null) return true;
    if (el.tabIndex >= 0) return true;
    return false;
  }

  function getLabelsForInput(input) {
    const labels = [];
    if (input.labels && input.labels.length) labels.push(...input.labels);
    if (input.id) labels.push(...toArray(document.querySelectorAll(`label[for='${CSS.escape(input.id)}']`)));
    let p = input.parentElement;
    while (p) { if (lower(p.tagName) === 'label') { labels.push(p); break; } p = p.parentElement; }
    const aria = input.getAttribute('aria-labelledby');
    if (aria) aria.split(/\s+/).forEach(id => { const el = document.getElementById(id); if (el) labels.push(el); });
    return Array.from(new Set(labels));
  }
  const getLabel = (el) => {
    const ls = getLabelsForInput(el).map(l => squeeze(l.innerText || l.textContent || ''));
    return ls.find(Boolean) || null;
  };

  function getAccessibleName(el) {
    const ariaLabel = el.getAttribute('aria-label');
    if (ariaLabel && squeeze(ariaLabel)) return squeeze(ariaLabel);
    const labelledBy = el.getAttribute('aria-labelledby');
    if (labelledBy) {
      const name = labelledBy.split(/\s+/)
        .map(id => document.getElementById(id))
        .filter(Boolean)
        .map(n => squeeze(n.innerText || n.textContent || ''))
        .filter(Boolean)
        .join(' ');
      if (name) return name;
    }
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName)) {
      const lbl = getLabel(el); if (lbl) return lbl;
      if (el.placeholder) return squeeze(el.placeholder);
    }
    if (el.tagName === 'IMG' && el.alt) return squeeze(el.alt);
    const txt = squeeze(el.innerText || el.textContent || '');
    if (txt) return txt;
    if (el.title) return squeeze(el.title);
    return null;
  }

  function collectTestId(el) {
    const keys = ['data-testid', 'data-test-id', 'data-test', 'data-cy', 'data-qa', 'data-automation-id'];
    for (const k of keys) { const v = el.getAttribute(k); if (v) return { key: k, value: v }; }
    return null;
  }

  function implicitRole(el) {
    const tag = lower(el.tagName);
    if (tag === 'button') return 'button';
    if (tag === 'a' && el.hasAttribute('href')) return 'link';
    if (tag === 'img') return 'img';
    if (tag === 'form') return 'form';
    if (tag === 'select') return 'combobox';
    if (tag === 'textarea') return 'textbox';
    if (tag === 'input') {
      const t = lower(el.type || 'text');
      return ({
        button: 'button', submit: 'button', reset: 'button',
        checkbox: 'checkbox', radio: 'radio', search: 'searchbox',
        password: 'textbox', email: 'textbox', text: 'textbox', number: 'spinbutton'
      }[t]) || null;
    }
    return null;
  }

  function escapeRegex(value) { return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  function firstLabelNearInput(input, maxHops = 3) {
    const parent = input.parentElement;
    if (parent) {
      const lbl = parent.querySelector('label');
      const txt = lbl && (lbl.innerText || lbl.textContent || '').toString().trim();
      if (txt) return { text: txt, container: parent };
    }
    const prev = input.previousElementSibling;
    if (prev && prev.tagName === 'LABEL') {
      const txt = (prev.innerText || prev.textContent || '').toString().trim();
      if (txt) return { text: txt, container: input.parentElement || prev.parentElement || document.body };
    }
    let hop = 0, p = input.parentElement;
    while (p && hop < maxHops) {
      const lbl = p.querySelector('label');
      const txt = lbl && (lbl.innerText || lbl.textContent || '').toString().trim();
      if (txt) return { text: txt, container: p };
      p = p.parentElement; hop++;
    }
    return null;
  }
  function containerTextLocator(container, text, role) {
    const tag = container?.tagName ? container.tagName.toLowerCase() : 'div';
    const safe = escapeRegex(text);
    return `locator('${tag}').filter({ hasText: /^${safe}$/ }).getByRole('${role}')`;
  }

  function roleOf(el) { return (el.getAttribute('role') || implicitRole(el) || '').toLowerCase() || null; }
  function isDisabled(el) {
    if (el.disabled || el.getAttribute('disabled') != null) return true;
    if (el.closest('[aria-disabled="true"], [inert]')) return true;
    const fs = el.closest('fieldset[disabled]'); if (fs && !fs.contains(el.closest('legend'))) return true;
    return false;
  }
  function isReadOnly(el) { return !!(el.readOnly || el.getAttribute('readonly') != null || el.getAttribute('aria-readonly') === 'true'); }
  function isFocusable(el) {
    if (!isVisible(el) || isDisabled(el)) return false;
    const ti = el.tabIndex; return ti >= 0 || /^(input|select|textarea|button|a)$/i.test(el.tagName);
  }
  function isEditable(el) {
    const tag = (el.tagName || '').toLowerCase(); const r = roleOf(el);
    if (isReadOnly(el) || isDisabled(el)) return false;
    if (tag === 'textarea') return true;
    if (tag === 'input') { const t = el.type ? String(el.type).toLowerCase() : 'text'; return !['button', 'submit', 'reset', 'checkbox', 'radio', 'file', 'image'].includes(t); }
    if (el.isContentEditable) return true;
    if (r === 'textbox') return true;
    
    // Rich Text Editor iframe'leri için özel kontrol
    if (tag === 'iframe') {
      const iframeTitle = (el.title || '').toLowerCase();
      const iframeClass = (el.className || '').toLowerCase();
      const iframeId = (el.id || '').toLowerCase();
      
      // TinyMCE ve diğer Rich Text Editor iframe'lerini tespit et
      if (iframeTitle.includes('rich text') || 
          iframeTitle.includes('editor') ||
          iframeClass.includes('tox-edit-area') ||
          iframeClass.includes('editor') ||
          iframeId.includes('editor') ||
          iframeId.includes('jseditor')) {
        return true;
      }
      
      // Iframe içindeki contenteditable kontrolü
      try {
        const iframeDoc = el.contentDocument || el.contentWindow?.document;
        if (iframeDoc) {
          const contentEditable = iframeDoc.querySelector('body[contenteditable="true"], [contenteditable="true"]');
          if (contentEditable) return true;
        }
      } catch (e) {
        // Cross-origin iframe - yine de Rich Text Editor olabilir
        return iframeTitle.includes('rich text') || iframeTitle.includes('editor');
      }
    }
    
    return false;
  }
  function optionsPreview(el, limit = 15) {
    if (el.tagName === 'SELECT') return Array.from(el.options).slice(0, limit).map(o => (o.text || '').trim()).filter(Boolean);
    const listId = el.getAttribute('aria-controls') || el.getAttribute('aria-owns');
    if (listId) { const lb = document.getElementById(listId); if (lb) { const opts = lb.querySelectorAll('[role="option"]'); return Array.from(opts).slice(0, limit).map(o => (o.innerText || o.textContent || '').trim()).filter(Boolean); } }
    return null;
  }
  function controlKind(el) {
    const tag = (el.tagName || '').toLowerCase(); const r = roleOf(el);
    if (r === 'button' || tag === 'button') return 'click';
    if (r === 'link' || (tag === 'a' && hasHref(el))) return 'click';
    if (r === 'checkbox') return el.checked ? 'uncheck' : 'check';
    if (r === 'radio') return 'check';
    if (tag === 'select' || r === 'combobox') return 'select';
    if (isEditable(el)) return 'fill';
    return 'click';
  }
  function actionHint(el) {
    const k = controlKind(el);
    switch (k) {
      case 'fill': 
        // Rich Text Editor iframe'leri için özel action hint
        if (el.tagName === 'IFRAME' && isEditable(el)) {
          return 'richTextFill';
        }
        return 'fill';
      case 'select': return (el.tagName === 'SELECT') ? 'selectOption' : 'openAndPick';
      case 'check': return 'check';
      case 'uncheck': return 'uncheck';
      default: return 'click';
    }
  }
  function selectorCandidates(el) {
    const out = []; const t = collectTestId(el); const r = roleOf(el); const name = getAccessibleName(el);
    if (t) out.push({ type: 'testId', value: `getByTestId('${esc(t.value)}')`, weight: 100 });
    if (r && name) out.push({ type: 'role', value: `getByRole('${esc(r)}',{ name:'${esc(name)}' })`, weight: 90 });
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName)) {
      const lbl = getLabel(el); if (lbl) out.push({ type: 'label', value: `getByLabel('${esc(lbl)}')`, weight: 80 });
      if (el.placeholder) out.push({ type: 'placeholder', value: `getByPlaceholder('${esc(el.placeholder)}')`, weight: 70 });
    }
    if (el.id) out.push({ type: 'id', value: `locator('#${CSS.escape(el.id)}')`, weight: 60 });
    
    // Rich Text Editor iframe'leri için özel selector stratejileri
    if (el.tagName === 'IFRAME' && isEditable(el)) {
      const iframeTitle = el.title || '';
      const iframeClass = el.className || '';
      const iframeId = el.id || '';
      
      // TinyMCE için özel selector'lar
      if (iframeClass.includes('tox-edit-area') || iframeId.includes('jseditor')) {
        out.push({ type: 'richTextIframe', value: `locator('#${CSS.escape(el.id)}').contentLocator('body')`, weight: 95 });
        out.push({ type: 'richTextClass', value: `locator('.tox-edit-area iframe').contentLocator('body')`, weight: 90 });
        out.push({ type: 'richTextTitle', value: `locator('iframe[title*="${esc(iframeTitle)}"]').contentLocator('body')`, weight: 85 });
      }
      
      // Genel Rich Text Editor selector'ları
      if (iframeTitle.toLowerCase().includes('rich text') || iframeTitle.toLowerCase().includes('editor')) {
        out.push({ type: 'richTextTitle', value: `locator('iframe[title*="${esc(iframeTitle)}"]').contentLocator('body')`, weight: 90 });
        out.push({ type: 'richTextIframe', value: `locator('#${CSS.escape(el.id)}').contentLocator('body')`, weight: 85 });
      }
      
      // Fallback selector'lar
      out.push({ type: 'richTextFallback', value: `locator('iframe[title*="Rich Text"]').contentLocator('body')`, weight: 70 });
      out.push({ type: 'richTextFallback2', value: `locator('iframe.tox-edit-area__iframe').contentLocator('body')`, weight: 65 });
    }
    
    out.push({ type: 'css', value: `locator('${(el.tagName || '').toLowerCase()}')`, weight: 10 });
    out.sort((a, b) => b.weight - a.weight); return out;
  }

  function bestLocator(el) {
    const testid = collectTestId(el);
    if (testid) return `getByTestId('${esc(testid.value)}')`;
    
    // Rich Text Editor iframe'leri için özel handling
    if (el.tagName === 'IFRAME' && isEditable(el)) {
      const iframeId = el.id;
      const iframeTitle = el.title || '';
      const iframeClass = el.className || '';
      
      // TinyMCE için öncelikli selector'lar
      if (iframeClass.includes('tox-edit-area') || iframeId.includes('jseditor')) {
        if (iframeId) return `locator('#${CSS.escape(iframeId)}').contentLocator('body')`;
        if (iframeTitle) return `locator('iframe[title*="${esc(iframeTitle)}"]').contentLocator('body')`;
        return `locator('.tox-edit-area iframe').contentLocator('body')`;
      }
      
      // Genel Rich Text Editor selector'ları
      if (iframeTitle.toLowerCase().includes('rich text') || iframeTitle.toLowerCase().includes('editor')) {
        if (iframeId) return `locator('#${CSS.escape(iframeId)}').contentLocator('body')`;
        if (iframeTitle) return `locator('iframe[title*="${esc(iframeTitle)}"]').contentLocator('body')`;
      }
      
      // Fallback
      return `locator('iframe[title*="Rich Text"]').contentLocator('body')`;
    }
    
    const role = el.getAttribute('role') || implicitRole(el); const name = getAccessibleName(el);
    if (role && name) return `getByRole('${esc(role)}', { name: '${esc(name)}' })`;
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName)) {
      const lbl = getLabel(el); if (lbl) return `getByLabel('${esc(lbl)}')`;
      if (el.placeholder) return `getByPlaceholder('${esc(el.placeholder)}')`;
      const near = firstLabelNearInput(el);
      if (near && near.text) {
        const r = el.tagName === 'SELECT' ? 'combobox' : (el.tagName === 'TEXTAREA' ? 'textbox' : (implicitRole(el) || 'textbox'));
        return containerTextLocator(near.container, near.text, r);
      }
    }
    if (el.id) return `locator('#${CSS.escape(el.id)}')`;
    if ((role === 'button' || role === 'link') && name) return `getByRole('${esc(role)}', { name: '${esc(name)}' })`;
    return null;
  }

  function pack(el) {
    const locator = bestLocator(el);
    if (!locator) return null;
    const tag = lower(el.tagName);
    const name = getAccessibleName(el);
    const vis = isVisible(el);
    const inter = isInteractive(el) && vis;

    return {
      Tag: tag,
      Role: roleOf(el),
      ID: el.id || 'N/A',
      Name: short(name),
      Text: short(el.innerText || el.textContent || ''),
      Visibility: vis ? 'Visible' : 'Non-visible',
      Interactability: inter ? 'Interactable' : 'Non-interactable',
      state: {
        visible: vis, disabled: isDisabled(el), readonly: isReadOnly(el),
        focusable: isFocusable(el), editable: isEditable(el),
        expanded: el.getAttribute('aria-expanded') === 'true',
        checked: !!el.checked, required: el.getAttribute('aria-required') === 'true' || !!el.required
      },
      inputType: (el.type || null),
      controlKind: controlKind(el),
      actionHint: actionHint(el),
      selectors: selectorCandidates(el),
      Locator: locator,
      optionsPreview: optionsPreview(el)
    };
  }

  function getTableColumnSelectors(table, headerText, filterInput) {
    const selectors = [];
    const role = roleOf(filterInput);
    const isNativeSelect = (filterInput.tagName || '').toLowerCase() === 'select';
    const isCombo = role === 'combobox' || isNativeSelect;


    const ariaLabel = filterInput.getAttribute('aria-label');
    if (ariaLabel) {
      const ariaRole = isCombo ? 'combobox' : 'textbox';
      selectors.push(`getByRole('${ariaRole}', { name: '${esc(ariaLabel)}' })`);
    }

    if (isCombo) {
      selectors.push(`getByRole('cell', { name: '${esc(headerText)}' }).getByRole('combobox')`);
      selectors.push(`getByRole('cell', { name: '${esc(headerText)}' }).locator('[role="combobox"]')`);
    } else {
      selectors.push(`getByRole('cell', { name: '${esc(headerText)}' }).getByRole('textbox')`);
    }


    if (filterInput.placeholder) {
      selectors.push(`getByPlaceholder('${esc(filterInput.placeholder)}')`);
    }


    const dataField = filterInput.getAttribute('data-field');
    if (dataField) {
      selectors.push(`locator('[data-field="${esc(dataField)}"]')`);
    }


    if (!isCombo && filterInput.classList.contains('p-inputtext')) {
      selectors.push(`locator('.p-inputtext')`);
    }

    return selectors;
  }

function chain(scope, child) { return child ? `${scope}.${child}` : scope; }


function rowScopeForFilterRow(table, filterRow) {
  const pickIdx = (parent, sel) => {
    const rows = Array.from(parent.querySelectorAll(sel));
    const i = rows.indexOf(filterRow);
    return i >= 0 ? i : null;
  };

  if (table.tHead && table.tHead.contains(filterRow)) {
    const i = pickIdx(table.tHead, 'tr');
    if (i !== null) return `locator('thead tr').nth(${i})`;
  }
  if (table.tBodies[0] && table.tBodies[0].contains(filterRow)) {
    const i = pickIdx(table.tBodies[0], 'tr');
    if (i !== null) return `locator('tbody tr').nth(${i})`;
  }
  const rg = filterRow.closest('[role="rowgroup"]');
  if (rg && rg.parentElement) {
    const rows = Array.from(rg.querySelectorAll('[role="row"]'));
    const i = rows.indexOf(filterRow);
    if (i >= 0) return `locator('[role="rowgroup"] [role="row"]').nth(${i})`;
  }

  const rows = Array.from(table.querySelectorAll('tr'));
  const i = rows.indexOf(filterRow);
  return `locator('tr').nth(${i})`;
}


const getField = (el) =>
  (el && (el.getAttribute?.('data-field') || (el.dataset && el.dataset.field))) || null;


function extractTableBodyElements() {
  const out = [];
  const tables = Array.from(document.querySelectorAll('table'));

  tables.forEach((table, tIndex) => {
    const tbody = table.querySelector('tbody');
    if (!tbody) return;

    const headerRow = table.querySelector('thead tr') ||
      Array.from(table.querySelectorAll('tr')).find(tr => tr.querySelector('th'));
    if (!headerRow) return;

    const headerCells = Array.from(headerRow.querySelectorAll('th'));
    const headers = headerCells.map(th => (th.innerText || th.textContent || '').replace(/\s+/g, ' ').trim());

    Array.from(tbody.querySelectorAll('tr')).forEach((row, rowIndex) => {
      const rowCheckbox = row.querySelector('input[type="checkbox"], [role="checkbox"]');
      if (rowCheckbox) {
        out.push({
          Tag: rowCheckbox.tagName.toLowerCase(),
          Role: 'checkbox',
          Name: `row ${rowIndex + 1}: checkbox`,
          grid: { table: tIndex, section: 'body', row: rowIndex },
          Locator: `locator('tbody tr').nth(${rowIndex}).getByRole('checkbox')`,
          state: { visible: isVisible(rowCheckbox) }
        });
      }

      Array.from(row.children).forEach((cell, colIndex) => {
        const cellContent = (cell.innerText || cell.textContent || '').trim();
        const headerText = headers[colIndex] || `Column ${colIndex + 1}`;
        const field = getField(cell) || getField(headerCells[colIndex]);

        if (field) {
          out.push({
            Tag: cell.tagName.toLowerCase(),
            Role: 'cell',
            Name: `row ${rowIndex + 1}: ${field} (row ${rowIndex + 1})`,
            Text: cellContent,
            grid: { table: tIndex, section: 'body', row: rowIndex, col: colIndex, field, header: headerText },
            Locator: `locator('tbody tr').nth(${rowIndex}).locator('[data-field="${field}"]')`,
            state: { visible: isVisible(cell) }
          });
        }

        const interactives = cell.querySelectorAll('button, a, input, select, [role="button"], [role="link"]');
        Array.from(interactives).forEach(el => {
          const packed = pack(el);
          if (packed) {
            packed.grid = { table: tIndex, section: 'body', row: rowIndex, col: colIndex, field, header: headerText };
            packed.Name = `row ${rowIndex + 1}: ${packed.Name}`;
            if (field) {
              packed.Locator = `locator('tbody tr').nth(${rowIndex}).locator('[data-field="${field}"]')${packed.Role ? `.getByRole('${packed.Role}')` : ''}`;
            }
            out.push(packed);
          }
        });
      });
    });
  });
  return out;
}

function tableFilterElements() {
  const out = [];
  const tables = Array.from(document.querySelectorAll('table'));

  tables.forEach((table, tIndex) => {
    const headerRow = table.querySelector('thead tr') ||
      Array.from(table.querySelectorAll('tr')).find(tr => tr.querySelector('th'));
    if (!headerRow) return;

    const headerCells = Array.from(headerRow.querySelectorAll('th'));
    const headers = headerCells.map(th => (th.innerText || th.textContent || '').replace(/\s+/g, ' ').trim());

    const allRows = Array.from(table.querySelectorAll('tr'));
    const filterRow = allRows.find(tr => tr !== headerRow && tr.querySelector('input, select, [role="combobox"], span[role="combobox"]'));
    if (!filterRow) return;

    const rowScope = rowScopeForFilterRow(table, filterRow);
    const cells = Array.from(filterRow.children);

    headers.forEach((headerText, colIdx) => {
      const cell = cells[colIdx]; if (!cell) return;
      const ctrl = cell.querySelector('input, select, [role="combobox"], span[role="combobox"]'); if (!ctrl) return;

      const role = (ctrl.getAttribute('role') || implicitRole(ctrl) || '').toLowerCase();
      const isNativeSelect = (ctrl.tagName || '').toLowerCase() === 'select';
      const isCombo = role === 'combobox' || isNativeSelect;

      const field =
        getField(ctrl) || getField(cell) || getField(headerCells[colIdx]) || null;

      const locator = field
        ? `locator('thead tr').nth(1).locator('[data-field="${esc(field)}"]')`
        : `locator('thead tr').nth(1).locator('th, td').nth(${colIdx}).getByRole('${isCombo ? 'combobox' : 'textbox'}')`;

      const opts = optionsPreview(ctrl);

      out.push({
        Tag: (ctrl.tagName || '').toLowerCase(),
        Role: role || (isNativeSelect ? 'combobox' : 'textbox'),
        Name: `${headerText} (filter)`,
        grid: { table: tIndex, section: 'filter', col: colIdx, field, header: headerText },
        Locator: locator,
        controlKind: isCombo ? 'select' : 'fill',
        optionsPreview: opts || undefined,
      });
    });
  });
  return out;
}

  function extractRichTextEditors() {
    const richTextEditors = [];
    
    // Tüm iframe'leri kontrol et (Rich Text Editor olabilecek)
    const allIframes = Array.from(document.querySelectorAll('iframe'));
    
    allIframes.forEach(iframe => {
      if (!isVisible(iframe)) return;
      
      // Rich Text Editor iframe'lerini tespit et
      const iframeTitle = (iframe.title || '').toLowerCase();
      const iframeClass = (iframe.className || '').toLowerCase();
      const iframeId = (iframe.id || '').toLowerCase();
      
      const isRichTextEditor = iframeTitle.includes('rich text') || 
                              iframeTitle.includes('editor') ||
                              iframeClass.includes('tox-edit-area') ||
                              iframeClass.includes('editor') ||
                              iframeId.includes('editor') ||
                              iframeId.includes('jseditor');
      
      if (!isRichTextEditor) return;
      
      try {
        // Iframe içindeki contenteditable element'i bul
        const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
        if (!iframeDoc) return;
        
        const contentEditable = iframeDoc.querySelector('body[contenteditable="true"], [contenteditable="true"]');
        if (contentEditable) {
          const elementInfo = getBasicElementInfo(iframe);
          const editorName = iframe.title || iframe.getAttribute('aria-label') || 'Rich Text Editor';
          
          // En iyi selector'ı seç
          let bestSelector = '';
          if (iframe.id) {
            bestSelector = `locator('#${CSS.escape(iframe.id)}').contentLocator('body')`;
          } else if (iframeTitle) {
            bestSelector = `locator('iframe[title*="${esc(iframeTitle)}"]').contentLocator('body')`;
          } else if (iframeClass.includes('tox-edit-area')) {
            bestSelector = `locator('.tox-edit-area iframe').contentLocator('body')`;
          } else {
            bestSelector = `locator('iframe.tox-edit-area__iframe').contentLocator('body')`;
          }
          
          pushUnique(richTextEditors, v2Row('textbox', editorName, 'richTextFill', bestSelector, {
            ...elementInfo,
            isRichTextEditor: true,
            iframeId: iframe.id,
            contentEditable: true,
            iframeTitle: iframe.title,
            iframeClass: iframe.className
          }));
        }
      } catch (e) {
        // Cross-origin iframe - yine de Rich Text Editor olabilir
        const elementInfo = getBasicElementInfo(iframe);
        const editorName = iframe.title || 'Rich Text Editor';
        
        let bestSelector = '';
        if (iframe.id) {
          bestSelector = `locator('#${CSS.escape(iframe.id)}').contentLocator('body')`;
        } else if (iframeTitle) {
          bestSelector = `locator('iframe[title*="${esc(iframeTitle)}"]').contentLocator('body')`;
        } else {
          bestSelector = `locator('iframe[title*="Rich Text"]').contentLocator('body')`;
        }
        
        pushUnique(richTextEditors, v2Row('textbox', editorName, 'richTextFill', bestSelector, {
          ...elementInfo,
          isRichTextEditor: true,
          iframeId: iframe.id,
          requiresJSInjection: true,
          iframeTitle: iframe.title,
          iframeClass: iframe.className
        }));
      }
    });
    
    // Diğer Rich Text Editor türleri (iframe olmayan)
    const otherRichEditors = Array.from(document.querySelectorAll('[contenteditable="true"]:not(iframe)'))
      .filter(el => {
        const parent = el.closest('.tox-edit-area, .editor, .rich-text, [class*="editor"]');
        return parent && isVisible(el);
      });
    
    otherRichEditors.forEach(editor => {
      const elementInfo = getBasicElementInfo(editor);
      const editorName = editor.getAttribute('aria-label') || editor.title || 'Rich Text Editor';
      
      pushUnique(richTextEditors, v2Row('textbox', editorName, 'fill', 
        `locator('[contenteditable="true"]')`, {
          ...elementInfo,
          isRichTextEditor: true,
          contentEditable: true
        }));
    });
    
    return richTextEditors;
  }

  function collectSpecialV2() {
    const v2 = [];

    // --- RICH TEXT EDITORS ---
    const richTextEditors = extractRichTextEditors();
    richTextEditors.forEach(editor => pushUnique(v2, editor));

    // --- OCCUPANCY ---
    const occBtn = document.querySelector('button.form-control, [data-toggle="dropdown"].header-rmsearch-input');
    if (occBtn && isVisible(occBtn)) {
      const elementInfo = getBasicElementInfo(occBtn);
      pushUnique(v2, v2Row('button', getAccessibleName(occBtn) || '1 Adult, 1 Room', 'click', 
        `getByRole('button',{ name:'${esc(getAccessibleName(occBtn)||'1 Adult, 1 Room')}' })`, elementInfo));
    }

    const overlay = document.querySelector('#detected-overlay, .p-overlaypanel, [role="menu"], [role="dialog"]');

    const up = document.querySelector('#detected-overlay .occupancy_quantity_up, .occupancy_quantity_up');
    if (up && isVisible(up)) {
      const elementInfo = getBasicElementInfo(up);
      pushUnique(v2, v2Row('button', '+ Adults', 'click', `locator('#detected-overlay .occupancy_quantity_up, .occupancy_quantity_up')`, elementInfo));
    }

    const down = document.querySelector('#detected-overlay .occupancy_quantity_down, .occupancy_quantity_down');
    if (down && isVisible(down)) {
      const elementInfo = getBasicElementInfo(down);
      pushUnique(v2, v2Row('button', '- Adults', 'click', `locator('#detected-overlay .occupancy_quantity_down, .occupancy_quantity_down')`, elementInfo));
    }

    const done = document.querySelector('button.submit_occupancy_btn, [role="menu"] .submit_occupancy_btn');
    if (done && isVisible(done)) {
      const doneName = getAccessibleName(done) || 'Done';
      const sel = done.getAttribute('role') === 'button'
        ? `getByRole('button',{ name:'${esc(doneName)}' })`
        : `locator('button.submit_occupancy_btn')`;
      const elementInfo = getBasicElementInfo(done);
      pushUnique(v2, v2Row('button', doneName, 'click', sel, elementInfo));
    }

    // --- DATEPICKER ---
    const dateInputs = Array.from(document.querySelectorAll('input, [role="textbox"]'))
      .filter(el => {
        const name = (getAccessibleName(el)||'').toLowerCase();
        const ph = (el.placeholder||'').toLowerCase();
        return isVisible(el) && (
          /check[\s-]?in|check[\s-]?out|date|dates|check\-in|check\-out/.test(name) ||
          /check[\s-]?in|check[\s-]?out|date/.test(ph)
        );
      });

    dateInputs.forEach(el => {
      pushUnique(v2, v2Row('textbox', getAccessibleName(el) || el.placeholder || 'Check-in / Check-out', 'click',
        selectorFor(el)));
    });

    const calendarGrid = document.querySelector('[role="grid"][aria-label*="Calendar" i], .datepicker, .ui-datepicker-calendar, .p-datepicker-calendar');
    if (calendarGrid && isVisible(calendarGrid)) {
      pushUnique(v2, v2Row('grid', 'Calendar', 'none', `getByRole('grid',{ name:'Calendar' })`));
      const dayButtons = Array.from(calendarGrid.querySelectorAll('[role="button"], button'))
        .filter(b => isVisible(b) && /^\d{1,2}$/.test((b.innerText||b.textContent||'').toString().trim()))
        .slice(0, 6);
      dayButtons.forEach(b => {
        const day = (b.innerText||b.textContent||'').toString().trim();
        pushUnique(v2, v2Row('button', day, 'click', `getByRole('button',{ name:'${esc(day)}' })`));
      });
    }

    // --- CHOSEN.JS DROPDOWNS ---
    const chosenSelects = Array.from(document.querySelectorAll('select.chosen, select[data-placeholder]'));
    chosenSelects.forEach(select => {
      if (isVisible(select)) {
        const placeholder = select.getAttribute('data-placeholder') || 'Select option';
        const chosenContainer = document.querySelector(`#${select.id}_chosen`);
        if (chosenContainer) {
          const elementInfo = getBasicElementInfo(select);
          pushUnique(v2, v2Row('combobox', placeholder, 'select', `locator('#${CSS.escape(select.id)}')`, elementInfo));
        }
      }
    });

    // --- CHOSEN.JS CONTAINERS ---
    const chosenContainers = Array.from(document.querySelectorAll('.chosen-container, [id$="_chosen"]'));
    chosenContainers.forEach(container => {
      if (isVisible(container)) {
        const selectId = container.id.replace('_chosen', '');
        const originalSelect = document.getElementById(selectId);
        if (originalSelect) {
          const placeholder = originalSelect.getAttribute('data-placeholder') || 'Select option';
          const elementInfo = getBasicElementInfo(container);
          pushUnique(v2, v2Row('combobox', placeholder, 'select', `locator('#${CSS.escape(selectId)}')`, elementInfo));
        }
      }
    });

    // --- SEARCH ROOMS ---
    const searchBtn = Array.from(document.querySelectorAll('button, [role="button"]'))
      .find(b => isVisible(b) && /search rooms/i.test(getAccessibleName(b)||''));
    if (searchBtn) {
      const elementInfo = getBasicElementInfo(searchBtn);
      pushUnique(v2, v2Row('button', 'SEARCH ROOMS', 'click', `getByRole('button',{ name:'SEARCH ROOMS' })`, elementInfo));
    }

    // --- ALL CHECKBOXES (AGGRESSIVE) ---
    const allCheckboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
    allCheckboxes.forEach(checkbox => {
      // Görünürlük kontrolünü gevşetelim
      const isCheckboxVisible = isVisible(checkbox) || 
                                checkbox.offsetParent !== null || 
                                checkbox.getBoundingClientRect().width > 0;
      
      if (isCheckboxVisible) {
        let labelText = '';
        
        // 1. Filter checkbox'ları için özel kontrol
        if (checkbox.classList.contains('filter') || checkbox.hasAttribute('data-type')) {
          // Önce .layered_filt container'ını bul
          let parent = checkbox.closest('.layered_filt');
          if (parent) {
            labelText = parent.querySelector('.filters_name')?.textContent?.trim() || '';
          }
          
          // Eğer bulamazsa, daha geniş arama yap
          if (!labelText) {
            parent = checkbox.closest('div');
            if (parent) {
              // Parent container'daki tüm text'leri topla
              const allText = parent.textContent?.trim() || '';
              // Checkbox'ın kendisini ve boşlukları çıkar
              const cleanText = allText.replace(checkbox.value || '', '').replace(/\s+/g, ' ').trim();
              if (cleanText && cleanText.length < 50) {
                labelText = cleanText;
              }
            }
          }
          
        }
        
        // 2. Genel checkbox'lar için
        if (!labelText) {
          labelText = getAccessibleName(checkbox) || 
                     checkbox.closest('label')?.textContent?.trim() ||
                     checkbox.getAttribute('aria-label') ||
                     checkbox.getAttribute('title') ||
                     `Checkbox ${checkbox.value || ''}`.trim();
        }
        
        // 3. Parent container'dan text bul
        if (!labelText) {
          const parent = checkbox.parentElement;
          if (parent) {
            const textNodes = Array.from(parent.childNodes)
              .filter(node => node.nodeType === Node.TEXT_NODE)
              .map(node => node.textContent.trim())
              .filter(text => text.length > 0);
            labelText = textNodes[0] || '';
          }
        }
        
        // 4. Sibling element'lerden text bul
        if (!labelText) {
          const siblings = Array.from(checkbox.parentElement?.children || []);
          const textSibling = siblings.find(sibling => 
            sibling !== checkbox && 
            sibling.textContent?.trim() && 
            !sibling.querySelector('input, select, button')
          );
          labelText = textSibling?.textContent?.trim() || '';
        }
        
        if (labelText) {
          const elementInfo = getBasicElementInfo(checkbox);
          const selector = checkbox.id ? 
            `locator('#${CSS.escape(checkbox.id)}')` : 
            `locator('input[type="checkbox"][value="${checkbox.value}"]')`;
          pushUnique(v2, v2Row('checkbox', labelText, 'check', selector, elementInfo));
        }
      }
    });

    return v2;
  }

  async function waitForTableLoad(maxWait = 5000) {
    const t0 = NOW();
    while (NOW() - t0 < maxWait) {
      const tables = document.querySelectorAll('table');
      let allTablesLoaded = true;
      
      for (const table of tables) {
        const hasRows = table.querySelector('tbody tr');
        const hasFilters = table.querySelector('thead tr:nth-child(2)');
        if (!hasRows && !hasFilters) {
          allTablesLoaded = false;
          break;
        }
      }
      
      if (allTablesLoaded) return true;
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    return false;
  }

  async function extractPageForPlaywright(opts = {}) {
    const {
      onlyInteractives = true,
      includeHidden = false,
      waitForTables = true,
    } = opts;

    const t0 = NOW();
    
    if (waitForTables) {
      await waitForTableLoad();
    }
    
    const all = toArray(document.querySelectorAll('*'));
    const filtered = all.filter(el => (!onlyInteractives || isInteractive(el)) && (includeHidden || isVisible(el)));

    const elements = [];
    for (const el of filtered) { try { const p = pack(el); if (p) elements.push(p); } catch { } }

    const filterEls = tableFilterElements();
    const tableBodyEls = extractTableBodyElements();
    const merged = elements.concat(filterEls, tableBodyEls);

    const v2 = [];

    for (const it of elements) {
      try {
        const type = roleToV2Type(it.Role, it.Tag, null);
        const name = it.Name || it.Text || it.ID || '';
        if (!name) continue;
        const action = actionFromControlKind(it.controlKind);
        const sel = (it.selectors && it.selectors.find(s => s.type === 'role')?.value) || it.Locator;
        
        if (sel) {
          // Element referansını bul ve temel bilgileri al
          const el = document.getElementById(it.ID) || 
                    document.querySelector(`[data-testid="${it.ID}"]`) ||
                    document.querySelector(`#${it.ID}`) ||
                    null;
          
          const elementInfo = el ? getBasicElementInfo(el) : {
            tag: it.Tag,
            id: it.ID,
            classes: null,
            name: null,
            type: it.inputType,
            text: it.Text,
            visible: it.state?.visible || false
          };
          
          pushUnique(v2, v2Row(type, name, action, sel, elementInfo));
        }
      } catch {}
    }

    const special = collectSpecialV2();
    special.forEach(x => pushUnique(v2, x));

    v2.sort((a,b) => {
      const order = { textbox: 1, combobox: 2, checkbox: 3, radio: 4, link: 5, button: 6, grid: 7, node: 99 };
      return (order[a.type]||50) - (order[b.type]||50) || String(a.name).localeCompare(String(b.name));
    });

    return {
      meta: { url: location.href, title: document.title, lang: document.documentElement.getAttribute('lang') || 'N/A' },
      summary: { totalElements: all.length, scanned: filtered.length, visibleCount: merged.length, domV2: v2.length },
      elements: merged,
      domDataV2: v2,
      timingMs: NOW() - t0
    };
  }

  // Rich Text Editor tespitini test etmek için fonksiyon
  function testRichTextEditorDetection() {
    const results = {
      iframes: [],
      richTextEditors: [],
      contentEditables: []
    };
    
    // Tüm iframe'leri kontrol et
    const allIframes = Array.from(document.querySelectorAll('iframe'));
    allIframes.forEach(iframe => {
      const iframeInfo = {
        id: iframe.id,
        title: iframe.title,
        className: iframe.className,
        visible: isVisible(iframe),
        isRichTextEditor: false,
        hasContentEditable: false
      };
      
      // Rich Text Editor kontrolü
      const iframeTitle = (iframe.title || '').toLowerCase();
      const iframeClass = (iframe.className || '').toLowerCase();
      const iframeId = (iframe.id || '').toLowerCase();
      
      iframeInfo.isRichTextEditor = iframeTitle.includes('rich text') || 
                                   iframeTitle.includes('editor') ||
                                   iframeClass.includes('tox-edit-area') ||
                                   iframeClass.includes('editor') ||
                                   iframeId.includes('editor') ||
                                   iframeId.includes('jseditor');
      
      // Iframe içindeki contenteditable kontrolü
      try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
        if (iframeDoc) {
          const contentEditable = iframeDoc.querySelector('body[contenteditable="true"], [contenteditable="true"]');
          iframeInfo.hasContentEditable = !!contentEditable;
        }
      } catch (e) {
        iframeInfo.crossOrigin = true;
      }
      
      results.iframes.push(iframeInfo);
      
      if (iframeInfo.isRichTextEditor) {
        results.richTextEditors.push(iframeInfo);
      }
    });
    
    // Contenteditable elementleri kontrol et
    const contentEditables = Array.from(document.querySelectorAll('[contenteditable="true"]'));
    contentEditables.forEach(el => {
      const parent = el.closest('.tox-edit-area, .editor, .rich-text, [class*="editor"]');
      if (parent) {
        results.contentEditables.push({
          tagName: el.tagName,
          id: el.id,
          className: el.className,
          visible: isVisible(el),
          parentClass: parent.className,
          isInIframe: el.closest('iframe') !== null
        });
      }
    });
    
    return results;
  }

  window.__extractPageForPlaywright = extractPageForPlaywright;
  try { globalThis.__extractPageForPlaywright = extractPageForPlaywright; } catch { }
  window.__waitForTableLoad = waitForTableLoad;
  window.__testRichTextEditorDetection = testRichTextEditorDetection;
  window.__extractorReady__ = true;
})();
