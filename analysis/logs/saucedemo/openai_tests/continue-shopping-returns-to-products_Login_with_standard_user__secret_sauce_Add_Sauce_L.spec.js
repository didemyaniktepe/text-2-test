const { test, expect } = require('@playwright/test');

test('Login with standard_user / secret_sauce. Add Sauce Labs Backpack to cart, open the cart, then click CONTINUE SHOPPING. Verify you return to the Products page and the cart badge still shows 1.', async ({ page }) => {
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

  await expect(page).toHaveURL(/.*inventory\.html/);

  const addToCartButton = page.getByRole('button', { name: 'Add to cart' }).nth(0);
  await expect(addToCartButton).toBeVisible();
  await addToCartButton.click();

  const cartBadge = page.locator('[data-test="shopping-cart-link"]');
  await expect(cartBadge).toBeVisible();
  await cartBadge.click();

  await expect(page).toHaveURL(/.*cart\.html/);

  const continueShoppingButton = page.getByRole('button', { name: 'Continue Shopping' });
  await expect(continueShoppingButton).toBeVisible();
  await expect(continueShoppingButton).toBeEnabled();
  await continueShoppingButton.click();

  await expect(page).toHaveURL(/.*inventory\.html/);
  
  const cartBadgeAfter = page.locator('.shopping_cart_badge');
  await expect(cartBadgeAfter).toHaveText('1');
});