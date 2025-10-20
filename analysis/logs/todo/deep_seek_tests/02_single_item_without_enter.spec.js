const { test, expect } = require('@playwright/test');

test('Add single item as To Do', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL(/.+/);

  const inputField = page.getByRole('textbox', { name: 'What needs to be done?' });
  await expect(inputField).toBeVisible();
  await expect(inputField).toBeEnabled();
  await inputField.fill('Buy groceries');
  await inputField.press('Enter');

  const todoItem = page.getByText('Buy groceries');
  await expect(todoItem).toBeVisible();
});