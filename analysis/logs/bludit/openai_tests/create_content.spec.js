const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login Go to create new content and write title How to write thesis and then write something in content and save it', async ({ page }) => {
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
  await expect(page).toHaveURL(/.+/);

  const newContentLink = page.getByRole('link', { name: 'New content' });
  await expect(newContentLink).toBeVisible();
  await newContentLink.click();
  await expect(page).toHaveURL(/.+/);

  const titleField = page.getByRole('textbox', { name: 'Enter title' });
  await expect(titleField).toBeVisible();
  await titleField.fill('How to write thesis');

  const contentFrame = page.frameLocator('#jseditor_ifr').locator('body');
  await expect(contentFrame).toBeVisible();
  await contentFrame.fill('This is the content of the thesis.');

  const saveButton = page.getByRole('button', { name: 'Save' });
  await expect(saveButton).toBeVisible();
  await saveButton.click();
  await expect(page).toHaveURL(/.+/);
});