const { test, expect } = require('@playwright/test');

test('Add three todos ("Todo 1", "Todo 2", "Todo 3") press enter after each one of them, mark two of them as completed, then click "Clear completed" and verify that exactly one active todo remains in the list.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  
  const input = page.getByRole('textbox', { name: 'What needs to be done?' });
  
  await expect(input).toBeVisible();
  await input.fill('Todo 1');
  await input.press('Enter');

  await expect(input).toBeVisible();
  await input.fill('Todo 2');
  await input.press('Enter');

  await expect(input).toBeVisible();
  await input.fill('Todo 3');
  await input.press('Enter');
  
  const firstCheckbox = page.getByRole('checkbox', { name: 'Toggle Todo' }).first();
  const secondCheckbox = page.getByRole('checkbox', { name: 'Toggle Todo' }).nth(1);
  
  await expect(firstCheckbox).toBeVisible();
  await firstCheckbox.check();
  
  await expect(secondCheckbox).toBeVisible();
  await secondCheckbox.check();
  
  const clearCompletedButton = page.getByRole('button', { name: 'Clear completed' });
  
  await expect(clearCompletedButton).toBeVisible();
  await clearCompletedButton.click();
  
  const remainingTodos = page.locator('.todo-list li');
  
  await expect(remainingTodos).toHaveCount(1);
  await expect(remainingTodos.first()).toHaveText('Todo 2');
});