const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login Go to settings and then go to language tab and change language as Turkish', async ({ page }) => {
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

  const settingsLink = page.getByRole('link', { name: 'General' });
  await expect(settingsLink).toBeVisible();
  await settingsLink.click();
  await expect(page).toHaveURL(/.*settings/);
  await page.waitForLoadState('networkidle');

  const languageTab = page.getByRole('tab', { name: 'Language' });
  await expect(languageTab).toBeVisible();
  await languageTab.click();
  await expect(page).toHaveURL(/.*settings/);
  await page.waitForLoadState('networkidle');

  const languageDropdown = page.getByRole('combobox', { name: 'Language' });
  await expect(languageDropdown).toBeVisible();
  await languageDropdown.click();
  const turkishOption = page.getByRole('option', { name: 'Türkçe' });
  await expect(turkishOption).toBeVisible();
  await turkishOption.click();
  
  const saveButton = page.getByRole('button', { name: 'Save' });
  await expect(saveButton).toBeVisible();
  await saveButton.click();
});