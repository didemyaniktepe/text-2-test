const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login then go to users click on newuser user and change it role Editor to Admin and save it', async ({ page }) => {
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
  
  await page.goto('http://localhost:8001/admin/users');
  await expect(page).toHaveURL(/.*users/);
  await page.waitForLoadState('networkidle');
  
  const newUserLink = page.getByRole('link', { name: 'newuser' });
  await expect(newUserLink).toBeVisible();
  await newUserLink.click();
  await expect(page).toHaveURL(/.*dashboard/);
  await page.waitForLoadState('networkidle');
  
  const roleDropdown = page.getByRole('combobox', { name: 'Role' });
  await expect(roleDropdown).toBeVisible();
  await roleDropdown.selectOption('Administrator');
  
  const saveButton = page.locator('form').locator('button.btn');
  await expect(saveButton).toBeVisible();
  await expect(saveButton).toBeEnabled();
  await saveButton.click();
  await expect(page).toHaveURL(/.*dashboard/);
  await page.waitForLoadState('networkidle');
});