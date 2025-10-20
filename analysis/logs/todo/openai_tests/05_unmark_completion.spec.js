const { test, expect } = require('@playwright/test');

test('Add two todos "Buy eggs" and "Clean room" and press enter after each one of them, mark the first as completed, then unmark it and verify style reverts.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL(/.+/);

  const todoInput = page.getByRole('textbox', { name: 'What needs to be done?' });
  await expect(todoInput).toBeVisible();
  await expect(todoInput).toBeEnabled();
  await todoInput.fill('Buy eggs');
  await todoInput.press('Enter');

  await expect(page.getByText('Buy eggs')).toBeVisible();

  await expect(todoInput).toBeVisible();
  await expect(todoInput).toBeEnabled();
  await todoInput.fill('Clean room');
  await todoInput.press('Enter');

  await expect(page.getByText('Clean room')).toBeVisible();

  const buyEggsCheckbox = page.getByRole('checkbox', { name: 'Toggle Todo' }).first();
  await expect(buyEggsCheckbox).toBeVisible();
  await buyEggsCheckbox.check();
  await expect(buyEggsCheckbox).toBeChecked();

  await buyEggsCheckbox.uncheck();
  await expect(buyEggsCheckbox).not.toBeChecked();
  await expect(page.getByText('Buy eggs')).toBeVisible();
});