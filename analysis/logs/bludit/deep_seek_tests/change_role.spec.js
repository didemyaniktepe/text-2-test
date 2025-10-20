const { test, expect } = require('@playwright/test');

test('change user role', async ({ page }) => {
    await page.goto('http://localhost:8001/admin');
    
    const usernameField = page.getByRole('textbox', {name: 'Username'});
    await expect(usernameField).toBeVisible();
    await usernameField.fill('admin');

    const passwordField = page.getByRole('textbox', {name: 'Password'});
    await expect(passwordField).toBeVisible();
    await passwordField.fill('admin1');

    const loginButton = page.locator('form').locator('button.btn');
    await expect(loginButton).toBeVisible();
    await loginButton.click();

    await expect(page).toHaveURL(/.+/);

    const usersLink = page.getByRole('link', {name: 'Users'});
    await expect(usersLink).toBeVisible();
    await usersLink.click();

    await expect(page).toHaveURL(/.+/);

    const newEditorUserLink = page.getByRole('link', {name:'neweditor'});
    await expect(newEditorUserLink).toBeVisible();
    await newEditorUserLink.click();

    await expect(page).toHaveURL(/.+/);

    const roleDropdown = page.getByRole('combobox', {name: 'Role'});
    await expect(roleDropdown).toBeVisible();
    await roleDropdown.selectOption('Admin', { exact: true });

    const saveButton = page.getByRole('button', {name: 'Save'});
    await expect(saveButton).toBeVisible();
    await saveButton.click();

    await expect(page).toHaveURL(/.+/);
});