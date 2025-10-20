const { test, expect } = require('@playwright/test');

test("Add a todo with the text 'One To', press enter after it, mark it as completed, then click 'Clear completed' and verify the list is empty.", async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  
  const todoInput = page.getByRole('textbox', { name: 'What needs to be done?' });
  await expect(todoInput).toBeVisible();
  await todoInput.fill('One To');
  await todoInput.press('Enter');

  const todoCheckbox = page.locator('input[type="checkbox"]').first();
  await expect(todoCheckbox).toBeVisible();
  await todoCheckbox.check();

  const clearCompletedButton = page.getByRole('button', { name: 'Clear completed' });
  await expect(clearCompletedButton).toBeVisible();
  await expect(clearCompletedButton).toBeEnabled();
  await clearCompletedButton.click();

  const todoList = page.locator('.todo-list li');
  await expect(todoList).toHaveCount(0);
});