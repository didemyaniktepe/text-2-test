const { test, expect } = require('@playwright/test');

test('Add three todos and press enter after each one of them, mark one as completed, then switch to All filter and verify all todos are still visible.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL(/.+/);
  
  const inputField = page.getByRole('textbox', { name: 'What needs to be done?' });

  await expect(inputField).toBeVisible();
  await inputField.fill('Todo 1');
  await inputField.press('Enter');

  await expect(inputField).toBeVisible();
  await inputField.fill('Todo 2');
  await inputField.press('Enter');

  await expect(inputField).toBeVisible();
  await inputField.fill('Todo 3');
  await inputField.press('Enter');

  const todoCheckbox = page.getByRole('checkbox', { name: 'Toggle Todo' }).nth(0);
  await expect(todoCheckbox).toBeVisible();
  await todoCheckbox.check();

  const allFilter = page.getByRole('link', { name: 'All' });
  await expect(allFilter).toBeVisible();
  await allFilter.click();

  const todos = page.locator('.todo-list li');
  await expect(todos).toHaveCount(3);
});