const { test, expect } = require('@playwright/test');

test('Attempt to submit an empty todo by pressing Enter on an empty input; verify no new item is created and the list remains unchanged.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL(/.+/);

  const inputField = page.getByRole('textbox', { name: 'What needs to be done?' });
  await expect(inputField).toBeVisible();
  await expect(inputField).toBeEnabled();
  await inputField.press('Enter');

  const todoList = page.locator('.todo-list');
  await expect(todoList).not.toBeVisible();
});