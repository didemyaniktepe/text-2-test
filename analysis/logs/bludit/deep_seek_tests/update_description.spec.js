const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login then go to categories the go to Didem and write description and save it', async ({ page }) => {
  await page.goto('http://localhost:8001/admin');

  const usernameField = page.getByRole('textbox', {name: 'Username'});
  await expect(usernameField).toBeVisible();
  await usernameField.fill('admin');

  const passwordField = page.getByRole('textbox', { name:'Password' });
  await expect(passwordField).toBeVisible();
  await passwordField.fill('admin1');

  const loginButton = page.locator('form').locator('button.btn');
  await expect(loginButton).toBeVisible();
  await loginButton.click();
  await expect(page).toHaveURL(/.+/);

  const categoriesLink = page.getByRole('link', {name: 'Categories'});
  await expect(categoriesLink).toBeVisible();
  await categoriesLink.click();

  const didemLink = page.locator('tbody tr').nth(0).getByRole('link', { name: 'Didem' }).first();
  await expect(didemLink).toBeVisible();
  await didemLink.click();

  const descriptionField = page.getByRole('textbox', {name: 'Description'});
  await expect(descriptionField).toBeVisible();
  await descriptionField.fill('Sample description');

  const saveButton = page.getByRole('button', {name: 'Save'});
  await expect(saveButton).toBeVisible();
  await saveButton.click();

  await expect(page).toHaveURL(/.+/);  
});