const { test, expect } = require('@playwright/test');

test('Login with standard_user / secret_sauce. On Products, add Sauce Labs Bike Light and Sauce Labs Fleece Jacket. Click the REMOVE button on the Backpack tile if present so only 2 items remain. Open the cart and verify Bike Light and Fleece Jacket are listed.', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');
  const usernameLocator = page.getByRole('textbox', { name: 'Username' });
  await expect(usernameLocator).toBeVisible();
  await usernameLocator.fill('standard_user');

  const passwordLocator = page.getByRole('textbox', { name: 'Password' });
  await expect(passwordLocator).toBeVisible();
  await passwordLocator.fill('secret_sauce');

  const loginButton = page.locator('#login-button');
  await expect(loginButton).toBeEnabled();
  await loginButton.click();
  await expect(page).toHaveURL(/inventory\.html/);

  const bikeLightAddButton = page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]');
  await expect(bikeLightAddButton).toBeVisible();
  await bikeLightAddButton.click();

  const fleeceJacketAddButton = page.getByRole('button', { name: 'Add to cart' }).nth(0);
  await expect(fleeceJacketAddButton).toBeVisible();
  await fleeceJacketAddButton.click();

  const backpackRemoveButton = page.locator('#remove-sauce-labs-backpack');
  const backpackRemoveButtonVisible = await backpackRemoveButton.isVisible();
  if (backpackRemoveButtonVisible) {
    await backpackRemoveButton.click();
  }

  const cartIcon = page.locator('[data-test="shopping-cart-link"]');
  await expect(cartIcon).toBeVisible();
  await cartIcon.click();
  await expect(page).toHaveURL(/cart\.html/);

  const bikeLightInCart = page.getByRole('link', { name: 'Sauce Labs Bike Light' });
  await expect(bikeLightInCart).toBeVisible();

  const fleeceJacketInCart = page.getByRole('link', { name: 'Sauce Labs Fleece Jacket' });
  await expect(fleeceJacketInCart).toBeVisible();
});