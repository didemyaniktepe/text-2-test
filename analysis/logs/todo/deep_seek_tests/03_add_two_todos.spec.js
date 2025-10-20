const { test, expect } = require('@playwright/test');

test('Add two todos "Buy eggs" and "Clean room" and press enter after each one of them, mark the second as completed, and verify its style changes.', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  
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
  
  const cleanRoomCheckbox = page.locator('text=Clean room').locator('xpath=..').locator('.toggle');
  await expect(cleanRoomCheckbox).toBeVisible();
  await cleanRoomCheckbox.check();
  
  const cleanRoomItem = page.getByText('Clean room');
  await expect(cleanRoomItem).toHaveClass(/completed/);
});