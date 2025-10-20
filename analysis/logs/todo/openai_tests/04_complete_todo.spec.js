const { test, expect } = require('@playwright/test');

test('Add two todos "Buy eggs" and "Clean room" and press enter after each one of them, mark the second as completed, and verify its style changes.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  
  const todoInput = page.getByRole('textbox', { name: 'What needs to be done?' });
  
  await expect(todoInput).toBeVisible();
  await todoInput.fill('Buy eggs');
  await todoInput.press('Enter');
  
  await expect(todoInput).toBeVisible();
  await todoInput.fill('Clean room');
  await todoInput.press('Enter');
  
  const todoItem = page.getByRole('checkbox', { name: 'Toggle Todo' }).nth(1);
  await expect(todoItem).toBeVisible();
  await todoItem.check();
  
  const completedTodo = page.locator('.todo-list li.completed').nth(0);
  await expect(completedTodo).toContainText('Clean room');
});