def get_playwright_config_template(use_storage_state=True):
    storage_state_config = """
    storageState: path.resolve(__dirname, '../../../storage_state.json'),""" if use_storage_state else ""
    
    return f"""// @ts-check
const {{ defineConfig, devices }} = require('@playwright/test');
const path = require('path');

module.exports = defineConfig({{
  testDir: './',
  outputDir: path.join(__dirname, 'test-results'),
  projects: [
    {{
      name: 'chromium',
      use: {{ ...devices['Desktop Chrome'] }},
    }},
  ],
  use: {{
    headless: {{headless}},
    launchOptions: {{
      slowMo: {{slow_mo}},
    }},
    viewport: {{ width: {{viewport_width}}, height: {{viewport_height}} }},{storage_state_config}
  }},
  reporter: [
    ['html'],
    ['list', {{ printSteps: true }}]
  ],
  timeout: {{timeout}},
}});""" 