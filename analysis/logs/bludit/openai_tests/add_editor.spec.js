const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login Go to Users and then add one user role as Editor ', async ({ page }) => {
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

  await expect(page).toHaveURL(/.*admin.*dashboard.*/);
  
  await page.goto('http://localhost:8001/admin/users');

  await expect(page).toHaveURL(/.*admin.*users.*/);

  const addUserLink = page.getByRole('link', { name: 'Add a new user' });
  await expect(addUserLink).toBeVisible();
  await addUserLink.click();

  const roleDropdown = page.getByRole('combobox', { name: 'Role' });
  await expect(roleDropdown).toBeVisible();
  await roleDropdown.selectOption('Editor');

  const newUsernameField = page.getByRole('textbox', { name: 'Username' });
  await expect(newUsernameField).toBeVisible();
  await newUsernameField.fill('new_user_editor');

  const newPasswordField = page.locator('#jsnew_password');
  await expect(newPasswordField).toBeVisible();
  await newPasswordField.fill('password123');

  const confirmPasswordField = page.locator('#jsconfirm_password');
  await expect(confirmPasswordField).toBeVisible();
  await confirmPasswordField.fill('password123');

  const emailField = page.getByRole('textbox', { name: 'Email' });
  await expect(emailField).toBeVisible();
  await emailField.fill('user@example.com');

  const saveButton = page.getByRole('button', { name: 'Save' });
  await expect(saveButton).toBeVisible();
  await expect(saveButton).toBeEnabled();
  await saveButton.click();

  await expect(page).toHaveURL(/.*admin.*new-user.*/);
});