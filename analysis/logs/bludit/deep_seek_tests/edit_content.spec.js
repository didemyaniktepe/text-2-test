const { test, expect } = require('@playwright/test');

test('username admin password admin1 then login go to content edit click Inside Out and write some content about movie and save it', async ({ page }) => {
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

  await expect(page).toHaveURL(/.+/);

  const contentLink = page.getByRole('link', {name: 'Content'}).nth(1);
  await expect(contentLink).toBeVisible();
  await contentLink.click();

  await expect(page).toHaveURL(/.+/);

  const editLink = page.locator('tbody tr').nth(2).getByRole('link', { name: 'Edit' });
  await expect(editLink).toBeVisible();
  await editLink.click();

  await expect(page).toHaveURL(/.+/);

  const contentField = page.frameLocator('#jseditor_ifr').locator('body');
  await expect(contentField).toBeVisible();
  await contentField.fill('Some content about the movie.');

  const saveButton = page.getByRole('button', {name:'Save'});
  await expect(saveButton).toBeVisible();
  await saveButton.click();

  await expect(page).toHaveURL(/.+/);
});