const { test, expect } = require('@playwright/test');

test('Login with "standard_user" / "secret_sauce". Add "Sauce Labs Backpack" and navigate to the cart. Click CHECKOUT, fill First Name "March", Last Name "April", Zip "10115", continue to Overview, then click CANCEL and verify you return to the Products page.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');

  // Step 1: Login
  await expect(page.getByRole('textbox', { name: 'Username' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Username' }).fill('standard_user');
  await expect(page.getByRole('textbox', { name: 'Password' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Password' }).fill('secret_sauce');
  await expect(page.locator('#login-button')).toBeVisible();
  await page.locator('#login-button').click();
  await expect(page).toHaveURL(/inventory\.html/);

  // Step 4: Add to Cart
  await expect(page.locator('#add-to-cart-sauce-labs-backpack')).toBeVisible();
  await page.locator('#add-to-cart-sauce-labs-backpack').click();

  // Step 5: Navigate to Cart
  await expect(page.locator('[data-test="shopping-cart-link"]')).toBeVisible();
  await page.locator('[data-test="shopping-cart-link"]').click();
  await expect(page).toHaveURL(/cart\.html/);

  // Step 6: Checkout
  await expect(page.getByRole('button', { name: 'Checkout' })).toBeVisible();
  await page.getByRole('button', { name: 'Checkout' }).click();
  await expect(page).toHaveURL(/checkout-step-one\.html/);

  // Step 7-9: Fill Checkout Information
  await expect(page.getByRole('textbox', { name: 'First Name' })).toBeVisible();
  await page.getByRole('textbox', { name: 'First Name' }).fill('March');
  await expect(page.getByRole('textbox', { name: 'Last Name' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Last Name' }).fill('April');
  await expect(page.getByRole('textbox', { name: 'Zip/Postal Code' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Zip/Postal Code' }).fill('10115');

  // Step 10: Continue
  await expect(page.locator('#continue')).toBeVisible();
  await page.locator('#continue').click();
  await expect(page).toHaveURL(/checkout-step-two\.html/);

  // Step 11: Cancel and return to Products page
  await expect(page.getByRole('button', { name: 'Cancel' })).toBeVisible();
  await page.getByRole('button', { name: 'Cancel' }).click();
  await expect(page).toHaveURL(/inventory\.html/);

  // Step 12: Verify Products page
  await expect(page.getByRole('link', { name: 'Sauce Labs Backpack' })).toBeVisible();
  await expect(page.locator('[data-test="shopping-cart-link"]')).toHaveText('1');
});