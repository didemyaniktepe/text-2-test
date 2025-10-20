const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login, Go to content and then delete how to Write Thesis content ', async ({ page }) => {
  await page.goto('http://localhost:8001/admin/');

  const usernameInput = page.getByRole('textbox', {name: 'Username'});
  await expect(usernameInput).toBeVisible();
  await usernameInput.fill('admin');

  const passwordInput = page.getByRole('textbox', {name: 'Password'});
  await expect(passwordInput).toBeVisible();
  await passwordInput.fill('admin1');

  const loginButton = page.locator('form').locator('button.btn');
  await expect(loginButton).toBeVisible();
  await loginButton.click();

  await expect(page).toHaveURL(/.+/);

  const contentLink = page.getByRole('link', {name: 'Content'}).first();
  await expect(contentLink).toBeVisible();
  await contentLink.click();

  await expect(page).toHaveURL(/.+/);

  const deleteLink = page.locator('tbody tr').nth(0).getByRole('link', {name: 'Delete'});
  await expect(deleteLink).toBeVisible();
  await deleteLink.click();

  await expect(page).toHaveURL(/.+/);
});