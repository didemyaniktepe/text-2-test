const { test, expect } = require('@playwright/test');

test('Fill and press enter after a todo with leading and trailing spaces \'   Trim me   \' verify the saved item text is trimmed to \'Trim me\'.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page.getByRole('textbox', { name: 'What needs to be done?' })).toBeVisible();
  await page.getByRole('textbox', { name: 'What needs to be done?' }).fill('   Trim me   ');
  await page.getByRole('textbox', { name: 'What needs to be done?' }).press('Enter');
  await expect(page.getByText('Trim me')).toBeVisible();
});