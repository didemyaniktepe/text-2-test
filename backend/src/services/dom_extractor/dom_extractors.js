
function detectActiveOverlays() {
    const overlayElements = [];
    
    const commonOverlaySelectors = [
        '.p-overlaypanel, .p-dropdown-panel, .p-menu',
        '[role="dialog"][aria-modal="true"]',
        '[role="menu"], [role="listbox"], [role="combobox"]',
        
        '.dropdown-menu, .popover, .tooltip',
        '.modal, .overlay, .popup',
        
        '.MuiPopover-root, .MuiMenu-root, .MuiSelect-menu',
        
        '.ant-dropdown, .ant-select-dropdown, .ant-menu',
        
        '[class*="dropdown"], [class*="menu"], [class*="popup"]',
        '[class*="overlay"], [class*="popover"], [class*="tooltip"]'
    ];
    
    commonOverlaySelectors.forEach(selector => {
        try {
            const elements = Array.from(document.querySelectorAll(selector));
            elements.forEach(element => {
                if (isElementVisible(element) && hasInteractiveContent(element) && isAlreadyOpen(element)) {
                    overlayElements.push(element);
                }
            });
        } catch (e) {
        }
    });
    
    const allElements = Array.from(document.querySelectorAll('*'));
    allElements.forEach(element => {
        const style = window.getComputedStyle(element);
        
        if ((style.position === 'absolute' || style.position === 'fixed') &&
            style.zIndex > 100 &&
            isElementVisible(element) &&
            hasInteractiveContent(element) &&
            !overlayElements.includes(element)) {
            
            overlayElements.push(element);
        }
    });
    
    return overlayElements;
}

function isElementVisible(element) {
    const rect = element.getBoundingClientRect();
    const style = window.getComputedStyle(element);
    
    return (
        rect.width > 0 &&
        rect.height > 0 &&
        style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        style.opacity !== '0' &&
        element.offsetParent !== null
    );
}

function isAlreadyOpen(element) {
    if (element.classList.contains('modal')) {
        return element.classList.contains('show') || 
               element.style.display === 'block' || 
               element.getAttribute('aria-modal') === 'true';
    }
    
    if (element.classList.contains('dropdown-menu')) {
        return element.classList.contains('show') || 
               element.style.display === 'block';
    }
    
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && 
           style.visibility !== 'hidden' && 
           style.opacity !== '0';
}

function hasInteractiveContent(element) {
    const interactiveSelectors = [
        'button', 'a', 'input', 'select', 'textarea',
        
        '[role="button"]', '[role="menuitem"]', '[role="option"]',
        '[role="menu"]', '[role="menubar"]', '[role="tab"]',
        
        '[tabindex]', '[onclick]', '[aria-haspopup]',
        '[aria-expanded]', '[aria-controls]',
        
        '[class*="item"]', '[class*="option"]', '[class*="choice"]',
        '[class*="menu"]', '[class*="dropdown"]',
        
        'img.pointer', 'img[data-pd-tooltip]', '[data-pd-tooltip]',
        '[title]', '[data-tooltip]', '[aria-label]',
        
        '[class*="menu-item"]', '[id*="menu"]', '[class*="more"]',
        '.details-menu', '.action-buttons'
    ];
    
    for (let selector of interactiveSelectors) {
        if (element.matches(selector)) return true;
    }
    
    for (let selector of interactiveSelectors) {
        if (element.querySelector(selector)) return true;
    }
    
    const text = element.innerText?.trim() || '';
    const style = window.getComputedStyle(element);
    
    return text.length > 0 && text.length < 200 && 
           (style.cursor === 'pointer' || element.onclick);
}

function extractMenuItems(overlayElement) {
    const menuItems = [];
    
    const itemSelectors = [
        '[role="menuitem"], [role="option"]',
        'li, .item, .option, .choice',
        '[class*="item"], [class*="option"], [class*="choice"]',
        'a, button',
        
        '.p-menuitem, .ant-dropdown-menu-item',
        '.MuiMenuItem-root, .dropdown-item',
        
        '[data-value], [data-option], [data-item]'
    ];
    
    itemSelectors.forEach(selector => {
        try {
            const items = Array.from(overlayElement.querySelectorAll(selector));
            items.forEach(item => {
                const text = getElementText(item);
                if (text && text.length > 0 && text.length < 100) {
                    menuItems.push({
                        text: text,
                        classes: item.className,
                        tagName: item.tagName.toLowerCase(),
                        selectors: [
                            `text="${text}"`,
                            ...getTestingLibrarySelectors(item)
                        ],
                        isClickable: isElementClickable(item),
                        dataAttributes: getDataAttributes(item)
                    });
                }
            });
        } catch (e) {
        }
    });

    const uniqueItems = [];
    const seenTexts = new Set();
    
    menuItems.forEach(item => {
        if (!seenTexts.has(item.text)) {
            seenTexts.add(item.text);
            uniqueItems.push(item);
        }
    });
    
    return uniqueItems;
}

function getElementText(element) {
    let text = element.innerText?.trim() || '';
    
    if (!text) {
        const textNodes = Array.from(element.childNodes)
            .filter(node => node.nodeType === Node.TEXT_NODE)
            .map(node => node.textContent.trim())
            .filter(t => t.length > 0);
        
        text = textNodes.join(' ');
    }
    
    return text;
}

function isElementClickable(element) {
    const clickableElements = ['button', 'a', 'input'];
    const clickableRoles = ['button', 'menuitem', 'option'];
    const style = window.getComputedStyle(element);
    
    return (
        clickableElements.includes(element.tagName.toLowerCase()) ||
        clickableRoles.includes(element.getAttribute('role')) ||
        element.onclick ||
        element.getAttribute('onclick') ||
        style.cursor === 'pointer' ||
        element.tabIndex >= 0
    );
}

function getDataAttributes(element) {
    const dataAttrs = {};
    Array.from(element.attributes).forEach(attr => {
        if (attr.name.startsWith('data-')) {
            dataAttrs[attr.name] = attr.value;
        }
    });
    return dataAttrs;
}

