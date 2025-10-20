const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 and click remember me then login Go to create new content and write title "How to write thesis" and then write something in content and select options then select books as a category and save it', async ({ page }) => {
  await page.goto('http://localhost:8001/admin');
  
  const usernameField = page.getByRole('textbox', { name: 'Username' });
  await expect(usernameField).toBeVisible();
  await usernameField.fill('admin');

  const passwordField = page.getByRole('textbox', { name: 'Password' });
  await expect(passwordField).toBeVisible();
  await passwordField.fill('admin1');

  const rememberMeCheckbox = page.getByRole('checkbox', { name: 'Remember me' });
  await expect(rememberMeCheckbox).toBeVisible();
  await rememberMeCheckbox.check();

  const loginButton = page.locator('form').locator('button.btn');
  await expect(loginButton).toBeVisible();
  await expect(loginButton).toBeEnabled();
  await loginButton.click();

  await expect(page).toHaveURL(/\/admin\/dashboard/);

});
