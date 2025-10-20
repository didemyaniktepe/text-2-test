const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 and click remember me then login Go to create new content and write title \'How to write thesis\' and then write something in content and select options then select category and save it', async ({ page }) => {
  // Navigate to admin page
  await page.goto('http://localhost:8001/admin');
  
  // Login with username and password
  const usernameField = page.getByRole('textbox', { name: 'Username' });
  await expect(usernameField).toBeVisible();
  await usernameField.fill('admin');
  
  const passwordField = page.getByRole('textbox', { name: 'Password' });
  await expect(passwordField).toBeVisible();
  await passwordField.fill('admin1');
  
  // Check remember me checkbox
  const rememberMeCheckbox = page.getByRole('checkbox', { name: 'Remember me' });
  await expect(rememberMeCheckbox).toBeVisible();
  await rememberMeCheckbox.check();
  
  // Click login button
  const loginButton = page.locator('form').locator('button.btn');
  await expect(loginButton).toBeVisible();
  await expect(loginButton).toBeEnabled();
  await loginButton.click();
  
  // Verify login success
  await expect(page).toHaveURL(/\/dashboard/);
  
  // Navigate to new content page
  const newContentLink = page.getByRole('link', { name: 'New content' });
  await expect(newContentLink).toBeVisible();
  await newContentLink.click();
  
  await expect(page).toHaveURL(/\/new-content/);
  
  // Fill in content details
  const titleField = page.getByRole('textbox', { name: 'Enter title' });
  await expect(titleField).toBeVisible();
  await titleField.fill('How to write thesis');
  
  // Fill content in iframe editor
  const contentFrame = page.frameLocator('#jseditor_ifr').locator('body');
  await expect(contentFrame).toBeVisible();
  await contentFrame.fill('something');
  
  // Open options and select category
  const optionsButton = page.getByRole('button', { name: 'Options' });
  await expect(optionsButton).toBeVisible();
  await optionsButton.click();
  
  const categoryDropdown = page.getByRole('combobox', { name: 'CATEGORY' });
  await expect(categoryDropdown).toBeVisible();
  await categoryDropdown.selectOption('a category');
  
  // Save the content
  const saveButton = page.getByRole('button', { name: 'Save' });
  await expect(saveButton).toBeVisible();
  await expect(saveButton).toBeEnabled();
  await saveButton.click();
  
  // Verify save success
  await expect(page).toHaveURL(/\/new-content/);
});
