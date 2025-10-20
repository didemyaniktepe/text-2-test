const { test, expect } = require('@playwright/test');

test('Login with standard_user / secret_sauce. Add Sauce Labs Onesie to cart from Products, open the cart, click REMOVE, and verify the cart is empty and the badge disappears.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  const usernameField = page.getByRole('textbox', { name: 'Username' });
  await expect(usernameField).toBeVisible();
  await usernameField.fill('standard_user');
  
  const passwordField = page.getByRole('textbox', { name: 'Password' });
  await expect(passwordField).toBeVisible();
  await passwordField.fill('secret_sauce');
  
  const loginButton = page.locator('#login-button');
  await expect(loginButton).toBeVisible();
  await expect(loginButton).toBeEnabled();
  await loginButton.click();
  
  await expect(page).toHaveURL(/inventory\.html/);
  
  const addToCartButton = page.locator('#add-to-cart-sauce-labs-onesie');
  await expect(addToCartButton).toBeVisible();
  await expect(addToCartButton).toBeEnabled();
  await addToCartButton.click();
  
  const cartLink = page.locator('[data-test="shopping-cart-link"]');
  await expect(cartLink).toBeVisible();
  await cartLink.click();
  
  await expect(page).toHaveURL(/cart\.html/);
  
  const removeButton = page.getByRole('button', { name: 'Remove' });
  await expect(removeButton).toBeVisible();
  await expect(removeButton).toBeEnabled();
  await removeButton.click();
  
  const cartItems = page.locator('.cart_item');
  await expect(cartItems).toHaveCount(0);
  
  const cartBadge = page.locator('.shopping_cart_badge');
  await expect(cartBadge).not.toBeVisible();
});