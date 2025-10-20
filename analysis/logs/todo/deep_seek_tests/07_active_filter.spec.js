const { test, expect } = require('@playwright/test');

test('Add three todos and press enter after each one of them, mark one as completed, then switch to “Active” filter and confirm only active todos are shown.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL('https://demo.playwright.dev/todomvc/#/');

  // Step 1
  const todoInput = page.getByRole('textbox', { name: 'What needs to be done?' });
  await expect(todoInput).toBeVisible();
  await todoInput.fill('Todo 1');

  // Step 2
  await todoInput.press('Enter');

  // Step 3
  await expect(todoInput).toBeVisible();
  await todoInput.fill('Todo 2');

  // Step 4
  await todoInput.press('Enter');

  // Step 5
  await expect(todoInput).toBeVisible();
  await todoInput.fill('Todo 3');

  // Step 6
  await todoInput.press('Enter');

  // Step 7
  const firstTodoCheckbox = page.getByRole('checkbox', { name: 'Toggle Todo' }).nth(0);
  await expect(firstTodoCheckbox).toBeVisible();
  await firstTodoCheckbox.check();

  // Step 8
  const activeFilter = page.getByRole('link', { name: 'Active' });
  await expect(activeFilter).toBeVisible();
  await activeFilter.click();

  // Assertion to verify only active todos are shown
  const activeTodos = await page.locator('.todo-list li').count();
  expect(activeTodos).toBe(2);
});