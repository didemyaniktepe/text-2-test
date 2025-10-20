const { test, expect } = require('@playwright/test');

test('Add three todos (Todo 1, Todo 2, Todo 3) press enter after each one of them, mark two of them as completed, then click Clear completed and verify that exactly one active todo remains in the list.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await expect(page).toHaveURL(/.+/);

  const todoInput = page.getByRole('textbox', { name: 'What needs to be done?' });
  
  await expect(todoInput).toBeVisible();
  await todoInput.fill('Todo 1');
  await todoInput.press('Enter');
  
  await expect(todoInput).toBeVisible();
  await todoInput.fill('Todo 2');
  await todoInput.press('Enter');
  
  await expect(todoInput).toBeVisible();
  await todoInput.fill('Todo 3');
  await todoInput.press('Enter');
  
  const checkboxes = page.locator('input[type="checkbox"]');
  await checkboxes.nth(0).check();
  await checkboxes.nth(1).check();
  
  const clearCompletedButton = page.getByRole('button', { name: 'Clear completed' });
  await expect(clearCompletedButton).toBeVisible();
  await clearCompletedButton.click();
  
  const remainingTodos = page.locator('.todo-list li');
  await expect(remainingTodos).toHaveCount(1);
});