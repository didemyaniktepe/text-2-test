const { test, expect } = require('@playwright/test');

test('Add two todos "Buy eggs" and "Clean room" and press enter after each one of them, mark the first as completed, then unmark it and verify style reverts.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL(/.+/);

  const todoInput = page.getByRole('textbox', { name: 'What needs to be done?' });

  await expect(todoInput).toBeVisible();
  await todoInput.fill('Buy eggs');
  await todoInput.press('Enter');

  await expect(page.getByText('Buy eggs')).toBeVisible();

  await expect(todoInput).toBeVisible();
  await todoInput.fill('Clean room');
  await todoInput.press('Enter');

  await expect(page.getByText('Clean room')).toBeVisible();

  const firstTodoCheckbox = page.getByRole('checkbox', { name: 'Toggle Todo' }).first();

  await expect(firstTodoCheckbox).toBeVisible();
  await firstTodoCheckbox.check();

  await expect(page.getByText('Buy eggs').first()).toHaveClass(/completed/);

  await firstTodoCheckbox.uncheck();

  await expect(page.getByText('Buy eggs').first()).not.toHaveClass(/completed/);
});