function extractDynamicContent() {
    const dynamicElements = [];
    
    const activeOverlays = detectActiveOverlays();
    
    activeOverlays.forEach(overlay => {
        const menuItems = extractMenuItems(overlay);
        
        if (menuItems.length > 0) {
            dynamicElements.push({
                type: 'overlay_panel',
                trigger: {
                    text: `Active Menu (${menuItems.length} items)`,
                    classes: overlay.className,
                    tag: overlay.tagName.toLowerCase(),
                    selectors: getTestingLibrarySelectors(overlay)
                },
                menuItems: menuItems,
                isVisible: true,
                panelId: overlay.id || 'detected-overlay',
                overlayType: detectOverlayType(overlay)
            });
        }
    });
    
    const dropdowns = Array.from(document.querySelectorAll('.dropdown, [role="menu"], [aria-haspopup]'));
    
    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('[data-toggle], [aria-haspopup], .dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu, [role="menu"], ul, ol');
        
        if (trigger && menu) {
            const menuItems = Array.from(menu.querySelectorAll('a, button, li')).map(item => ({
                text: (item.innerText || '').trim(),
                href: item.href || null,
                selectors: getTestingLibrarySelectors(item)
            }));
            
            dynamicElements.push({
                type: 'dropdown',
                trigger: {
                    text: (trigger.innerText || '').trim(),
                    selectors: getTestingLibrarySelectors(trigger)
                },
                menuItems: menuItems
            });
        }
    });
    
    const lazyImages = Array.from(document.querySelectorAll('img[loading="lazy"], img[data-src]'));
    const ajaxContainers = Array.from(document.querySelectorAll('[data-url], [data-ajax], .ajax-content'));
    const scrollContainers = Array.from(document.querySelectorAll('[data-infinite], .infinite-scroll'));
    
    return {
        lazyImages: lazyImages.length,
        ajaxContainers: ajaxContainers.length,
        scrollContainers: scrollContainers.length,
        dropdowns: dynamicElements
    };
}

function detectOverlayType(element) {
    const className = String(element.className || '').toLowerCase();
    
    if (className.includes('dropdown')) return 'dropdown';
    if (className.includes('menu')) return 'menu';
    if (className.includes('popup') || className.includes('popover')) return 'popup';
    if (className.includes('modal') || className.includes('dialog')) return 'modal';
    if (element.getAttribute('role') === 'menu') return 'menu';
    if (element.getAttribute('role') === 'dialog') return 'dialog';
    
    return 'overlay';
}


function getLabelsForInput(input) {
    const labels = [];
    if (input.id) {
        const forLabels = Array.from(document.querySelectorAll(`label[for='${input.id}']`));
        labels.push(...forLabels);
    }
    let parent = input.parentElement;
    while (parent) {
        if (parent.tagName && parent.tagName.toLowerCase() === 'label') {
            labels.push(parent);
            break;
        }
        parent = parent.parentElement;
    }
    const ariaLabelledBy = input.getAttribute('aria-labelledby');
    if (ariaLabelledBy) {
        ariaLabelledBy.split(' ').forEach(id => {
            const el = document.getElementById(id);
            if (el) labels.push(el);
        });
    }
    return labels;
}

function getImplicitRole(element) {
    const tag = element.tagName.toLowerCase();
    const type = element.type ? String(element.type).toLowerCase() : null;
    
    const roleMap = {
        'button': 'button',
        'a': element.href ? 'link' : null,
        'input': {
            'button': 'button',
            'submit': 'button',
            'reset': 'button',
            'checkbox': 'checkbox',
            'radio': 'radio',
            'text': 'textbox',
            'email': 'textbox',
            'password': 'textbox',
            'search': 'searchbox',
            'tel': 'textbox',
            'url': 'textbox',
            'number': 'spinbutton'
        },
        'textarea': 'textbox',
        'select': 'combobox',
        'h1': 'heading',
        'h2': 'heading',
        'h3': 'heading',
        'h4': 'heading',
        'h5': 'heading',
        'h6': 'heading',
        'img': 'img',
        'nav': 'navigation',
        'main': 'main',
        'header': 'banner',
        'footer': 'contentinfo',
        'aside': 'complementary',
        'section': 'region',
        'article': 'article',
        'form': 'form',
        'table': 'table',
        'ul': 'list',
        'ol': 'list',
        'li': 'listitem'
    };
    
    if (tag === 'input' && type) {
        return roleMap[tag][type] || null;
    }
    
    return roleMap[tag] || null;
}

function getAccessibleName(element) {
    const ariaLabel = element.getAttribute('aria-label');
    if (ariaLabel) return String(ariaLabel).trim();
    
    const ariaLabelledBy = element.getAttribute('aria-labelledby');
    if (ariaLabelledBy) {
        const labelElements = ariaLabelledBy.split(' ')
            .map(id => document.getElementById(id))
            .filter(el => el)
            .map(el => (el.innerText || '').trim())
            .join(' ');
        if (labelElements) return labelElements;
    }
    
    if (['input', 'select', 'textarea'].includes(element.tagName.toLowerCase())) {
        const label = getElementLabel(element);
        if (label) return label;
    }
    
    if (element.tagName.toLowerCase() === 'button' || element.getAttribute('role') === 'button') {
        const text = (element.innerText || '').trim();
        if (text) return text;
    }
    
    if (element.tagName.toLowerCase() === 'a') {
        const text = (element.innerText || '').trim();
        if (text) return text;
    }
    
    if (element.tagName.toLowerCase() === 'img') {
        return element.alt || null;
    }
    
    if (element.title) {
        return String(element.title).trim();
    }
    
    if (element.placeholder) {
        return String(element.placeholder).trim();
    }
    
    return null;
}

function getElementLabel(element) {
    if (element.labels && element.labels.length > 0) {
        return (element.labels[0].innerText || '').trim();
    }
    
    if (element.id) {
        const label = document.querySelector(`label[for="${element.id}"]`);
        if (label) return (label.innerText || '').trim();
    }
    
    let parent = element.parentElement;
    while (parent) {
        if (parent.tagName.toLowerCase() === 'label') {
            return (parent.innerText || '').trim();
        }
        parent = parent.parentElement;
    }
    
    const ariaLabelledBy = element.getAttribute('aria-labelledby');
    if (ariaLabelledBy) {
        const labelEl = document.getElementById(ariaLabelledBy);
        if (labelEl) return (labelEl.innerText || '').trim();
    }
    
    return null;
}

function getVisibleText(element) {
    if (element.offsetWidth === 0 && element.offsetHeight === 0) return null;
    
    const text = element.innerText?.trim();
    if (!text) return null;
    
    if (text.length > 100) return text.substring(0, 97) + '...';
    
    return text;
}

