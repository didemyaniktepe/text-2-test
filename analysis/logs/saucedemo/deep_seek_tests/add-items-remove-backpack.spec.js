const { test, expect } = require('@playwright/test');

test('Login with \'standard_user\' / \'secret_sauce\'. On Products, add \'Sauce Labs Bike Light\' and \'Sauce Labs Fleece Jacket\'. Click the REMOVE button on the Backpack tile if present so only 2 items remain. Open the cart and verify Bike Light and Fleece Jacket are listed.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  await expect(page.getByRole('textbox', { name: 'Username' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Username' }).fill('standard_user');
  
  await expect(page.getByRole('textbox', { name: 'Password' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Password' }).fill('secret_sauce');
  
  await expect(page.locator('[data-test="login-button"]')).toBeVisible();
  await page.locator('[data-test="login-button"]').click();
  await expect(page).toHaveURL(/.*inventory\.html/);
  
  await expect(page.locator('#add-to-cart-sauce-labs-bike-light')).toBeVisible();
  await page.locator('#add-to-cart-sauce-labs-bike-light').click();
  
  await expect(page.locator('#add-to-cart-sauce-labs-fleece-jacket')).toBeVisible();
  await page.locator('#add-to-cart-sauce-labs-fleece-jacket').click();
  
  const backpackRemoveButton = page.locator('[data-test="remove-sauce-labs-backpack"]');
  if (await backpackRemoveButton.isVisible()) {
    await backpackRemoveButton.click();
  }
  
  await expect(page.getByText('2')).toBeVisible();
  await page.getByText('2').first().click();
  await expect(page).toHaveURL(/.*cart\.html/);
  
  await expect(page.locator('.cart_item')).toHaveCount(2);
  await expect(page.getByText('Sauce Labs Bike Light')).toBeVisible();
  await expect(page.getByText('Sauce Labs Fleece Jacket')).toBeVisible();
});