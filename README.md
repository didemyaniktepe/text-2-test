# Text‑to‑Test 🚀

Generate end‑to‑end Playwright tests from natural‑language scenarios. The backend drives a real browser, analyzes the UI via a vision model, plans actions, selects robust locators, performs steps, and finally emits runnable JS tests.

## Project Structure 🏗️

```
text-to-test/
├── backend/                   # FastAPI backend + core engine
│   ├── src/infrastructure/    # OpenAI/DeepSeek clients, settings
│   ├── src/services/          # Orchestrator, planners, DOM extractor, performer
│   └── src/utils/             # JSON/locator/logger helpers
```

## Key Capabilities ✨

- Text LLM provider switch: OpenAI or DeepSeek R1 (reasoner) for selector planning 
- Real browser execution with Playwright to validate each step
- Emits complete Playwright JS tests with verified selectors

## Requirements 📦

- Python 3.11+
- Node.js (for Playwright runtime if needed)
- Playwright browsers: `npx playwright install --with-deps`
- OpenAI API key (for vision) and optionally DeepSeek API key (for text tasks)

## Setup ⚙️

1) Clone and enter repo
```bash
git clone https://github.com/didemyaniktepe/text-to-test.git
cd text-to-test
```

2) Backend env and deps (pyproject.toml / Poetry)
```bash
cd backend
# If Poetry is not installed: curl -sSL https://install.python-poetry.org | python3 -
poetry install
poetry run playwright install --with-deps
```

3) Playwright browsers (once)
```bash
npx playwright install --with-deps
```

4) Configure environment in `.env` 🔐
```env
# Provider for text-only tasks (selector planning, codegen): openai or deepseek
OPENAI_PROVIDER=deepseek
OPENAI_API_KEY=sk-openai-...
OPENAI_MODEL=gpt-4o-mini

# DeepSeek (used when OPENAI_PROVIDER=deepseek)
OPENAI_DEEPSEEK_API_KEY=sk-deepseek-...
OPENAI_DEEPSEEK_MODEL=deepseek-reasoner
OPENAI_DEEPSEEK_BASE_URL=https://api.deepseek.com

# Vision is always OpenAI with a vision-capable model
OPENAI_VISION_PROVIDER=openai
OPENAI_VISION_MODEL=gpt-4o
```

Notes:
- Vision pipeline requires an image‑capable model; `gpt-4o` is used by default.
- If `OPENAI_PROVIDER=deepseek`, only text tasks are routed to DeepSeek; vision stays on OpenAI.

## Run Backend ▶️

```bash
poetry run uvicorn src.main:app --reload
```

Swagger UI: http://localhost:8000/docs

## How It Works (Architecture) 🧭

- Orchestrator: `TestGeneratorService` runs an iteration loop:
  - Extract current DOM + screenshot (`DOMExtractorService`)
  - Plan next step from scenario + UI (`TestStepPlanner` → `VisionAnalysisClient` with `gpt-4o`)
  - Choose a robust locator and action (`ElementSelector` → `ElementSelectorClient` via OpenAI/DeepSeek)
  - Perform the action in browser (`ActionPerformer`/Playwright); collect failures for retries
  - Accumulate verified steps, then generate code (`TestCodeGeneratorClient`)


## Usage (Programmatic) 🛠️

Call the service from an endpoint or script with a scenario and URL. The service returns Playwright JS code. See `TestGeneratorService.generate()` for an end‑to‑end example.

## Troubleshooting 🧩

- 400 invalid content type (image_url): Ensure vision model is image‑capable and vision provider is OpenAI (`OPENAI_VISION_MODEL=gpt-4o`).
- Selector not found: The system records `failed_attempts` and retries with DOM context; check logs for the chosen selector and page state.


# text-2-test
