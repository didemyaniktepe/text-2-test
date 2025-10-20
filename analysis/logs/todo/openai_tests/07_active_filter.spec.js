const { test, expect } = require('@playwright/test');

test('Add three todos and press enter after each one of them, mark one as completed, then switch to “Active” filter and confirm only active todos are shown.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  
  const todoInput = page.getByRole('textbox', { name: 'What needs to be done?' });
  
  await expect(todoInput).toBeVisible();
  await todoInput.fill('Todo 1');
  await todoInput.press('Enter');
  
  await expect(todoInput).toBeVisible();
  await todoInput.fill('Todo 2');
  await todoInput.press('Enter');

  await expect(todoInput).toBeVisible();
  await todoInput.fill('Todo 3');
  await todoInput.press('Enter');
  
  const firstCheckbox = page.getByRole('checkbox', { name: 'Toggle Todo' }).nth(0);
  await expect(firstCheckbox).toBeVisible();
  await firstCheckbox.check();
  
  const activeFilter = page.getByRole('link', { name: 'Active' });
  await expect(activeFilter).toBeVisible();
  await activeFilter.click();
  
  await expect(page).toHaveURL(/#\/active/);
  const activeTodos = page.locator('.todo-list li');
  await expect(activeTodos).toHaveCount(2);
  await expect(activeTodos.nth(0)).toHaveText('Todo 2');
  await expect(activeTodos.nth(1)).toHaveText('Todo 3');
});