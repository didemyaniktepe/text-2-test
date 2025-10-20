const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login, Go to category and then add new category as Movies and save it', async ({ page }) => {
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

  await expect(page).toHaveURL(/.*dashboard/);
  await page.waitForLoadState('networkidle');

  await page.goto('http://localhost:8001/admin/categories');

  await expect(page).toHaveURL(/categories/);

  const addCategoryLink = page.getByRole('link', { name: 'Add a new category' });
  await expect(addCategoryLink).toBeVisible();
  await addCategoryLink.click();

  await expect(page).toHaveURL(/.*new-category.*/);

  const nameField = page.getByRole('textbox', { name: 'Name' });
  await expect(nameField).toBeVisible();
  await nameField.fill('Movies');

  const saveButton = page.locator('form').locator('button.btn');
  await expect(saveButton).toBeVisible();
  await expect(saveButton).toBeEnabled();
  await saveButton.click();

  await expect(page).toHaveURL(/.*categories$/);
});