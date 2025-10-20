const { test, expect } = require('@playwright/test');

test('Fill and press enter after a todo with leading and trailing spaces "   Trim me   " verify the saved item text is trimmed to "Trim me".', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL(/.+/);
  const inputField = page.getByRole('textbox', { name: 'What needs to be done?' });
  await expect(inputField).toBeVisible();
  await expect(inputField).toBeEnabled();
  await inputField.fill('   Trim me   ');
  await inputField.press('Enter');
  const todoItem = page.locator('.todo-list li').first();
  await expect(todoItem).toBeVisible();
  await expect(todoItem).toHaveText('Trim me');
});