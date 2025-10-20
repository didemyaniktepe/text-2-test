const { test, expect } = require('@playwright/test');

test('Login with standard_user / secret_sauce. From Products, change the sort dropdown to Price (low to high). Verify Sauce Labs Onesie ($7.99) appears before higher-priced items. Add it to cart and verify the cart badge shows 1.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  const usernameLocator = page.getByRole('textbox', { name: 'Username' });
  await expect(usernameLocator).toBeVisible();
  await usernameLocator.fill('standard_user');

  const passwordLocator = page.getByRole('textbox', { name: 'Password' });
  await expect(passwordLocator).toBeVisible();
  await passwordLocator.fill('secret_sauce');

  const loginButton = page.locator('#login-button');
  await expect(loginButton).toBeVisible();
  await expect(loginButton).toBeEnabled();
  await loginButton.click();
  await expect(page).toHaveURL(/.*inventory.html/);

  const sortDropdown = page.getByRole('combobox');
  await expect(sortDropdown).toBeVisible();
  await sortDropdown.selectOption('lohi');

  const itemLocator = page.getByText('Sauce Labs Onesie');
  await expect(itemLocator).toBeVisible();
  const priceLocator = page.getByText('$7.99');
  await expect(priceLocator).toBeVisible();

  const addToCartButton = page.getByRole('button', { name: 'Add to cart' }).first();
  await expect(addToCartButton).toBeVisible();
  await addToCartButton.click();

  const cartBadge = page.locator('.shopping_cart_badge');
  await expect(cartBadge).toBeVisible();
  await expect(cartBadge).toHaveText('1');
});