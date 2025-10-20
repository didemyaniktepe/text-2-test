const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login then go to categories the go to Didem and write description and save it', async ({ page }) => {
  await page.goto('http://localhost:8001/admin');

  const usernameField = page.getByRole('textbox', { name: 'Username' });
  await expect(usernameField).toBeVisible();
  await usernameField.fill('admin');

  const passwordField = page.getByRole('textbox', { name: 'Password' });
  await expect(passwordField).toBeVisible();
  await passwordField.fill('admin1');

  const loginButton = page.locator('form').locator('button.btn');
  await expect(loginButton).toBeVisible();
  await loginButton.click();
  await expect(page).toHaveURL(/.*dashboard/);
  await page.waitForLoadState('networkidle');

  await page.goto('http://localhost:8001/admin/categories');
  await expect(page).toHaveURL(/categories/);

  const didemLink = page.locator('a[href="/admin/edit-category/didem"]');
  await expect(didemLink).toBeVisible();
  await didemLink.click();
  await expect(page).toHaveURL(/.*edit-category.*didem/);

  const descriptionField = page.getByRole('textbox', { name: 'Description' });
  await expect(descriptionField).toBeVisible();
  await descriptionField.fill('New description');

  const saveButton = page.getByRole('button', { name: 'Save' });
  await expect(saveButton).toBeVisible();
  await saveButton.click();
  await expect(page).toHaveURL(/.*categories$/);
});