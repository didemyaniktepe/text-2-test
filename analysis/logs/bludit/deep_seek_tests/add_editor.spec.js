const { test, expect } = require('@playwright/test');

test('add editor', async ({ page }) => {
    await page.goto('http://localhost:8001/admin/');

    const usernameField = page.getByRole('textbox', {name: 'Username'});
    await expect(usernameField).toBeVisible();
    await usernameField.fill('admin');

    const passwordField = page.getByRole('textbox', {name: 'Password'});
    await expect(passwordField).toBeVisible();
    await passwordField.fill('admin1');

    const loginButton = page.locator('form').locator('button.btn');
    await expect(loginButton).toBeVisible();
    await loginButton.click();

    const usersLink = page.getByRole('link', {name: 'Users'});
    await expect(usersLink).toBeVisible();
    await usersLink.click();

    const addUserLink = page.getByRole('link', {name: /add.*user/i}).first();
    await expect(addUserLink).toBeVisible();
    await addUserLink.click();

    const roleDropdown = page.getByLabel('Role');
    await expect(roleDropdown).toBeVisible();
    await roleDropdown.selectOption('Editor');

    const newUserField = page.getByRole('textbox', {name: 'Username'});
    await expect(newUserField).toBeVisible();
    await newUserField.fill('new_editor');

    const newPasswordField = page.getByRole('textbox', {name: 'Password'}).first();
    await expect(newPasswordField).toBeVisible();
    await newPasswordField.fill('password123');

    const passwordConfirmField = page.getByRole('textbox', {name: /confirm/i}).or(page.getByRole('textbox', {name: /password.*confirm/i}));
    await expect(passwordConfirmField).toBeVisible();
    await passwordConfirmField.fill('password123');

    const emailField = page.getByRole('textbox', {name: 'Email'});
    await expect(emailField).toBeVisible();
    await emailField.fill('editor@example.com');

    const saveButton = page.getByRole('button', {name: 'Save'});
    await expect(saveButton).toBeVisible();
    await saveButton.click();

    await expect(page).toHaveURL(/.+/);
});