function generateCssSelectors(element) {
    const selectors = [];
    
    if (element.id && String(element.id).trim()) {
        selectors.push({
            selector: `#${CSS.escape(element.id)}`,
            confidence: 0.9
        });
    }
    
    if (element.name && String(element.name).trim()) {
        selectors.push({
            selector: `[name="${CSS.escape(element.name)}"]`,
            confidence: 0.8
        });
    }
    
    if (element.className && String(element.className).trim()) {
        const classes = String(element.className).split(' ').filter(c => c.trim());
        if (classes.length > 0) {
            const classSelector = '.' + classes.map(c => CSS.escape(c)).join('.');
            const matchingElements = document.querySelectorAll(classSelector);
            
            if (matchingElements.length === 1) {
                selectors.push({
                    selector: classSelector,
                    confidence: 0.7
                });
            } else if (matchingElements.length < 5) {
                selectors.push({
                    selector: `${element.tagName.toLowerCase()}${classSelector}`,
                    confidence: 0.6
                });
            }
        }
    }
    
    const uniqueAttributes = ['data-id', 'data-cy', 'data-qa', 'data-automation-id'];
    uniqueAttributes.forEach(attr => {
        const value = element.getAttribute(attr);
        if (value && String(value).trim()) {
            selectors.push({
                selector: `[${attr}="${CSS.escape(value)}"]`,
                confidence: 0.85
            });
        }
    });
    
    if (element.tagName.toLowerCase() === 'input' && element.type && String(element.type).trim()) {
        selectors.push({
            selector: `input[type="${element.type}"]`,
            confidence: 0.3
        });
    }
    
    return selectors;
}

function escapeSelector(str) {
    if (!str || !String(str).trim()) return '';
    return String(str).replace(/'/g, "\\'").replace(/"/g, '\\"');
}

