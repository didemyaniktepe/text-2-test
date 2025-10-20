const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './logs/Checkturio_2/deep_seek_tests',
  workers: 1,
  use: {
    headless: false,
    viewport: { width: 1280, height: 720 },
    video: 'on-first-retry',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],
});
