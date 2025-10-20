const { test, expect } = require('@playwright/test');

test('Add three todos after each one of them, mark two as completed, then switch to Completed filter and verify only completed todos are displayed.', async ({ page }) => {
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

  const secondCheckbox = page.getByRole('checkbox', { name: 'Toggle Todo' }).nth(1);
  await secondCheckbox.check();

  const completedFilter = page.getByRole('link', { name: 'Completed' });
  await completedFilter.click();

  await expect(page).toHaveURL(/completed/);

  const completedTodos = page.locator('.todo-list li');
  await expect(completedTodos).toHaveCount(2);
  await expect(completedTodos.nth(0)).toContainText('Todo 1');
  await expect(completedTodos.nth(1)).toContainText('Todo 2');
});