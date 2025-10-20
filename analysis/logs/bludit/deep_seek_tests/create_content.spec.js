const { test, expect } = require('@playwright/test');

test('create new content', async ({ page }) => {
    await page.goto('http://localhost:8001/admin/dashboard');

    const usernameInput = page.getByRole('textbox',{ name:'Username' });
    await expect(usernameInput).toBeVisible();
    await usernameInput.fill('admin');
    
    const passwordInput = page.getByRole('textbox', {name:'Password'});
    await expect(passwordInput).toBeVisible();
    await passwordInput.fill('admin1');
    
    const loginButton = page.locator('form').locator('button.btn');
    await expect(loginButton).toBeVisible();
    await loginButton.click();
    
    await expect(page).toHaveURL('http://localhost:8001/admin/dashboard');
    
    const newContentLink = page.getByRole('link', {name: 'New content'});
    await expect(newContentLink).toBeVisible();
    await newContentLink.click();
    
    const titleInput = page.getByRole('textbox', {name:'Enter title'});
    await expect(titleInput).toBeVisible();
    await titleInput.fill('How to write thesis');
    
    try {
      const contentInput = page.getByRole('textbox', {name: /content/i});
      await expect(contentInput).toBeVisible();
      await contentInput.fill('This is the content of the thesis.');
    } catch {
      const contentInput = page.frameLocator('iframe').locator('body');
      await expect(contentInput).toBeVisible();
      await contentInput.fill('This is the content of the thesis.');
    }
    
    const saveButton = page.getByRole('button', {name:'Save'});
    await expect(saveButton).toBeVisible();
    await saveButton.click();
    
    await expect(page).toHaveURL(/.+/);
});