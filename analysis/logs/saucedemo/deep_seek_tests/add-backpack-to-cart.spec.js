const { test, expect } = require('@playwright/test');

test('Login with username \'standard_user\' and password \'secret_sauce\'. From Products, add \'Sauce Labs Backpack\' to cart. Open the cart and verify the item name and price are shown as $29.99.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  const usernameField = page.getByRole('textbox', { name: 'Username' });
  await expect(usernameField).toBeVisible();
  await usernameField.fill('standard_user');
  
  const passwordField = page.getByRole('textbox', { name: 'Password' });
  await expect(passwordField).toBeVisible();
  await passwordField.fill('secret_sauce');
  
  const loginButton = page.locator('[data-test="login-button"]');
  await expect(loginButton).toBeVisible();
  await expect(loginButton).toBeEnabled();
  await loginButton.click();
  
  await expect(page).toHaveURL(/.*inventory\.html/);
  
  const addToCartButton = page.locator('#add-to-cart-sauce-labs-backpack');
  await expect(addToCartButton).toBeVisible();
  await expect(addToCartButton).toBeEnabled();
  await addToCartButton.click();
  
  const cartIcon = page.getByText('1').first();
  await expect(cartIcon).toBeVisible();
  await cartIcon.click();
  
  await expect(page).toHaveURL(/.*cart\.html/);
  
  const itemName = page.getByRole('link', { name: 'Sauce Labs Backpack' });
  await expect(itemName).toBeVisible();
  
  const itemPrice = page.locator('.inventory_item_price');
  await expect(itemPrice).toBeVisible();
  await expect(itemPrice).toHaveText('$29.99');
});