const { test, expect } = require('@playwright/test');

test('Login with \'standard_user\' / \'secret_sauce\'. Add \'Sauce Labs Onesie\' to cart from Products, open the cart, click REMOVE, and verify the cart is empty and the badge disappears.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  await expect(page.getByRole('textbox', {name:'Username'})).toBeVisible();
  await page.getByRole('textbox', {name:'Username'}).fill('standard_user');
  
  await expect(page.getByRole('textbox', {name:'Password'})).toBeVisible();
  await page.getByRole('textbox', {name:'Password'}).fill('secret_sauce');
  
  await expect(page.locator('[data-test="login-button"]')).toBeVisible();
  await expect(page.locator('[data-test="login-button"]')).toBeEnabled();
  await page.locator('[data-test="login-button"]').click();
  await expect(page).toHaveURL(/.*inventory\.html/);
  
  await expect(page.locator('#add-to-cart-sauce-labs-onesie')).toBeVisible();
  await page.locator('#add-to-cart-sauce-labs-onesie').click();
  
  await expect(page.getByText('1').first()).toBeVisible();
  await page.getByText('1').first().click();
  await expect(page).toHaveURL(/.*cart\.html/);
  
  await expect(page.getByRole('button', {name:'Remove'})).toBeVisible();
  await page.getByRole('button', {name:'Remove'}).click();
  
  await expect(page.locator('.cart_item')).toHaveCount(0);
  await expect(page.locator('.shopping_cart_badge')).toHaveCount(0);
  
  await expect(page.getByRole('button', {name:'Continue Shopping'})).toBeVisible();
  await page.getByRole('button', {name:'Continue Shopping'}).click();
  await expect(page).toHaveURL(/.*inventory\.html/);
});