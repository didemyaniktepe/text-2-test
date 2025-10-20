const { test, expect } = require('@playwright/test');

test('Add single item as To Do', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL(/.+/);

  const todoInput = page.getByRole('textbox', { name: 'What needs to be done?' });
  await expect(todoInput).toBeVisible();
  await todoInput.fill('Buy groceries');
  await todoInput.press('Enter');

  const addedTodo = page.getByText('Buy groceries');
  await expect(addedTodo).toBeVisible();
});