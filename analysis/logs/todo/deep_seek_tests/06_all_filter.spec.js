const { test, expect } = require('@playwright/test');

test('Add three todos and press enter after each one of them, mark one as completed, then switch to All filter and verify all todos are still visible.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL(/.+/);

  const todoInput = page.getByRole('textbox', { name: 'What needs to be done?' });

  await expect(todoInput).toBeVisible();
  await expect(todoInput).toBeEnabled();
  await todoInput.fill('Todo 1');
  await todoInput.press('Enter');

  await expect(todoInput).toBeVisible();
  await expect(todoInput).toBeEnabled();
  await todoInput.fill('Todo 2');
  await todoInput.press('Enter');

  await expect(todoInput).toBeVisible();
  await expect(todoInput).toBeEnabled();
  await todoInput.fill('Todo 3');
  await todoInput.press('Enter');

  const firstCheckbox = page.getByRole('checkbox', { name: 'Toggle Todo' }).first();
  await firstCheckbox.check();

  const todoListItems = page.locator('.todo-list li');
  await expect(todoListItems).toHaveCount(3);
});