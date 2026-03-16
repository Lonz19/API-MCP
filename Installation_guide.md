# Installation Guide — API-MCP Template

Complete step-by-step guide to set up the development environment and deploy this project from a clean machine.

---

## Part 1: Local Machine Setup

### 1.1 Install Python 3.11+

**macOS:**

```bash
brew install python@3.11
```

**Windows:**

Download from [python.org/downloads](https://www.python.org/downloads/). During install, check **"Add Python to PATH"**.

**Verify:**

```bash
python3 --version
```

---

### 1.2 Install Git

**macOS:**

```bash
brew install git
```

**Windows:**

Download from [git-scm.com](https://git-scm.com/). Use default options during install.

**Verify:**

```bash
git --version
```

**Configure Git (first time only):**

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

---

### 1.3 Install VS Code

Download from [code.visualstudio.com](https://code.visualstudio.com/).

**Recommended extensions:**

- Python (Microsoft)
- Ruff (Astral Software)
- GitLens

---

### 1.4 Install Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

If you don't have Node.js/npm:

**macOS:**

```bash
brew install node
```

**Windows:**

Download from [nodejs.org](https://nodejs.org/) (LTS version).

**Verify:**

```bash
claude --version
```

---

### 1.5 Install Homebrew (macOS only)

If you don't have Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## Part 2: Project Setup

### 2.1 Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/API-MCP.git
cd API-MCP
```

### 2.2 Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows
```

### 2.3 Install dependencies

```bash
pip install -r requirements.txt
```

### 2.4 Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

| Variable | Description | Where to get it |
|----------|-------------|-----------------|
| `API_KEY` | Protects your API endpoints | Generate: `openssl rand -hex 32` |
| `GEMINI_API_KEY` | Google Gemini API key | [aistudio.google.com](https://aistudio.google.com/) |
| `GEMINI_DEFAULT_MODEL` | Gemini model to use | Default: `gemini-3.1-flash-lite-preview` |

### 2.5 Run locally

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

### 2.6 Verify it works

```bash
# Health check (no auth needed)
curl http://localhost:8000/health

# Test an API endpoint
curl -X POST http://localhost:8000/api/v1/gemini \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}'
```

### 2.7 Run tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
```

### 2.8 Lint and format

```bash
ruff check app/ tests/      # Check for lint errors
ruff format app/ tests/      # Auto-format code
```

---

## Part 3: GitHub Setup

### 3.1 Create GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Name it `API-MCP` (or your preferred name)
3. Set to **Private** (recommended — it will contain API config)
4. Do NOT initialize with README (you already have one)

### 3.2 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/API-MCP.git
git branch -M main
git push -u origin main
```

### 3.3 Create the deploy branch

```bash
git checkout -b deploy
git push origin deploy
git checkout main
```

### 3.4 Enable GitHub Actions permissions

1. Go to your repo > **Settings > Actions > General**
2. Under **Workflow permissions**, select **Read and write permissions**
3. Click **Save**

### 3.5 Verify CI pipeline

Push any small change to `main` and go to the **Actions** tab. You should see the CI/CD workflow run with 4 jobs:

- **Lint** — checks code formatting and lint rules
- **Test** — runs all tests with coverage gate (80%)
- **Documentation Check** — verifies README.md and ARCHITECTURE.md exist
- **Deploy to Replit** — pushes to the `deploy` branch (only on `main` push)

---

## Part 4: Replit Deployment

### 4.1 Create the Repl

1. Go to [replit.com](https://replit.com) > **Create Repl** > **Import from GitHub**
2. Connect your GitHub account if needed
3. Select your repository and import the **`deploy`** branch
4. Wait for Replit to set up the environment

### 4.2 Configure secrets on Replit

Go to **Tools > Secrets** and add:

| Key | Value |
|-----|-------|
| `API_KEY` | Your production API key |
| `GEMINI_API_KEY` | Your Gemini API key |

> **Important:** Never put secrets in the `.replit` file — use the Secrets panel only.

### 4.3 Verify the app runs

Click **Run** in Replit. You should see uvicorn start. Test with:

```bash
curl https://YOUR-REPL-URL/health
```

Expected: `{"status":"ok","app":"API-MCP"}`

### 4.4 Deploy to production

1. Go to the **Deploy** tab in Replit
2. Select **Reserved VM**
3. Click **Deploy**
4. Wait for deployment to complete
5. Test the production URL:

```bash
curl https://YOUR-APP.replit.app/health
```

### 4.5 Deployment flow (ongoing)

After the initial setup, this is the flow for every code change:

```
Local machine                    GitHub                         Replit
─────────────                    ──────                         ──────
git push main ──────────> CI runs (lint/test/docs)
                           │
                           ├──> (fail) fix locally, push again
                           │
                           └──> (pass) auto-push to deploy branch
                                                                │
                          You: Replit Shell ─────────────────────┘
                          $ git fetch origin
                          $ git reset --hard origin/deploy
                          Then click Redeploy in Deploy tab
```

**Steps:**

1. Push code to `main` on GitHub
2. Watch GitHub Actions — all 4 jobs must go green
3. In the Replit Shell, run:
   ```bash
   git fetch origin && git reset --hard origin/deploy
   ```
4. Click **Redeploy** in the Replit Deploy tab
5. Verify: `curl https://YOUR-APP.replit.app/health`

> **Note:** Replit does not support auto-deploy from GitHub. Steps 3-4 are manual (~30 seconds).

---

## Part 5: Online Accounts Required

| Service | URL | What for | Plan needed |
|---------|-----|----------|-------------|
| GitHub | [github.com](https://github.com) | Source code, CI/CD | Free |
| Replit | [replit.com](https://replit.com) | Hosting/deployment | Core ($25/mo) |
| Google AI Studio | [aistudio.google.com](https://aistudio.google.com/) | Gemini API key | Free tier available |
| Anthropic | [console.anthropic.com](https://console.anthropic.com/) | Claude Code CLI | API key required |

---

## Part 6: Troubleshooting

### Local issues

| Problem | Fix |
|---------|-----|
| `python3: command not found` | Install Python and ensure it's on PATH |
| `pip: command not found` | Use `python3 -m pip` instead |
| `ModuleNotFoundError` | Activate venv: `source venv/bin/activate` |
| Tests fail with `extra_forbidden` | Check `.env` — variable names must match `app/core/config.py` exactly |
| `ruff format` changes files | Run `ruff format app/ tests/` before committing |

### GitHub Actions issues

| Problem | Fix |
|---------|-----|
| Lint job fails | Run `ruff format app/ tests/` and `ruff check app/ tests/` locally before pushing |
| Test job fails | Run `pytest tests/ -v` locally to see the failure |
| Deploy job fails with exit code 128 | Enable write permissions: Settings > Actions > General > Workflow permissions > Read and write |
| Deploy job fails on first push | Create the `deploy` branch first: `git checkout -b deploy && git push origin deploy && git checkout main` |

### Replit issues

| Problem | Fix |
|---------|-----|
| `git fetch` fails with `.lock` error | Run `rm /home/runner/workspace/.git/refs/remotes/origin/HEAD.lock` then retry |
| `git pull` says "divergent branches" | Use `git reset --hard origin/deploy` instead |
| App returns 500 after redeploy | Check Replit **Tools > Logs** for Python traceback |
| `ModuleNotFoundError` in Replit Shell | Run `/home/runner/workspace/.pythonlibs/bin/python -m pip install -r requirements.txt` |
| Secrets not found by app | Add them in **Tools > Secrets** (not in `.replit` file). Click Redeploy after adding. |
| App works in workspace but not deployment | You must click **Redeploy** after pulling new code — the deployment is a separate snapshot |
| `.replit` config lost after `git reset` | Delete the Repl and re-import from GitHub (deploy branch). Re-add secrets. |

---

## Quick Reference: Common Commands

```bash
# Start dev server
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80

# Lint and format
ruff check app/ tests/
ruff format app/ tests/

# Deploy workflow
git add .
git commit -m "your message"
git push origin main
# Wait for CI green, then on Replit:
# git fetch origin && git reset --hard origin/deploy
# Click Redeploy
```
