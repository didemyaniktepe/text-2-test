const { test, expect } = require('@playwright/test');

test('Login with \'standard_user\' / \'secret_sauce\'. Add \'Sauce Labs Backpack\' to cart, open the cart, then click CONTINUE SHOPPING. Verify you return to the Products page and the cart badge still shows 1.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  await expect(page.getByRole('textbox', { name: 'Username' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Username' }).fill('standard_user');
  
  await expect(page.getByRole('textbox', { name: 'Password' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Password' }).fill('secret_sauce');
  
  await expect(page.locator('[data-test="login-button"]')).toBeVisible();
  await page.locator('[data-test="login-button"]').click();
  await expect(page).toHaveURL(/.*inventory\.html/);
  
  await expect(page.locator('[data-test="add-to-cart-sauce-labs-backpack"]')).toBeVisible();
  await page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click();
  
  await expect(page.getByText('1').first()).toBeVisible();
  await page.getByText('1').first().click();
  await expect(page).toHaveURL(/.*cart\.html/);
  
  await expect(page.getByRole('button', { name: 'Continue Shopping' })).toBeVisible();
  await page.getByRole('button', { name: 'Continue Shopping' }).click();
  await expect(page).toHaveURL(/.*inventory\.html/);
  
  await expect(page.getByText('1').first()).toBeVisible();
});