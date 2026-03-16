# API-MCP

A **FastAPI template** for hosting HTTP APIs and MCP (Model Context Protocol) servers in a single application, with CI/CD deployment to Replit via GitHub.

## Features

- **HTTP APIs** with versioning, auth, structured errors, and OpenAPI docs
- **MCP servers** using Streamable HTTP transport
- **Working API key authentication**
- **Correlation ID logging** for request tracing
- **CI/CD pipeline** (GitHub Actions) with lint, test, coverage gate, and Replit deployment
- **Extensible template** designed for use with Claude Code

---

## Quick Start

### Prerequisites

- Python 3.11+ ([python.org](https://www.python.org/downloads/))
- Git ([git-scm.com](https://git-scm.com/))
- VS Code ([code.visualstudio.com](https://code.visualstudio.com/))
- Claude Code CLI (`npm install -g @anthropic-ai/claude-code`)
- GitHub account
- Replit account (Core subscription)

### Local Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/API-MCP.git
cd API-MCP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Run Locally

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80

# Or use the script
./scripts/test.sh
```

### Lint & Format

```bash
ruff check app/ tests/     # Lint
ruff format app/ tests/     # Format
```

---

## API Documentation

### Health Check

```
GET /health
```

No authentication required.

```json
{"status": "ok", "app": "API-MCP"}
```

---

### Summarize API

Summarize a PDF document by uploading a file or providing a URL.

```
POST /api/v1/summarize
Header: X-API-Key: your-api-key
```

**Upload a file:**

```bash
curl -X POST http://localhost:8000/api/v1/summarize \
  -H "X-API-Key: your-api-key" \
  -F "file=@document.pdf"
```

**Provide a URL:**

```bash
curl -X POST http://localhost:8000/api/v1/summarize \
  -H "X-API-Key: your-api-key" \
  -F "url=https://example.com/document.pdf"
```

**Response:**

```json
{
  "summary_markdown": "# Document Summary\n\n**Pages processed:** 5\n\n## Content Preview\n\n...",
  "source": "upload:document.pdf",
  "pages": 5
}
```

#### Python Example

```python
import httpx

# Upload a file
with open("document.pdf", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/api/v1/summarize",
        headers={"X-API-Key": "your-api-key"},
        files={"file": ("document.pdf", f, "application/pdf")},
    )
print(response.json()["summary_markdown"])

# From URL
response = httpx.post(
    "http://localhost:8000/api/v1/summarize",
    headers={"X-API-Key": "your-api-key"},
    data={"url": "https://example.com/document.pdf"},
)
print(response.json()["summary_markdown"])
```

#### JavaScript Example

```javascript
// Upload a file
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await fetch("http://localhost:8000/api/v1/summarize", {
  method: "POST",
  headers: { "X-API-Key": "your-api-key" },
  body: formData,
});
const data = await response.json();
console.log(data.summary_markdown);

// From URL
const formData2 = new FormData();
formData2.append("url", "https://example.com/document.pdf");

const response2 = await fetch("http://localhost:8000/api/v1/summarize", {
  method: "POST",
  headers: { "X-API-Key": "your-api-key" },
  body: formData2,
});
const data2 = await response2.json();
console.log(data2.summary_markdown);
```

---

### Gemini API

Send a prompt to a Google Gemini model.

```
POST /api/v1/gemini
Header: X-API-Key: your-api-key
Content-Type: application/json
```

**Request body:**

```json
{
  "prompt": "Explain quantum computing in 3 sentences.",
  "model": "gemini-3.1-flash-lite-preview"
}
```

The `model` field is optional — defaults to `GEMINI_DEFAULT_MODEL` from config.

**Response:**

```json
{
  "model": "gemini-3.1-flash-lite-preview",
  "response_text": "Quantum computing uses quantum bits...",
  "metadata": {
    "prompt_tokens": 12,
    "candidates_tokens": 45,
    "total_tokens": 57
  }
}
```

#### Python Example

```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/v1/gemini",
    headers={"X-API-Key": "your-api-key"},
    json={"prompt": "Explain quantum computing in 3 sentences."},
)
data = response.json()
print(data["response_text"])
```

#### JavaScript Example

```javascript
const response = await fetch("http://localhost:8000/api/v1/gemini", {
  method: "POST",
  headers: {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    prompt: "Explain quantum computing in 3 sentences.",
  }),
});
const data = await response.json();
console.log(data.response_text);
```

---

## MCP Servers

### Summarize MCP

**Endpoint:** `/mcp/summarize`

Tools:

| Tool | Description |
|------|-------------|
| `summarize_pdf_url` | Summarize a PDF from a URL |
| `summarize_pdf_text` | Generate a summary from raw text |

### Deep Search MCP

**Endpoint:** `/mcp/deep-search`

Tools:

| Tool | Description |
|------|-------------|
| `deep_search_url` | Summarize a PDF from URL + Gemini analysis with a query |
| `deep_search_text` | Summarize text + Gemini analysis with a query |

### Connecting an MCP Client

MCP servers use Streamable HTTP transport. Configure your MCP client to connect to:

```
http://localhost:8000/mcp/summarize/mcp
http://localhost:8000/mcp/deep-search/mcp
```

Example Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "summarize": {
      "url": "http://localhost:8000/mcp/summarize/mcp"
    },
    "deep-search": {
      "url": "http://localhost:8000/mcp/deep-search/mcp"
    }
  }
}
```

---

## Replit Deployment Guide

### Prerequisites

- GitHub repository with this template pushed to `main`
- Replit Core account
- GitHub Actions enabled on the repo (Settings > Actions > General > Allow all actions)
- GitHub Actions write permission (Settings > Actions > General > Workflow permissions > Read and write)

### Step 1 — Create the deploy branch

From your local machine:

```bash
git checkout -b deploy
git push origin deploy
git checkout main
```

### Step 2 — Create the Repl

1. Go to [replit.com](https://replit.com) > **Create Repl** > **Import from GitHub**
2. Connect your GitHub account if needed
3. Select your repository and import the **`deploy`** branch
4. Wait for Replit to set up the environment

### Step 3 — Configure Secrets on Replit

In **Tools > Secrets**, add:

| Key | Value |
|-----|-------|
| `API_KEY` | Your production API key |
| `GEMINI_API_KEY` | Your Google Gemini API key |

### Step 4 — Verify the app runs

Click **Run** in Replit. You should see uvicorn start. Test with:

```bash
curl https://YOUR-REPL-URL/health
```

Expected: `{"status":"ok","app":"API-MCP"}`

### Step 5 — Deploy

Go to the **Deploy** tab > select **Reserved VM** > click **Deploy**.

### Deployment Flow

```
git push main
  > GitHub Actions: lint + test + docs-check
    > (all pass) auto-push to deploy branch
      > You: git reset --hard origin/deploy (in Replit Shell)
        > You: click Redeploy in Replit UI
```

1. Push to `main` on GitHub
2. GitHub Actions runs lint, tests, and docs check
3. On success, CI pushes to the `deploy` branch automatically
4. In the Replit Shell, pull the latest: `git fetch origin && git reset --hard origin/deploy`
5. Click **Redeploy** in the Replit Deploy tab

> **Note:** Replit does not support auto-deploy from GitHub. Steps 4-5 are manual.

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `git fetch` fails with `.lock` error | `rm /home/runner/workspace/.git/refs/remotes/origin/HEAD.lock` then retry |
| `git pull` says "divergent branches" | Use `git reset --hard origin/deploy` instead |
| App returns 500 after redeploy | Check Replit Logs tab for Python traceback |
| CI deploy job fails with exit code 128 | Enable write permissions: repo Settings > Actions > General > Workflow permissions > Read and write |
| `ModuleNotFoundError` in Replit Shell | Run `/home/runner/workspace/.pythonlibs/bin/python -m pip install -r requirements.txt` |
| Secrets not found by app | Add them in Replit Tools > Secrets (not in `.replit` file). Redeploy after adding. |

---

## Project Structure

```
API-MCP/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── api/v1/                    # HTTP API routes
│   │   ├── router.py              # v1 router aggregator
│   │   ├── summarize.py           # Summarize API
│   │   └── gemini.py              # Gemini API
│   ├── mcp/                       # MCP server implementations
│   │   ├── summarize_mcp.py       # Summarize MCP
│   │   └── deep_search_mcp.py     # Deep Search MCP
│   ├── core/                      # Config, auth, logging, errors
│   ├── models/                    # Pydantic models
│   └── services/                  # Business logic
├── tests/                         # Unit, integration, and MCP tests
├── .github/workflows/ci.yml       # CI/CD pipeline
├── requirements.txt
├── .env.example
├── ARCHITECTURE.md                # Detailed architecture guide
└── CLAUDE.md                      # Instructions for Claude Code
```

---

## Working with Claude Code

Claude Code is the recommended tool for extending this template. Here are effective prompts:

### Add a New API

> "Add a new API endpoint POST /api/v1/translate that takes a JSON body with `text` and `target_language` fields, calls an external translation service, and returns the translated text. Include unit and integration tests, and update the README."

### Add a New MCP Server

> "Create a new MCP server at /mcp/translate that exposes a `translate_text` tool using the translate API service. Include MCP tests and update the README."

### Fix a Bug

> "The Summarize API returns a 500 when the PDF URL returns a 404. It should return a 422 with a clear error message. Fix it and add a test case."

### Add a Feature

> "Add rate limiting to all API endpoints — 100 requests per minute per API key. Use an in-memory store for now."

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "error_code",
  "detail": "Human-readable description of what went wrong",
  "status_code": 422
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad request (missing input) |
| 401 | Missing API key |
| 403 | Invalid API key |
| 422 | Validation error / processing error |
| 502 | External API error (e.g., Gemini) |
| 503 | Service not configured |

---

## License

MIT
