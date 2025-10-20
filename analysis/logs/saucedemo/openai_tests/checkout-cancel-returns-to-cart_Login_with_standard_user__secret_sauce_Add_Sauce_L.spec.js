const { test, expect } = require('@playwright/test');

test('Login with \'standard_user\' / \'secret_sauce\'. Add \'Sauce Labs Bolt T-Shirt\' then open the cart and proceed to Checkout. On \'Your Information\', click CANCEL and verify you are returned to the cart without losing the item.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  
  const usernameField = page.getByRole('textbox', { name: 'Username' });
  await expect(usernameField).toBeVisible();
  await usernameField.fill('standard_user');
  
  const passwordField = page.getByRole('textbox', { name: 'Password' });
  await expect(passwordField).toBeVisible();
  await passwordField.fill('secret_sauce');
  
  const loginButton = page.locator('#login-button');
  await expect(loginButton).toBeVisible();
  await expect(loginButton).toBeEnabled();
  await loginButton.click();
  
  await expect(page).toHaveURL(/.*inventory.html/);
  
  const addToCartButton = page.getByRole('button', { name: 'Add to cart' }).nth(2);
  await expect(addToCartButton).toBeVisible();
  await addToCartButton.click();
  
  const cartIcon = page.locator('[data-test="shopping-cart-link"]');
  await expect(cartIcon).toBeVisible();
  await cartIcon.click();
  
  await expect(page).toHaveURL(/.*cart.html/);
  
  const checkoutButton = page.getByRole('button', { name: 'Checkout' });
  await expect(checkoutButton).toBeVisible();
  await expect(checkoutButton).toBeEnabled();
  await checkoutButton.click();
  
  await expect(page).toHaveURL(/.*checkout-step-one.html/);
  
  const cancelButton = page.getByRole('button', { name: 'Cancel' });
  await expect(cancelButton).toBeVisible();
  await expect(cancelButton).toBeEnabled();
  await cancelButton.click();
  
  await expect(page).toHaveURL(/.*cart.html/);
  
  const itemLink = page.getByRole('link', { name: 'Sauce Labs Bolt T-Shirt' });
  await expect(itemLink).toBeVisible();
});