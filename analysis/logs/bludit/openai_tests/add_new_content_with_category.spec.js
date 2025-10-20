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

  const newContentLink = page.getByRole('link', { name: 'New content' });
  await expect(newContentLink).toBeVisible();
  await newContentLink.click();

  await expect(page).toHaveURL(/\/admin\/new-content/);

  const titleField = page.getByRole('textbox', { name: 'Enter title' });
  await expect(titleField).toBeVisible();
  await titleField.fill('How to write thesis');

  const contentBody = page.frameLocator('#jseditor_ifr').locator('body');
  await expect(contentBody).toBeVisible();
  await contentBody.fill('This is the content for the thesis.');

  const optionsButton = page.getByRole('button', { name: 'Options' });
  await expect(optionsButton).toBeVisible();
  await optionsButton.click();

  const categoryDropdown = page.locator('#jscategory');
  await expect(categoryDropdown).toBeVisible();
  await categoryDropdown.selectOption({ value: 'books' });

  const saveButton = page.getByRole('button', { name: 'Save' });
  await expect(saveButton).toBeVisible();
  await expect(saveButton).toBeEnabled();
  await saveButton.click();

  await expect(page).toHaveURL(/\/admin\/content#published/);
});
