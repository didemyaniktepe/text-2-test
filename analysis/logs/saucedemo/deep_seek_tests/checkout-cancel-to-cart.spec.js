const { test, expect } = require('@playwright/test');

test('Login with \'standard_user\' / \'secret_sauce\'. Add \'Sauce Labs Bolt T-Shirt\' then open the cart and proceed to Checkout. On \'Your Information\', click CANCEL and verify you are returned to the cart without losing the item.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  await expect(page.getByRole('textbox', {name:'Username'})).toBeVisible();
  await page.getByRole('textbox', {name:'Username'}).fill('standard_user');
  
  await expect(page.getByRole('textbox', { name: 'Password' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Password' }).fill('secret_sauce');
  
  await expect(page.locator('[data-test="login-button"]')).toBeVisible();
  await page.locator('[data-test="login-button"]').click();
  await expect(page).toHaveURL(/.*inventory\.html/);
  
  await expect(page.locator('#add-to-cart-sauce-labs-bolt-t-shirt')).toBeVisible();
  await page.locator('#add-to-cart-sauce-labs-bolt-t-shirt').click();
  
  await expect(page.getByText('1').first()).toBeVisible();
  await page.getByText('1').first().click();
  await expect(page).toHaveURL(/.*cart\.html/);
  
  await expect(page.getByRole('button', {name:'Checkout'})).toBeVisible();
  await page.getByRole('button', {name:'Checkout'}).click();
  await expect(page).toHaveURL(/.*checkout-step-one\.html/);
  
  await expect(page.getByRole('button', {name:'Cancel'})).toBeVisible();
  await page.getByRole('button', {name:'Cancel'}).click();
  await expect(page).toHaveURL(/.*cart\.html/);
  
  await expect(page.getByRole('link', {name: 'Sauce Labs Bolt T-Shirt'})).toBeVisible();
  await expect(page.locator('.cart_quantity')).toHaveText('1');
});