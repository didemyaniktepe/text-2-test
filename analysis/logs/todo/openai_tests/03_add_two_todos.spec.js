const { test, expect } = require('@playwright/test');

test('Add two todos "Buy eggs" and "Clean room" and press enter after each one of them, mark the second as completed, and verify its style changes.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL(/.+/);

  const inputField = page.getByRole('textbox', { name: 'What needs to be done?' });
  await expect(inputField).toBeVisible();
  await expect(inputField).toBeEnabled();

  await inputField.fill('Buy eggs');
  await inputField.press('Enter');

  await inputField.fill('Clean room');
  await inputField.press('Enter');

  const todoCheckbox = page.locator('input[type="checkbox"]').nth(1);
  await expect(todoCheckbox).toBeVisible();
  await expect(todoCheckbox).toBeEnabled();
  await todoCheckbox.check();

  const completedTodo = page.getByText('Clean room').locator('..').locator('label');
  await expect(completedTodo).toHaveCSS('text-decoration-line', 'line-through');
});