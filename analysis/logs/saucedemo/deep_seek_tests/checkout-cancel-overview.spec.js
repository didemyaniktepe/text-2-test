const { test, expect } = require('@playwright/test');

test('Login with \'standard_user\' / \'secret_sauce\'. Add \'Sauce Labs Backpack\' and navigate to the cart. Click CHECKOUT, fill First Name \'March\', Last Name \'April\', Zip \'10115\', continue to Overview, then click CANCEL and verify you return to the Products page.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  await expect(page.getByRole('textbox', { name: 'Username' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Username' }).fill('standard_user');
  
  await expect(page.getByRole('textbox', { name: 'Password' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Password' }).fill('secret_sauce');
  
  await expect(page.locator('[data-test="login-button"]')).toBeVisible();
  await page.locator('[data-test="login-button"]').click();
  await expect(page).toHaveURL(/.*inventory\.html/);
  
  await expect(page.locator('#add-to-cart-sauce-labs-backpack')).toBeVisible();
  await page.locator('#add-to-cart-sauce-labs-backpack').click();
  
  await expect(page.getByText('1').first()).toBeVisible();
  await page.getByText('1').first().click();
  await expect(page).toHaveURL(/.*cart\.html/);
  
  await expect(page.getByRole('button', { name: 'Checkout' })).toBeVisible();
  await page.getByRole('button', { name: 'Checkout' }).click();
  await expect(page).toHaveURL(/.*checkout-step-one\.html/);
  
  await expect(page.getByRole('textbox', { name: 'First Name' })).toBeVisible();
  await page.getByRole('textbox', { name: 'First Name' }).fill('March');
  
  await expect(page.getByRole('textbox', { name: 'Last Name' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Last Name' }).fill('April');
  
  await expect(page.getByRole('textbox', { name: 'Zip/Postal Code' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Zip/Postal Code' }).fill('10115');
  
  await expect(page.locator('[data-test=\'continue\']')).toBeVisible();
  await page.locator('[data-test=\'continue\']').click();
  await expect(page).toHaveURL(/.*checkout-step-two\.html/);
  
  await expect(page.getByRole('button', { name: 'Cancel' })).toBeVisible();
  await page.getByRole('button', { name: 'Cancel' }).click();
  await expect(page).toHaveURL(/.*inventory\.html/);
  
  await expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).toBeVisible();
  await expect(page.getByText('1').first()).toBeVisible();
});