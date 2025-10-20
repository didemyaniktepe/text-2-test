const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login, Go to category and then add new category as Movie and save it', async ({ page }) => {
  await page.goto('http://localhost:8001/admin/');

  const usernameField = page.getByRole('textbox', { name: 'Username' });
  await expect(usernameField).toBeVisible();
  await usernameField.fill('admin');

  const passwordField = page.getByRole('textbox', { name: 'Password' });
  await expect(passwordField).toBeVisible();
  await passwordField.fill('admin1');

  const loginButton = page.locator('form').locator('button.btn');
  await expect(loginButton).toBeEnabled();
  await loginButton.click();

  await expect(page).toHaveURL(/.+/);

  const categoriesLink = page.getByRole('link', { name: 'Categories' });
  await expect(categoriesLink).toBeVisible();
  await categoriesLink.click();

  await expect(page).toHaveURL(/.+/);

  const addCategoryLink = page.getByRole('link', { name: 'Add a new category' });
  await expect(addCategoryLink).toBeVisible();
  await addCategoryLink.click();

  await expect(page).toHaveURL(/.+/);

  const categoryNameField = page.getByRole('textbox', { name: 'Name' });
  await expect(categoryNameField).toBeVisible();
  await categoryNameField.fill('Movie');

  const saveButton = page.locator('form').locator('button.btn').filter({ hasText: 'Save' });
  await expect(saveButton).toBeEnabled();
  await saveButton.click();

  await expect(page).toHaveURL(/.+/);

  const newCategory = page.getByRole('link', { name: 'Movie' }).first();
  await expect(newCategory).toBeVisible();
});