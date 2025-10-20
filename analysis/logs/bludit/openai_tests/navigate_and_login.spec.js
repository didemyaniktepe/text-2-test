const { test, expect } = require('@playwright/test');

test('Navigate to http://localhost:8001 and then go to admin panel username admin password admin1', async ({ page }) => {
  await page.goto('http://localhost:8001/admin/');
  await expect(page).toHaveURL('http://localhost:8001/admin/');

  const usernameField = page.getByRole('textbox', { name: 'Username' });
  await expect(usernameField).toBeVisible();
  await expect(usernameField).toBeEnabled();
  await usernameField.fill('admin');

  const passwordField = page.getByRole('textbox', { name: 'Password' });
  await expect(passwordField).toBeVisible();
  await expect(passwordField).toBeEnabled();
  await passwordField.fill('admin1');
  await passwordField.press('Enter');

  // Assuming successful login redirects or shows admin panel
  await expect(page).toHaveURL(/\/admin/);
});