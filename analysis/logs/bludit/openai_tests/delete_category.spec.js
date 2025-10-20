const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login then navigate to http://localhost:8001/admin/categories then go to Didem and delete it', async ({ page }) => {
  await page.goto('http://localhost:8001/admin');

  const usernameField = page.getByRole('textbox', { name: 'Username' });
  await expect(usernameField).toBeVisible();
  await usernameField.fill('admin');

  const passwordField = page.getByRole('textbox', { name: 'Password' });
  await expect(passwordField).toBeVisible();
  await passwordField.fill('admin1');

  const loginButton = page.locator('form').locator('button.btn');
  await expect(loginButton).toBeVisible();
  await expect(loginButton).toBeEnabled();
  await loginButton.click();
  await expect(page).toHaveURL(/admin/);

  await page.goto('http://localhost:8001/admin/categories');
  await expect(page).toHaveURL(/admin\/categories/);

  const didemLink = page.locator('a[href="/admin/edit-category/didem"]');
  await expect(didemLink).toBeVisible();
  await didemLink.click();
  await expect(page).toHaveURL(/.*edit-category.*didem/);

  const deleteButton = page.getByRole('button', { name: 'Delete' }).first();
  await expect(deleteButton).toBeVisible();
  await expect(deleteButton).toBeEnabled();
  await deleteButton.click();

  // Assert that the item was deleted, e.g., by checking the absence of "Didem"
  await expect(page).toHaveURL(/.*categories$/);
});