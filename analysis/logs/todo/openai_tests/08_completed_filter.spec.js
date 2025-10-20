const { test, expect } = require('@playwright/test');

test('Add three todos after each one of them, mark two as completed, then switch to Completed filter and verify only completed todos are displayed.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  
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
  
  const todoCheckbox1 = page.getByRole('checkbox', { name: 'Toggle Todo' }).nth(0);
  await expect(todoCheckbox1).toBeVisible();
  await todoCheckbox1.check();
  
  const todoCheckbox2 = page.getByRole('checkbox', { name: 'Toggle Todo' }).nth(1);
  await expect(todoCheckbox2).toBeVisible();
  await todoCheckbox2.check();
  
  const completedFilter = page.getByRole('link', { name: 'Completed' });
  await expect(completedFilter).toBeVisible();
  await completedFilter.click();
  
  await expect(page).toHaveURL(/#\/completed/);
  
  const completedTodos = page.locator('.todo-list li');
  await expect(completedTodos).toHaveCount(2);
});