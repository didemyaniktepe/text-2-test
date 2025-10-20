const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login then navigate to http://localhost:8001/admin/categories the go to Didem and delete it', async ({ page }) => {
  await page.goto('http://localhost:8001/admin');

  const usernameField = page.getByRole('textbox', {name: 'Username'});
  await expect(usernameField).toBeVisible();
  await usernameField.fill('admin');

  const passwordField = page.getByRole('textbox',{ name:'Password' });
  await expect(passwordField).toBeVisible();
  await passwordField.fill('admin1');

  const loginButton = page.locator('form').locator('button.btn');
  await expect(loginButton).toBeVisible();
  await loginButton.click();

  await expect(page).toHaveURL(/.*admin.*/);

  const categoriesLink = page.getByRole('link', {name: 'Categories'});
  await expect(categoriesLink).toBeVisible();
  await categoriesLink.click();

  const didemLink = page.locator('tbody tr').nth(0).getByRole('link', { name: 'Didem' }).first();
  await expect(didemLink).toBeVisible();
  await didemLink.click();

  const deleteButton = page.getByRole('button', {name: 'Delete'}).nth(0);
  await expect(deleteButton).toBeVisible();
  await deleteButton.click();

  await expect(page).toHaveURL(/.*admin.*/);
});
