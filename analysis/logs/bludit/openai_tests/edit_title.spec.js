const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login then navigate to http://localhost:8001/admin/content and Click edit and change the title', async ({ page }) => {
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

  await expect(page).toHaveURL(/\/admin/);

  await page.goto('http://localhost:8001/admin/content');

  await expect(page).toHaveURL(/\/admin\/content/);

  const editLink = page.locator('tbody tr').first().getByRole('link', { name: 'Edit' });
  await expect(editLink).toBeVisible();
  await editLink.click();

  const titleField = page.getByRole('textbox', { name: 'Enter title' });
  await expect(titleField).toBeVisible();
  await titleField.fill('New Thesis Title');

  const saveButton = page.getByRole('button', { name: 'Save' });
  await expect(saveButton).toBeVisible();
  await expect(saveButton).toBeEnabled();
  await saveButton.click();

  await expect(page).toHaveURL(/.*content/);
  await page.waitForLoadState('networkidle');
});