function escapeRegex(str) {
    if (!str || !String(str).trim()) return '';
    return String(str).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function getInputParentWithLabel(input) {
    let parent = input.parentElement;
    while (parent) {
        if (parent.tagName.toLowerCase() === 'div') {
            const textNodes = Array.from(parent.childNodes)
                .filter(node => node.nodeType === Node.TEXT_NODE)
                .map(node => node.textContent.trim())
                .filter(text => text.length > 0);
            
            const directText = textNodes.join(' ').trim();
            
            if (directText.match(/^(Email|Passwort)\*?$/)) {
                return {
                    element: parent,
                    text: directText
                };
            }
        }
        parent = parent.parentElement;
    }
    return null;
}

function generatePlaywrightSelectors(element) {
    const selectors = [];
    
    if (element.tagName.toLowerCase() === 'button' || element.getAttribute('role') === 'button') {
        const customClasses = Array.from(element.classList).filter(cls => 
            !cls.startsWith('p-') && 
            !cls.startsWith('btn-') && 
            cls !== 'button'
        );

        const parentToolbar = element.closest('[role="toolbar"], .p-toolbar');
        if (parentToolbar && customClasses.length > 0) {
            selectors.push({
                type: 'toolbar-custom',
                selector: `getByRole('toolbar').locator('button.${customClasses[0]}')`,
                confidence: 0.95
            });
        }

        const parentNav = element.closest('nav, [role="navigation"]');
        if (parentNav && customClasses.length > 0) {
            selectors.push({
                type: 'nav-custom',
                selector: `getByRole('navigation').locator('button.${customClasses[0]}')`,
                confidence: 0.95
            });
        }

        const parentMenu = element.closest('[role="menu"], .dropdown-menu, .p-menu');
        if (parentMenu && customClasses.length > 0) {
            selectors.push({
                type: 'menu-custom',
                selector: `getByRole('menu').locator('button.${customClasses[0]}')`,
                confidence: 0.95
            });
        }

        const parentDialog = element.closest('[role="dialog"], .p-dialog, .modal');
        if (parentDialog && customClasses.length > 0) {
            selectors.push({
                type: 'dialog-custom',
                selector: `getByRole('dialog').locator('button.${customClasses[0]}')`,
                confidence: 0.95
            });
        }

        const parentForm = element.closest('form');
        if (parentForm && customClasses.length > 0) {
            selectors.push({
                type: 'form-custom',
                selector: `locator('form').locator('button.${customClasses[0]}')`,
                confidence: 0.95
            });
        }

        if (customClasses.length > 0) {
            selectors.push({
                type: 'custom-class',
                selector: `locator('button.${customClasses[0]}')`,
                confidence: 0.9
            });
        }

        const buttonText = element.textContent?.trim();
        if (buttonText) {
            selectors.push({
                type: 'text',
                selector: `getByRole('button', {name: '${escapeSelector(buttonText)}'})`,
                confidence: 0.85
            });
        }

        const tooltipText = element.getAttribute('aria-label') || 
                          element.getAttribute('title') || 
                          element.closest('[data-tooltip]')?.getAttribute('data-tooltip');
        if (tooltipText) {
            selectors.push({
                type: 'tooltip',
                selector: `getByRole('button', {name: '${escapeSelector(tooltipText)}'})`,
                confidence: 0.85
            });
        }

        const dataAttrs = Array.from(element.attributes)
            .filter(attr => attr.name.startsWith('data-'))
            .reduce((acc, attr) => {
                acc[attr.name] = attr.value;
                return acc;
            }, {});
        
        if (Object.keys(dataAttrs).length > 0) {
            const dataSelector = Object.entries(dataAttrs)
                .map(([key, value]) => `[${key}="${value}"]`)
                .join('');
            selectors.push({
                type: 'data-attrs',
                selector: `locator('button${dataSelector}')`,
                confidence: 0.8
            });
        }
    }
    
    if (element.tagName.toLowerCase() === 'input') {
        const parentWithLabel = getInputParentWithLabel(element);
        if (parentWithLabel) {
            selectors.push({
                type: 'parent-text',
                selector: `locator('div').filter({ hasText: /^${escapeRegex(parentWithLabel.text)}$/ }).getByRole('textbox')`,
                confidence: 0.95
            });
        }
    }
    
    const role = element.getAttribute('role') || getImplicitRole(element);
    if (role) {
        const accessibleName = getAccessibleName(element);
        if (accessibleName) {
            const sameElements = Array.from(document.querySelectorAll(`[role="${role}"], ${role}`))
                .filter(el => {
                    const elName = getAccessibleName(el);
                    return elName === accessibleName;
                });
            
            const elementIndex = sameElements.indexOf(element);
            
            let menuContext = '';
            let parent = element.parentElement;
            while (parent) {
                if (parent.getAttribute('role') === 'menu' || parent.classList.contains('dropdown-menu')) {
                    const menuTrigger = document.querySelector(`[aria-controls="${parent.id}"]`) || 
                                      parent.previousElementSibling;
                    if (menuTrigger) {
                        const triggerText = getAccessibleName(menuTrigger);
                        if (triggerText) {
                            menuContext = `${triggerText} menu`;
                            break;
                        }
                    }
                }
                parent = parent.parentElement;
            }
            
            if (sameElements.length > 1) {
                selectors.push({
                    type: 'nth-role',
                    selector: `getByRole('${role}', {name: '${escapeSelector(accessibleName)}'}).nth(${elementIndex})`,
                    confidence: 0.95,
                    testingLibrary: `screen.getAllByRole('${role}', { name: /${escapeRegex(accessibleName)}/i })[${elementIndex}]`,
                    menuContext: menuContext
                });
            }
            
            selectors.push({
                type: 'role',
                    selector: `getByRole('${role}', {name: '${escapeSelector(accessibleName)}'})`,
                confidence: 0.9,
                testingLibrary: `screen.getByRole('${role}', { name: /${escapeRegex(accessibleName)}/i })`
            });
        } else {
            const sameElements = Array.from(document.querySelectorAll(`[role="${role}"], ${role}`));
            const elementIndex = sameElements.indexOf(element);
            
            if (sameElements.length > 1) {
                selectors.push({
                    type: 'nth-role',
                    selector: `getByRole('${role}').nth(${elementIndex})`,
                    confidence: 0.85,
                    testingLibrary: `screen.getAllByRole('${role}')[${elementIndex}]`
                });
            }
            
            selectors.push({
                type: 'role',
                selector: `getByRole('${role}')`,
                confidence: 0.8,
                testingLibrary: `screen.getByRole('${role}')`
            });
        }
    }
    
    if (element.tagName.toLowerCase() === 'img' && 
        (element.classList.contains('pointer') || element.hasAttribute('data-pd-tooltip'))) {
        
        if (element.id) {
            selectors.push({
                type: 'id',
                selector: `locator('#${escapeSelector(element.id)}')`,
                confidence: 0.95,
                testingLibrary: `screen.getByTestId('${element.id}')`
            });
        }
        
        if (element.hasAttribute('data-pd-tooltip')) {
            selectors.push({
                type: 'tooltip',
                selector: `locator('img[data-pd-tooltip="true"]')`,
                confidence: 0.9
            });
        }
        
        if (element.classList.contains('menu-item')) {
            selectors.push({
                type: 'menu-item',
                selector: `locator('.menu-item.pointer')`,
                confidence: 0.85
            });
        }
        
        const menuParent = element.closest('[class*="menu"]');
        if (menuParent) {
            const menuRole = menuParent.getAttribute('role') || 'menu';
            selectors.push({
                type: 'menu-context',
                selector: `getByRole('${menuRole}').locator('img.pointer')`,
                confidence: 0.8
            });
        }
    }

    const testId = element.getAttribute('data-testid') || element.getAttribute('data-test-id') || element.getAttribute('data-test');
    if (testId && String(testId).trim()) {
        selectors.push({
            type: 'testid',
            selector: `getByTestId('${escapeSelector(testId)}')`,
            confidence: 0.95,
            testingLibrary: `screen.getByTestId('${testId}')`
        });
    }
    
    if (['input', 'select', 'textarea'].includes(element.tagName.toLowerCase())) {
        const label = getElementLabel(element);
        if (label && String(label).trim()) {
            selectors.push({
                type: 'label',
                selector: `getByLabel('${escapeSelector(label)}')`,
                confidence: 0.85,
                testingLibrary: `screen.getByLabelText(/${escapeRegex(label)}/i)`
            });
        }
    }
    
    if (element.placeholder && String(element.placeholder).trim()) {
        selectors.push({
            type: 'placeholder',
            selector: `getByPlaceholder('${escapeSelector(String(element.placeholder))}')`,
            confidence: 0.8,
            testingLibrary: `screen.getByPlaceholderText(/${escapeRegex(String(element.placeholder))}/i)`
        });
    }
    
    const visibleText = getVisibleText(element);
    if (visibleText && visibleText.length < 50) {
        selectors.push({
            type: 'text',
            selector: `getByText('${escapeSelector(visibleText)}')`,
            confidence: 0.7,
            testingLibrary: `screen.getByText(/${escapeRegex(visibleText)}/i)`
        });
    }
    
    if (element.title && String(element.title).trim()) {
        selectors.push({
            type: 'title',
            selector: `getByTitle('${escapeSelector(String(element.title))}')`,
            confidence: 0.75,
            testingLibrary: `screen.getByTitle(/${escapeRegex(String(element.title))}/i)`
        });
    }
    
    const cssSelectors = generateCssSelectors(element);
    cssSelectors.forEach(css => {
        selectors.push({
            type: 'css',
            selector: `locator('${css.selector}')`,
            confidence: css.confidence,
            testingLibrary: `screen.getByRole('${role || 'generic'}')`
        });
    });
    
    selectors.sort((a, b) => b.confidence - a.confidence);
    
    return selectors;
}

function extractElementsWithPlaywrightSelectors() {
    // Sayfa boş mu kontrol et
    if (isPageEmpty()) {
        return [];
    }
    
    const elements = Array.from(document.querySelectorAll('*')).filter(el => {
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               el.offsetWidth > 0 && 
               el.offsetHeight > 0;
    });

    return elements.map(element => {
        const selectors = generatePlaywrightSelectors(element);
        const bestSelector = selectors[0]?.selector || null;

        return {
            tag: element.tagName.toLowerCase(),
            role: element.getAttribute('role'),
            accessible_name: getAccessibleName(element),
            best_selector: bestSelector,
            selectors: selectors
        };
    });
}

function getTestingLibrarySelectors(element) {
    const selectors = [];
    
    const role = element.getAttribute('role');
    if (role) {
        selectors.push({
            type: 'role',
            value: role,
            name: element.getAttribute('aria-label') || element.innerText || element.value
        });
    }
    
    const labels = getLabelsForInput(element);
    if (labels.length > 0) {
        selectors.push({
            type: 'label',
            value: labels.map(l => l.innerText.trim()).filter(Boolean).join(' | ')
        });
    }
    
    if (element.placeholder) {
        selectors.push({
            type: 'placeholder',
            value: element.placeholder
        });
    }
    
    if (element.innerText) {
        selectors.push({
            type: 'text',
            value: (element.innerText || '').trim()
        });
    }
    
    if (element.name) {
        selectors.push({
            type: 'name',
            value: element.name
        });
    }
    
    if (element.getAttribute('data-testid')) {
        selectors.push({
            type: 'testid',
            value: element.getAttribute('data-testid')
        });
    }
    
    return selectors;
}

function extractModalsAndPopups() {
    // Sayfa boş mu kontrol et
    if (isPageEmpty()) {
        return [];
    }
    
    const modalSelectors = [
        '.modal', '[role="dialog"]', '[aria-modal="true"]',
        '.p-dialog', '.p-dialog-mask', '.p-component',
        '.dialog', '.popup', '.overlay',
        '[class*="dialog"]', '[class*="modal"]'
    ];
    
    const modals = [];
    
    modalSelectors.forEach(selector => {
        try {
            const elements = Array.from(document.querySelectorAll(selector));
            elements.forEach(modal => {
                if (isElementVisible(modal)) {
                    const title = modal.querySelector('.modal-title, [role="heading"], h1, h2, h3, h4, h5, h6, .p-dialog-title');
                    const actionButtons = Array.from(modal.querySelectorAll('button, [role="button"], .btn, .p-button')).map(button => ({
                        text: button.innerText?.trim() || button.querySelector('.p-button-label')?.textContent?.trim(),
                        type: button.type || 'button',
                        selector: generatePlaywrightSelectors(button)[0]?.selector || null,
                        disabled: button.disabled || button.classList.contains('p-disabled')
                    }));
                    
                    // Include PrimeVue components like dropdowns, calendars, etc.
                    const formElements = Array.from(modal.querySelectorAll('input, select, textarea, .p-dropdown, .p-calendar, [role="combobox"], .p-inputtext')).map(input => {
                        const isPrimeVueDropdown = input.classList.contains('p-dropdown');
                        const isPrimeVueCalendar = input.classList.contains('p-calendar');
                        const isSelect = input.tagName.toLowerCase() === 'select';
                        const isCombobox = input.getAttribute('role') === 'combobox';
                        
                        let selectOptions = undefined;
                        if (isSelect) {
                            selectOptions = Array.from(input.options).map(opt => ({
                                value: opt.value,
                                text: (opt.innerText || '').trim(),
                                selected: opt.selected
                            }));
                        } else if (isPrimeVueDropdown || isCombobox) {
                            // Try to find dropdown options in the DOM
                            const dropdownPanel = document.querySelector('.p-dropdown-panel, .p-overlaypanel');
                            if (dropdownPanel) {
                                const options = Array.from(dropdownPanel.querySelectorAll('.p-dropdown-item, .p-menuitem, [role="option"]'));
                                selectOptions = options.map(opt => ({
                                    value: opt.getAttribute('data-value') || opt.textContent?.trim(),
                                    text: opt.textContent?.trim(),
                                    selected: opt.classList.contains('p-highlight') || opt.getAttribute('aria-selected') === 'true'
                                }));
                            }
                        }

                        return {
                            type: isPrimeVueDropdown ? 'dropdown' : 
                                  isPrimeVueCalendar ? 'calendar' :
                                  input.type || input.tagName.toLowerCase(),
                            label: getElementLabel(input),
                            placeholder: input.placeholder,
                            options: selectOptions,
                            selector: generatePlaywrightSelectors(input)[0]?.selector || null,
                            isPrimeVue: isPrimeVueDropdown || isPrimeVueCalendar,
                            component: isPrimeVueDropdown ? 'p-dropdown' : 
                                       isPrimeVueCalendar ? 'p-calendar' : null
                        };
                    });

                    modals.push({
                        title: title ? title.innerText?.trim() : null,
                        actionButtons,
                        inputs: formElements,
                        selector: generatePlaywrightSelectors(modal)[0]?.selector || null,
                        modalType: detectOverlayType(modal),
                        visible: isElementVisible(modal)
                    });
                }
            });
        } catch (e) {
            // Ignore selector errors
        }
    });

    return modals;
}

function extractTables() {
    if (isPageEmpty()) {
        return [];
    }
    
    const elements = [];
    const tables = Array.from(document.querySelectorAll('table'));
    
    tables.forEach((table, tableIndex) => {

        const headers = Array.from(table.querySelectorAll('th')).map(th => (th.innerText || '').trim());
        if (headers.length > 0) {
            elements.push(`headers: ${headers.join(', ')}`);
        }

        const filterRow = Array.from(table.querySelectorAll('thead tr')).find((tr, idx) => idx > 0);
        if (filterRow) {
            Array.from(filterRow.children).forEach((cell, colIndex) => {
                const headerText = headers[colIndex] || `Column ${colIndex + 1}`;
                
                cell.querySelectorAll('input[type="text"], input:not([type])').forEach(input => {
                    const dataField = input.getAttribute('data-field') || cell.getAttribute('data-field');
                    elements.push({
                        role: 'textbox',
                        name: `${headerText} (filter)`,
                        action: 'fill',
                        selector: dataField 
                            ? `locator('thead tr').nth(0).locator('[data-field="${dataField}"]')`
                            : `locator('thead tr').nth(0).locator('th, td').nth(${colIndex}).getByRole('textbox')`
                    });
                });

                cell.querySelectorAll('select, [role="combobox"]').forEach(select => {
                    const dataField = select.getAttribute('data-field') || cell.getAttribute('data-field');
                    elements.push({
                        role: 'combobox',
                        name: `${headerText} (filter)`,
                        action: 'select',
                        selector: dataField 
                            ? `locator('thead tr').nth(0).locator('[data-field="${dataField}"]')`
                            : `locator('thead tr').nth(0).locator('th, td').nth(${colIndex}).getByRole('combobox')`
                    });
                });
            });
        }

        const rows = Array.from(table.querySelectorAll('tbody tr'));
        rows.forEach((row, rowIndex) => {
            const checkbox = row.querySelector('input[type="checkbox"], [role="checkbox"]');
            if (checkbox) {
                elements.push({
                    role: 'checkbox',
                    name: `row ${rowIndex + 1}: checkbox`,
                    action: 'check',
                    selector: `locator('tbody tr').nth(${rowIndex}).getByRole('checkbox')`
                });
            }

            Array.from(row.children).forEach((cell, colIndex) => {
                const headerText = headers[colIndex] || `Column ${colIndex + 1}`;
                const dataField = cell.getAttribute('data-field');
                
                if (dataField) {
                    elements.push({
                        role: 'cell',
                        name: `row ${rowIndex + 1}: ${dataField}`,
                        action: 'click',
                        selector: `locator('tbody tr').nth(${rowIndex}).locator('[data-field="${dataField}"]')`
                    });
                }

                cell.querySelectorAll('.action-buttons img[data-pd-tooltip], .action-buttons img[aria-haspopup]').forEach(img => {
                    const alt = img.getAttribute('alt') || 'More';
                    const hasTooltip = img.hasAttribute('data-pd-tooltip');
                    const hasPopup = img.getAttribute('aria-haspopup') === 'true';
                    const menuId = img.getAttribute('aria-controls');
                    
                    elements.push({
                        role: 'img',
                        name: `row ${rowIndex + 1}: ${alt} menu`,
                        action: 'click',
                        selector: `locator('tbody tr').nth(${rowIndex}).locator('.action-buttons img[data-pd-tooltip]')`,
                        tooltip: hasTooltip,
                        popup: hasPopup,
                        menuId: menuId,
                        isClickable: true
                    });
                });

                cell.querySelectorAll('button, a, input, select, [role="button"], [role="link"]').forEach(el => {
                    const role = el.getAttribute('role') || getImplicitRole(el);
                    const name = getAccessibleName(el) || el.innerText?.trim() || el.value;
                    if (name) {
                        elements.push({
                            role: role || el.tagName.toLowerCase(),
                            name: `row ${rowIndex + 1}: ${name}`,
                            action: role === 'combobox' ? 'select' : role === 'checkbox' ? 'check' : 'click',
                            selector: `locator('tbody tr').nth(${rowIndex}).getByRole('${role}', { name: '${name}' })`
                        });
                    }
                });
            });
        });
    });

    return elements.map(el => {
        if (typeof el === 'string') return el;
        return `${el.role} | ${el.name} | ${el.action} | ${el.selector}`;
    }).join('\n');
}

function extractAllVisibleElements() {
    // Sayfa boş mu kontrol et
    if (isPageEmpty()) {
        return {
            inputs: [],
            buttons: [],
            links: [],
            images: [],
            videos: [],
            iframes: [],
            unknown: []
        };
    }
    
    const allElements = Array.from(document.querySelectorAll('*')).filter(el => {
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               el.offsetWidth > 0 && 
               el.offsetHeight > 0;
    });
    
    const categorizedElements = {
        inputs: [],
        buttons: [],
        links: [],
        images: [],
        videos: [],
        iframes: [],
        unknown: []
    };
    
    allElements.forEach(el => {
        const tagName = el.tagName.toLowerCase();
        const hasClick = el.onclick || el.getAttribute('onclick');
        const hasRole = el.getAttribute('role');
        const isInteractive = ['button', 'a', 'input', 'select', 'textarea'].includes(tagName) || 
                             hasClick || 
                             hasRole === 'button' || 
                             el.tabIndex >= 0;
        
        if (!isInteractive) return;
        
        const elementData = {
            tag: tagName,
            text: el.innerText?.trim() || '',
            id: el.id || null,
            classes: el.className || null,
            role: hasRole,
            selectors: getTestingLibrarySelectors(el),
            position: {
                x: el.offsetLeft,
                y: el.offsetTop,
                width: el.offsetWidth,
                height: el.offsetHeight
            },
            'data-pd-tooltip': el.getAttribute('data-pd-tooltip'),
            'data-tooltip-text': el.getAttribute('data-tooltip-text') || el.getAttribute('title'),
            src: el.getAttribute('src'),
            alt: el.getAttribute('alt'),
            menuParent: el.closest('[class*="menu"]')?.className || null,
            menuRole: el.closest('[role="menu"]')?.getAttribute('role') || null,
            isClickable: el.onclick || el.classList.contains('pointer') || el.getAttribute('role') === 'button',
            isInteractive: el.tabIndex >= 0 || el.getAttribute('aria-haspopup') === 'true'
        };
        
        if (tagName === 'input' || tagName === 'select' || tagName === 'textarea') {
            categorizedElements.inputs.push({...elementData, type: el.type});
        } else if (tagName === 'button' || hasRole === 'button' || tagName === 'input' && el.type === 'submit') {
            categorizedElements.buttons.push(elementData);
        } else if (tagName === 'a') {
            categorizedElements.links.push({...elementData, href: el.href});
        } else if (tagName === 'img') {
            categorizedElements.images.push({...elementData, src: el.src, alt: el.alt});
        } else if (tagName === 'video') {
            categorizedElements.videos.push({...elementData, src: el.src});
        } else if (tagName === 'iframe') {
            categorizedElements.iframes.push({...elementData, src: el.src});
        } else {
            categorizedElements.unknown.push(elementData);
        }
    });
    
    return categorizedElements;
}

function extractMetaDescription() {
    const metaDesc = document.querySelector('meta[name="description"]');
    return metaDesc ? metaDesc.getAttribute('content') : null;
}

function extractFormElements() {
    // Sayfa boş mu kontrol et
    if (isPageEmpty()) {
        return [];
    }
    
    return Array.from(document.querySelectorAll('form')).map(form => {
        const inputs = Array.from(form.querySelectorAll('input, select, textarea, .p-dropdown, .p-calendar, [role="combobox"]')).map(input => {
            const labels = getLabelsForInput(input);
            const isPrimeVue = input.className?.includes('p-') || false;
            const isRequired = input.required || input.getAttribute('aria-required') === 'true' || 
                             labels[0]?.textContent?.includes('*') || false;
            
            if (input.classList.contains('p-dropdown')) {
                return {
                    type: 'dropdown',
                    name: input.id,
                    id: input.id,
                    required: isRequired,
                    label: labels.length > 0 ? labels[0].innerText.replace('*', '').trim() : null,
                    isPrimeVue: true,
                    selector: `locator('#${input.id}').getByRole('combobox')`,
                    component: 'p-dropdown'
                };
            }
            
            if (input.classList.contains('p-calendar')) {
                return {
                    type: 'calendar',
                    name: input.id,
                    id: input.id,
                    required: isRequired,
                    label: labels.length > 0 ? labels[0].innerText.replace('*', '').trim() : null,
                    isPrimeVue: true,
                    selector: `locator('#${input.id}').getByRole('combobox')`,
                    component: 'p-calendar'
                };
            }
            
            return {
                type: input.type || input.tagName.toLowerCase(),
                name: input.name,
                id: input.id,
                placeholder: input.placeholder,
                required: isRequired,
                label: labels.length > 0 ? labels[0].innerText.replace('*', '').trim() : null,
                isPrimeVue: isPrimeVue,
                selector: generatePlaywrightSelectors(input)[0]?.selector || null,
                component: isPrimeVue ? `p-${input.type || input.tagName.toLowerCase()}` : null
            };
        });

        const buttons = Array.from(form.querySelectorAll('button, input[type="submit"], input[type="button"], .p-button')).map(button => {
            const isPrimeVue = button.className?.includes('p-button') || false;
            const isDisabled = button.disabled || button.classList.contains('p-disabled');
            const buttonText = button.querySelector('.p-button-label')?.textContent || 
                             button.innerText || 
                             button.value;

            const isExpanded = 
            button.getAttribute('aria-expanded') === 'true' || 
            button.classList.contains('nav-button--expanded') ||
            button.classList.contains('expanded') ||
            button.classList.contains('--expanded') ||
            button.classList.contains('w--open');
            
            const isNavButton = button.classList.contains('nav-button');
            if (isNavButton) {
                const arrow = button.querySelector('.nav-arrow');
                if (arrow && arrow.getAttribute('alt') === 'Collapse') {
                    isExpanded = true;
                }
            }                 
            
            return {
                type: button.type || 'button',
                text: buttonText?.trim(),
                selector: generatePlaywrightSelectors(button)[0]?.selector || null,
                isPrimeVue: isPrimeVue,
                disabled: isDisabled,
                expanded: isExpanded,
                isNavButton: isNavButton,
                component: isPrimeVue ? 'p-button' : null,
                variant: button.classList.contains('p-info') ? 'info' : 
                        button.classList.contains('p-success') ? 'success' : 
                        button.classList.contains('p-warning') ? 'warning' : 
                        button.classList.contains('p-danger') ? 'danger' : 'default'
            };
        });

        return {
            id: form.id,
            action: form.action,
            method: form.method,
            inputs,
            buttons
        };
    });
}

function isVisible(element) {
    if (!element) return false;
    
    const style = window.getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    
    return style.display !== 'none' &&
           style.visibility !== 'hidden' &&
           style.opacity !== '0' &&
           rect.width > 0 &&
           rect.height > 0;
}

function findControlledPanel(el) {
    const controlsId = el.getAttribute('aria-controls');
    if (controlsId && String(controlsId).trim()) {
        return document.getElementById(controlsId);
    }

    const bsTarget = el.getAttribute('data-bs-target');
    if (bsTarget && String(bsTarget).trim()) {
        return document.querySelector(bsTarget);
    }

    const href = el.getAttribute('href');
    if (href && href.startsWith('#') && href.length > 1) {
        return document.querySelector(href);
    }

    return null;
}

function ariaExpandedRaw(el) {
    const expanded = el.getAttribute('aria-expanded');
    if (expanded === null) return null;
    return expanded === 'true';
}

function computeExpanded(el) {
    if (el.classList.contains('nav-button--expanded')) return true;
  
    const det = el.closest('details');
    if (det && el.tagName.toLowerCase() === 'summary') return !!det.open;
  
    const raw = ariaExpandedRaw(el);
    if (raw !== null) return raw;
  
    const panel = findControlledPanel(el);
    if (panel) return isVisible(panel);
    return null;
}

function getVisibleSubitems(container) {
    if (!container) return [];
    return Array.from(container.querySelectorAll(':scope > li > *, :scope > li'))
      .filter(isVisible)
      .map(n => (n.innerText || n.textContent || '').trim())
      .filter(Boolean);
  }

function isPageEmpty() {
    const body = document.body;
    if (!body) return true;
    
    const textContent = body.innerText?.trim() || '';
    const hasVisibleElements = body.children.length > 0;
    
    return !textContent && !hasVisibleElements;
}

function extractInteractiveElements() {
    if (isPageEmpty()) {
        return [];
    }
    
    const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"], .btn, [role="button"]'))
        .map(button => {
            const selectors = generatePlaywrightSelectors(button);
            
            const img = button.querySelector('img');
            const icon = button.querySelector('i, .icon, [class*="icon"]');
            const tooltipWrapper = button.closest('.tooltip-wrapper');
            const tooltipText = tooltipWrapper?.getAttribute('data-tooltip') || 
                              tooltipWrapper?.getAttribute('data-pd-tooltip') ||
                              button.getAttribute('aria-label') ||
                              button.title;

            const classes = Array.from(button.classList);
            const frameworkInfo = {
                primevue: classes.filter(c => c.startsWith('p-')),
                bootstrap: classes.filter(c => c.startsWith('btn-') || c.startsWith('nav-')),
                material: classes.filter(c => c.startsWith('mat-')),
                tailwind: classes.filter(c => c.match(/^(bg-|text-|border-|rounded-)/)),
                custom: classes.filter(c => 
                    !c.startsWith('p-') && 
                    !c.startsWith('btn-') && 
                    !c.startsWith('nav-') && 
                    !c.startsWith('mat-') &&
                    !c.match(/^(bg-|text-|border-|rounded-)/)
                )
            };

            const parentToolbar = button.closest('[role="toolbar"], .p-toolbar');
            const parentMenu = button.closest('[role="menu"], .dropdown-menu');
            const parentNav = button.closest('nav, [role="navigation"]');
            const parentForm = button.closest('form');
            const parentDialog = button.closest('[role="dialog"], .modal');

            const dataAttrs = {};
            const ariaAttrs = {};
            Array.from(button.attributes).forEach(attr => {
                if (attr.name.startsWith('data-')) {
                    dataAttrs[attr.name] = attr.value;
                } else if (attr.name.startsWith('aria-')) {
                    ariaAttrs[attr.name] = attr.value;
                }
            });

            const buttonText = (button.textContent || button.value || '').toLowerCase();
            const buttonClasses = String(button.className || '').toLowerCase();
            
            const actionTypes = {
                submit: ['submit', 'save', 'confirm', 'apply'],
                cancel: ['cancel', 'reset', 'clear', 'close'],
                export: ['export', 'download', 'excel', 'csv'],
                import: ['import', 'upload'],
                add: ['add', 'create', 'new'],
                edit: ['edit', 'modify', 'update'],
                delete: ['delete', 'remove', 'trash'],
                search: ['search', 'find', 'filter'],
                refresh: ['refresh', 'reload', 'sync'],
                settings: ['settings', 'configure', 'preferences'],
                menu: ['menu', 'more', 'options'],
                navigation: ['next', 'previous', 'back', 'forward']
            };

            const buttonActions = {};
            Object.entries(actionTypes).forEach(([action, keywords]) => {
                buttonActions[action] = keywords.some(keyword => 
                    buttonText.includes(keyword) || 
                    buttonClasses.includes(keyword) ||
                    classes.some(c => c.includes(keyword))
                );
            });

            const isPrimary = classes.some(c => c.includes('primary') || c.includes('main'));
            const isSecondary = classes.some(c => c.includes('secondary'));
            const isDanger = classes.some(c => c.includes('danger') || c.includes('delete') || c.includes('remove'));
            const isWarning = classes.some(c => c.includes('warning'));

            return {
                type: 'button',
                tag: button.tagName.toLowerCase(),
                text: button.innerText || button.value || null,
                role: button.getAttribute('role') || null,
                disabled: button.disabled || false,
                expanded: computeExpanded(button),
                id: button.id || null,
                className: button.className || null,
                
                hasIcon: !!icon || !!img,
                iconType: img ? 'image' : icon ? 'font-icon' : null,
                iconSrc: img?.src || null,
                tooltip: tooltipText,
                
                frameworks: frameworkInfo,
                isPrimeVue: frameworkInfo.primevue.length > 0,
                isBootstrap: frameworkInfo.bootstrap.length > 0,
                
                inToolbar: !!parentToolbar,
                inMenu: !!parentMenu,
                inNavigation: !!parentNav,
                inForm: !!parentForm,
                inDialog: !!parentDialog,
                
                dataAttributes: dataAttrs,
                ariaAttributes: ariaAttrs,
                
                actions: buttonActions,
                importance: {
                    primary: isPrimary,
                    secondary: isSecondary,
                    danger: isDanger,
                    warning: isWarning
                },
                
                selectors: selectors
            };
        });

    const links = Array.from(document.querySelectorAll('a'))
        .map(link => {
            const selectors = generatePlaywrightSelectors(link);
            return {
                type: 'link',
                tag: link.tagName.toLowerCase(),
                text: link.innerText || null,
                href: link.href || null,
                role: link.getAttribute('role') || null,
                id: link.id || null,
                className: link.className || null,
                selectors: selectors
            };
        });

    const clickables = Array.from(document.querySelectorAll('[onclick], [role="button"], [tabindex="0"]'))
        .filter(el => !el.matches('button, a, input[type="button"], input[type="submit"]'))
        .map(el => {
            const selectors = generatePlaywrightSelectors(el);
            return {
                type: 'clickable',
                tag: el.tagName.toLowerCase(),
                text: el.innerText || null,
                role: el.getAttribute('role') || null,
                id: el.id || null,
                className: el.className || null,
                selectors: selectors
            };
        });

    const selects = Array.from(document.querySelectorAll('select')).map(select => {
        const selectors = generatePlaywrightSelectors(select);
        const options = Array.from(select.options).map(opt => ({
            value: opt.value,
            text: opt.innerText.trim(),
            selected: opt.selected
        }));
        return {
            type: 'select',
            tag: select.tagName.toLowerCase(),
            name: select.name || null,
            label: getElementLabel(select),
            id: select.id || null,
            className: select.className || null,
            options: options,
            selectors: selectors
        };
    });

    const inputs = Array.from(document.querySelectorAll('input:not([type="button"]):not([type="submit"]):not([type="hidden"]), textarea'))
        .map(input => {
            const selectors = generatePlaywrightSelectors(input);
            const parentWithLabel = getInputParentWithLabel(input);
            
            let bestSelector;
            if (parentWithLabel) {
                bestSelector = `locator('div').filter({ hasText: /^${escapeRegex(parentWithLabel.text)}$/ }).getByRole('textbox')`;
            } else {
                if (input.type === 'password') {
                    bestSelector = `locator('input[type="password"]')`;
                } else {
                    bestSelector = selectors[0]?.selector;
                }
            }

            const label = parentWithLabel ? parentWithLabel.text : '';
            return {
                type: 'INPUT',
                text: input.value || '',
                id: input.id || '',
                placeholder: input.placeholder || '',
                inputType: input.type || 'text',
                label: label,
                selectors: [bestSelector]
            };
        });

    const toolbars = Array.from(document.querySelectorAll('.p-toolbar, [role="toolbar"]'))
        .map(toolbar => {
            const sections = {
                start: toolbar.querySelector('.p-toolbar-group-start, .p-toolbar-group-left'),
                center: toolbar.querySelector('.p-toolbar-group-center'),
                end: toolbar.querySelector('.p-toolbar-group-end, .p-toolbar-group-right')
            };

                        const extractToolbarButtons = (section) => {
                            if (!section) return [];
                            return Array.from(section.querySelectorAll('button, .p-button')).map(button => {
                                const img = button.querySelector('img');
                                const tooltipWrapper = button.closest('.tooltip-wrapper');
                                const tooltipText = tooltipWrapper?.getAttribute('data-tooltip') || 
                                                  tooltipWrapper?.getAttribute('data-pd-tooltip') ||
                                                  button.getAttribute('aria-label') ||
                                                  button.title;

                                const customClasses = Array.from(button.classList).filter(cls => 
                                    !cls.startsWith('p-') && 
                                    !cls.startsWith('btn-') && 
                                    cls !== 'button'
                                );
                                
                                const selectors = [];
                                
                                if (customClasses.length > 0) {
                                    selectors.push({
                                        type: 'toolbar-custom',
                                        selector: `getByRole('toolbar').locator('button.${customClasses[0]}')`,
                                        confidence: 0.95
                                    });
                                }

                                // Toolbar içindeki buton için alternatif seçici
                                selectors.push({
                                    type: 'toolbar-button',
                                    selector: `locator('.p-toolbar button.${customClasses[0] || 'p-button'}')`,
                                    confidence: 0.9
                                });

                                if (tooltipText) {
                                    selectors.push({
                                        type: 'tooltip',
                                        selector: `getByRole('button', {name:'${escapeSelector(tooltipText)}'})`,
                                        confidence: 0.85
                                    });
                                }

                                return {
                                    type: 'button',
                                    tag: 'button',
                                    component: 'p-button',
                                    isPrimeVue: true,
                                    variant: button.classList.contains('p-secondary') ? 'secondary' : 'primary',
                                    text: button.textContent?.trim() || '',
                                    tooltip: tooltipText,
                                    hasIcon: !!img,
                                    iconSrc: img?.src || null,
                                    className: button.className,
                                    customClass: customClasses[0] || null,
                                    selectors: selectors,
                                    section: section.classList.contains('p-toolbar-group-start') ? 'start' :
                                            section.classList.contains('p-toolbar-group-center') ? 'center' : 'end',
                                    inToolbar: true
                                };
                });
            };

            return {
                type: 'toolbar',
                component: 'p-toolbar',
                role: 'toolbar',
                buttons: [
                    ...extractToolbarButtons(sections.start),
                    ...extractToolbarButtons(sections.center),
                    ...extractToolbarButtons(sections.end)
                ]
            };
        });    

    return [...buttons, ...links, ...clickables, ...selects, ...inputs, ...toolbars];
}

function extractPageStructure() {
    const headings = Array.from(document.querySelectorAll('h1, h2, h3')).map(heading => ({
        level: parseInt(heading.tagName.substring(1)),
        text: heading.innerText.trim(),
        id: heading.id || null,
        selector: generatePlaywrightSelectors(heading)[0]?.selector || null
    }));

    const sections = Array.from(document.querySelectorAll('section, article, main, div[role="main"]'))
        .filter(section => {
            return section.id || 
                   section.className || 
                   section.querySelector('h1, h2, h3') ||
                   section.offsetHeight > 200;
        })
        .map(section => {
            const sectionHeading = section.querySelector('h1, h2, h3, h4');
            return {
                id: section.id || null,
                classes: section.className || null,
                heading: sectionHeading ? sectionHeading.innerText.trim() : null,
                selector: generatePlaywrightSelectors(section)[0]?.selector || null
            };
        });

    return {
        headings,
        sections
    };
}

function extractNavigation() {
    const navigationElements = Array.from(document.querySelectorAll('nav, [role="navigation"]')).map(nav => {
        const links = Array.from(nav.querySelectorAll('a')).map(link => ({
            text: link.innerText.trim(),
            href: link.href,
            selector: generatePlaywrightSelectors(link)[0]?.selector || null
        }));

        const buttons = Array.from(nav.querySelectorAll('button, [role="button"]')).map(button => ({
            text: button.innerText.trim(),
            selector: generatePlaywrightSelectors(button)[0]?.selector || null
        }));

        return {
            id: nav.id,
            role: nav.getAttribute('role'),
            links,
            buttons,
            selector: generatePlaywrightSelectors(nav)[0]?.selector || null
        };
    });

    return {
        navigation_elements: navigationElements
    };
}