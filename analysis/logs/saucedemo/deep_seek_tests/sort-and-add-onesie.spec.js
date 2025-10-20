const { test, expect } = require('@playwright/test');

test('Login with \'standard_user\' / \'secret_sauce\'. From Products, change the sort dropdown to \'Price (low to high)\'. Verify \'Sauce Labs Onesie\' ($7.99) appears before higher-priced items. Add it to cart and verify the cart badge shows 1.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  await expect(page.getByRole('textbox', {name:'Username'})).toBeVisible();
  await page.getByRole('textbox', {name:'Username'}).fill('standard_user');
  
  await expect(page.getByRole('textbox', {name:'Password'})).toBeVisible();
  await page.getByRole('textbox', {name:'Password'}).fill('secret_sauce');
  
  await expect(page.locator('[data-test="login-button"]')).toBeVisible();
  await expect(page.locator('[data-test="login-button"]')).toBeEnabled();
  await page.locator('[data-test="login-button"]').click();
  await expect(page).toHaveURL(/.*inventory\.html/);
  
  await expect(page.getByRole('combobox')).toBeVisible();
  await page.getByRole('combobox').selectOption('lohi');
  
  const productContainer = page.locator('.inventory_item');
  await expect(productContainer.first()).toBeVisible();
  
  const onesieItem = page.locator('.inventory_item:has-text("Sauce Labs Onesie")');
  const firstItem = productContainer.first();
  await expect(onesieItem).toBeVisible();
  await expect(firstItem).toContainText('Sauce Labs Onesie');
  
  await expect(page.locator('#add-to-cart-sauce-labs-onesie')).toBeVisible();
  await page.locator('#add-to-cart-sauce-labs-onesie').click();
  
  await expect(page.locator('.shopping_cart_badge')).toBeVisible();
  await expect(page.locator('.shopping_cart_badge')).toHaveText('1');
});