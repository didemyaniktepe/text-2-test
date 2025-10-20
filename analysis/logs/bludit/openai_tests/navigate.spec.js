const { test, expect } = require('@playwright/test');

test('Navigate to http://localhost:8001/admin/', async ({ page }) => {
  await page.goto('http://localhost:8001');
  await page.goto('http://localhost:8001/admin/');
  await expect(page).toHaveURL('http://localhost:8001/admin/');
});