const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login then navigate to users and edit user description', async ({ page }) => {
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

  const usersLink = page.getByRole('link', { name: 'Users' });
  await expect(usersLink).toBeVisible();
  await usersLink.click();

  await expect(page).toHaveURL(/\/admin\/users/);

  const editUserLink = page.locator('tbody tr').first().getByRole('link', { name: 'Edit' });
  await expect(editUserLink).toBeVisible();
  await editUserLink.click();

  await expect(page).toHaveURL(/.*users.*edit/);

  const descriptionField = page.getByRole('textbox', { name: 'Description' });
  await expect(descriptionField).toBeVisible();
  await descriptionField.fill('New user description for administrator account');

  const saveButton = page.getByRole('button', { name: 'Save' });
  await expect(saveButton).toBeVisible();
  await expect(saveButton).toBeEnabled();
  await saveButton.click();

  await expect(page).toHaveURL(/.*users/);
  await page.waitForLoadState('networkidle');
});
