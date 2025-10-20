const { test, expect } = require('@playwright/test');

test('Login with "standard_user" / "secret_sauce". Add "Sauce Labs Backpack" from Products. Verify the button label toggles from "ADD TO CART" to "REMOVE". Click "REMOVE" and confirm the button returns to "ADD TO CART" and the cart badge decrements.', async ({ page }) => {
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
  
  const addToCartButton = page.getByRole('button', { name: 'Add to cart' }).nth(0);
  await expect(addToCartButton).toBeVisible();
  await addToCartButton.click();
  
  const removeButton = page.getByRole('button', { name: 'Remove' });
  await expect(removeButton).toBeVisible();
  await removeButton.click();
  
  const addToCartButtonAgain = page.getByRole('button', { name: 'Add to cart' }).nth(0);
  await expect(addToCartButtonAgain).toBeVisible();
  
  const cartBadge = page.locator('.shopping_cart_badge');
  await expect(cartBadge).not.toBeVisible();
});