const { test, expect } = require('@playwright/test');

test('Login with \'standard_user\' / \'secret_sauce\'. Add \'Sauce Labs Backpack\' to cart and go to Checkout. Fill First Name \'Jane\', Last Name \'Doe\', Zip \'80331\', continue to Overview, verify Item total is $29.99, Tax is $2.40, and Total is $32.39, then click FINISH and verify the completion page loads.', async ({ page }) => {
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
  await page.getByRole('textbox', { name: 'First Name' }).fill('Jane');
  
  await expect(page.getByRole('textbox', { name: 'Last Name' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Last Name' }).fill('Doe');
  
  await expect(page.getByRole('textbox', { name: 'Zip/Postal Code' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Zip/Postal Code' }).fill('80331');
  
  await expect(page.locator('#continue')).toBeVisible();
  await page.locator('#continue').click();
  await expect(page).toHaveURL(/.*checkout-step-two\.html/);
  
  await expect(page.locator('.summary_subtotal_label')).toContainText('$29.99');
  await expect(page.locator('.summary_tax_label')).toContainText('$2.40');
  await expect(page.locator('.summary_total_label')).toContainText('$32.39');
  
  await expect(page.getByRole('button', { name: 'Finish' })).toBeVisible();
  await page.getByRole('button', { name: 'Finish' }).click();
  await expect(page).toHaveURL(/.*checkout-complete\.html/);
  await expect(page.locator('.complete-header')).toBeVisible();
});