const { test, expect } = require('@playwright/test');

test('Login with \'standard_user\' / \'secret_sauce\'. Add \'Sauce Labs Backpack\' from Products. Verify the button label toggles from \'ADD TO CART\' to \'REMOVE\'. Click \'REMOVE\' and confirm the button returns to \'ADD TO CART\' and the cart badge decrements.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  await expect(page.getByRole('textbox', { name: 'Username' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Username' }).fill('standard_user');
  
  await expect(page.getByRole('textbox', { name: 'Password' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Password' }).fill('secret_sauce');
  
  await expect(page.locator('[data-test="login-button"]')).toBeVisible();
  await expect(page.locator('[data-test="login-button"]')).toBeEnabled();
  await page.locator('[data-test="login-button"]').click();
  
  await expect(page).toHaveURL(/.*inventory\.html/);
  
  const addToCartButton = page.locator('#add-to-cart-sauce-labs-backpack');
  await expect(addToCartButton).toBeVisible();
  await expect(addToCartButton).toHaveText('Add to cart');
  await addToCartButton.click();
  
  const removeButton = page.locator('#remove-sauce-labs-backpack');
  await expect(removeButton).toBeVisible();
  await expect(removeButton).toHaveText('Remove');
  
  const cartBadge = page.locator('.shopping_cart_badge');
  await expect(cartBadge).toBeVisible();
  await expect(cartBadge).toHaveText('1');
  
  await removeButton.click();
  
  await expect(addToCartButton).toBeVisible();
  await expect(addToCartButton).toHaveText('Add to cart');
  await expect(cartBadge).not.toBeVisible();
});