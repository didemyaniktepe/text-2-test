const { test, expect } = require('@playwright/test');

test('Login app with username admin password admin1 then login, Go to category and then add new category as Movies', async ({ page }) => {
  await page.goto('http://localhost:8001/admin/');

  const usernameInput = page.getByRole('textbox', {name: 'Username'});
  const passwordInput = page.getByRole('textbox', {name: 'Password'});
  const loginButton = page.locator('form').locator('button.btn');
  const categoriesLink = page.getByRole('link', {name: 'Categories'});
  const addCategoryLink = page.getByRole('link', {name: 'Add a new category'});
  const nameInput = page.getByRole('textbox', {name: 'Name'});

  await expect(usernameInput).toBeVisible();
  await expect(usernameInput).toBeEnabled();
  await usernameInput.fill('admin');

  await expect(passwordInput).toBeVisible();
  await expect(passwordInput).toBeEnabled();
  await passwordInput.fill('admin1');

  await expect(loginButton).toBeVisible();
  await expect(loginButton).toBeEnabled();
  await loginButton.click();
  await expect(page).toHaveURL(/.+/);

  await expect(categoriesLink).toBeVisible();
  await expect(categoriesLink).toBeEnabled();
  await categoriesLink.click();
  await expect(page).toHaveURL(/.+/);

  await expect(addCategoryLink).toBeVisible();
  await expect(addCategoryLink).toBeEnabled();
  await addCategoryLink.click();
  await expect(page).toHaveURL(/.+/);

  await expect(nameInput).toBeVisible();
  await expect(nameInput).toBeEnabled();
  await nameInput.fill('Movies');
  await expect(page).toHaveURL(/.+/);

  await expect(page).toHaveURL(/.*category.*/);
});