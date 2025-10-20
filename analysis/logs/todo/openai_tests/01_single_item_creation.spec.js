const { test, expect } = require('@playwright/test');

test('Add single item as To Do and press Enter', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL(/.+/);
  
  const todoInput = page.getByRole('textbox', { name: 'What needs to be done?' });
  await expect(todoInput).toBeVisible();
  await expect(todoInput).toBeEnabled();
  
  await todoInput.fill('Buy groceries');
  await todoInput.press('Enter');
  
  const todoItem = page.getByRole('listitem', { name: 'Buy groceries' });
  await expect(todoItem).toBeVisible();
});