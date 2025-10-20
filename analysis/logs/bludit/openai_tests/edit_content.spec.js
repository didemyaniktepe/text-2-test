const { test, expect } = require('@playwright/test');

test('username admin password admin1 then login go to content edit click Inside Out and write some content about movie and save it', async ({ page }) => {
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
  await expect(page).toHaveURL(/.+\/dashboard/);

  const contentLink = page.getByRole('link', { name: 'Content' });
  await expect(contentLink).toBeVisible();
  await contentLink.click();
  await expect(page).toHaveURL(/.+\/content/);

  const editLink = page.locator('tbody tr').nth(2).getByRole('link', { name: 'Edit' });
  await expect(editLink).toBeVisible();
  await editLink.click();
  await expect(page).toHaveURL(/.+\/content\/inside-out\/edit/);

  const contentTextarea = page.getByRole('textbox', { name: 'Content' });
  await expect(contentTextarea).toBeVisible();
  await contentTextarea.fill('This is some content about the movie Inside Out.');

  const saveButton = page.getByRole('button', { name: 'Save' });
  await expect(saveButton).toBeVisible();
  await saveButton.click();
  await expect(page).toHaveURL(/.+\/content/);
});
