const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login then go to users and edit user description', async ({ page }) => {
    await page.goto('http://localhost:8001/admin');

    const usernameField = page.getByRole('textbox', {name: 'Username'});
    await expect(usernameField).toBeVisible();
    await usernameField.fill('admin');

    const passwordField = page.getByRole('textbox', {name: 'Password'});
    await expect(passwordField).toBeVisible();
    await passwordField.fill('admin1');

    const loginButton = page.locator('form').locator('button.btn');
    await expect(loginButton).toBeEnabled();
    await loginButton.click();

    await expect(page).toHaveURL(/.+/);

    const usersLink = page.getByRole('link', {name: 'Users'});
    await expect(usersLink).toBeVisible();
    await usersLink.click();

    await expect(page).toHaveURL(/.+/);

    const editUserLink = page.locator('tbody tr').nth(0).getByRole('link', { name: 'Edit' });
    await expect(editUserLink).toBeVisible();
    await editUserLink.click();

    await expect(page).toHaveURL(/.+/);

    const descriptionField = page.getByRole('textbox',{ name:'Description' });
    await expect(descriptionField).toBeVisible();
    await descriptionField.fill('Updated user description for admin user');

    const saveButton = page.getByRole('button', {name:'Save'});
    await expect(saveButton).toBeEnabled();
    await saveButton.click();

    await expect(page).toHaveURL(/.+/);

    const updatedDescription = page.getByRole('textbox',{ name:'Description' });
    await expect(updatedDescription).toBeVisible();
    expect(await updatedDescription.inputValue()).toBe('Updated user description for admin user');
});
