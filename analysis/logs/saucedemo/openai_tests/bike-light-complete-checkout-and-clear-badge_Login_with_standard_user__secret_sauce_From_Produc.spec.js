const { test, expect } = require('@playwright/test');

test('Login with standard_user / secret_sauce. From Products, add Sauce Labs Bike Light, open the cart and verify quantity shows 1. Proceed through Checkout with First Name Test, Last Name User, Zip 52200, finish the order, then navigate back Home and confirm the cart badge is cleared.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  await expect(page.getByRole('textbox', { name: 'Username' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Username' }).fill('standard_user');
  
  await expect(page.getByRole('textbox', { name: 'Password' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Password' }).fill('secret_sauce');
  
  await expect(page.locator('#login-button')).toBeVisible();
  await page.locator('#login-button').click();
  
  await expect(page).toHaveURL(/inventory.html/);
  
  await expect(page.locator('#add-to-cart-sauce-labs-bike-light')).toBeVisible();
  await page.locator('#add-to-cart-sauce-labs-bike-light').click();
  
  await expect(page.locator('[data-test="shopping-cart-link"]')).toBeVisible();
  await page.locator('[data-test="shopping-cart-link"]').click();
  
  await expect(page).toHaveURL(/cart.html/);
  await expect(page.locator('.cart_quantity')).toHaveText('1');
  
  await expect(page.getByRole('button', { name: 'Checkout' })).toBeVisible();
  await page.getByRole('button', { name: 'Checkout' }).click();
  
  await expect(page).toHaveURL(/checkout-step-one.html/);
  
  await expect(page.getByRole('textbox', { name: 'First Name' })).toBeVisible();
  await page.getByRole('textbox', { name: 'First Name' }).fill('Test');
  
  await expect(page.getByRole('textbox', { name: 'Last Name' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Last Name' }).fill('User');
  
  await expect(page.getByRole('textbox', { name: 'Zip/Postal Code' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Zip/Postal Code' }).fill('52200');
  
  await expect(page.locator('#continue')).toBeVisible();
  await page.locator('#continue').click();
  
  await expect(page).toHaveURL(/checkout-step-two.html/);
  
  await expect(page.getByRole('button', { name: 'Finish' })).toBeVisible();
  await page.getByRole('button', { name: 'Finish' }).click();
  
  await expect(page).toHaveURL(/checkout-complete.html/);
  
  await expect(page.getByRole('button', { name: 'Back Home' })).toBeVisible();
  await page.getByRole('button', { name: 'Back Home' }).click();
  
  await expect(page).toHaveURL(/inventory.html/);
  
  await expect(page.locator('.shopping_cart_link')).toBeVisible();
  await expect(page.locator('.shopping_cart_link .shopping_cart_badge')).not.toBeVisible();
});