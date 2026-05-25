# WSL2 Python Development Environment Setup Guide

> Complete reference for setting up a Python/AI development environment on Windows 11 using WSL2.
> Based on actual setup performed on 2026-05-25.

---

## What this guide produces

A clean, professional Python development environment for AI/data work:

- WSL2 with Ubuntu 26.04 LTS (or current latest)
- Python managed via pyenv (project-isolated)
- Node.js managed via nvm
- Claude Code CLI authenticated
- VS Code on Windows connected to WSL via Remote-WSL
- A scaffolded Python project with virtual environment
- GitHub repository with SSH authentication

## Prerequisites

- Windows 11 (or Windows 10 build 19041+)
- Administrator access on your machine
- A GitHub account
- An Anthropic account with API access
- 60-90 minutes of focused time (2-3 hours wall clock with downloads/reboots)

## Placeholder convention used in this guide

Replace these with your actual values:

| Placeholder | Example |
|-------------|---------|
| `<linux-user>` | The username you set in Ubuntu (lowercase, no spaces) |
| `<github-email>` | The email tied to your GitHub account |
| `<real-name>` | Your real name for git commits |
| `<github-username>` | Your GitHub handle |
| `<project-name>` | Your project's directory name (use underscores, not hyphens, for Python compatibility) |

---

## Key decisions made before starting

### Why WSL2 over native Windows
Native Windows + Python + AI development tools has rough edges. Most documentation, tutorials, and Stack Overflow answers assume macOS or Linux. Known friction points:
- Path management issues
- File permission weirdness when AI tools edit files
- Line ending issues (CRLF vs LF)
- npm/pip packages that don't install cleanly
- MCP servers that document Linux install paths
- Bash scripts in tutorials that can't run directly

WSL2 gives you a real Linux environment running inside Windows, with seamless VS Code integration. Eliminates all of these.

### Why VS Code over PyCharm Community
- Claude Code integration is dramatically better in VS Code (official extension)
- PyCharm Community Edition lacks Jupyter support; VS Code has it free
- Lighter weight, faster iteration
- Industry standard for AI/Python work
- Tutorials and screenshots match what you'll see

### Why pyenv over apt for Python
- Each project can use a different Python version (3.11 vs 3.12, etc.)
- No dependency on third-party PPA maintainers
- Industry-standard professional approach
- One-time compile cost (5-10 min) vs ongoing version conflicts
- Ubuntu's default Python tracks newest releases; some libraries lag behind

### Why VS Code on Windows (not Linux) for WSL development
- Microsoft's WSL extension lets Windows VS Code edit Linux files seamlessly
- Single VS Code install, switches between Windows and WSL contexts
- Avoids running GUI apps inside WSL
- Better performance

---

## Step 1: Install WSL2 with Ubuntu

**Time:** 15 minutes active + reboot + 5 minutes setup

### Open PowerShell as Administrator
- Press `Win + X`
- Click "Terminal (Admin)" or "Windows PowerShell (Admin)"
- Accept UAC prompt

### Install WSL with default Ubuntu

```powershell
wsl --install
```

This single command:
- Enables Windows Subsystem for Linux feature
- Enables Virtual Machine Platform
- Downloads the WSL2 kernel
- Installs Ubuntu (default Linux distribution)
- Sets WSL2 as default

Wait 2-5 minutes for completion. At the end, it tells you to restart.

### Restart Windows
**Do not skip this.** The install is incomplete until reboot.

### First Ubuntu launch (after reboot)
Ubuntu should launch automatically. If not, find "Ubuntu" in Start menu.

You'll be prompted:
1. **UNIX username:** Use lowercase only, no spaces. Short and memorable. This becomes `<linux-user>`.
2. **UNIX password:** Will be invisible as you type. Type carefully, confirm twice.

After setup, you should see:
```
<linux-user>@<hostname>:~$
```

**Pin Ubuntu to your taskbar** - right-click the running Ubuntu icon → "Pin to taskbar".

### Verify

```bash
lsb_release -a
```
Expected: `Ubuntu 24.04 LTS` or `Ubuntu 26.04 LTS` (or current LTS).

```bash
uname -r
```
Expected: kernel version with "microsoft-standard-WSL2" in it.

```bash
pwd
```
Expected: `/home/<linux-user>`

---

## Step 2: Update Ubuntu + install essential tools

**Time:** 10 minutes

All commands run from any directory (typically your home `~`).

### Update package lists and upgrade installed packages

```bash
sudo apt update && sudo apt upgrade -y
```

You'll be prompted for your Ubuntu password (invisible as you type).

**Note:** If prompted about config files (like "Configuration file `/etc/...` Y/I/N/O/D/Z"), press `N` and Enter to keep the existing version.

Expected time: 3-8 minutes the first time.

### Install essential build tools

```bash
sudo apt install -y build-essential curl wget git unzip ca-certificates
```

What this installs:
- `build-essential` - compilers and tools needed to build software from source (needed for pyenv)
- `curl`, `wget` - downloading tools
- `git` - version control
- `unzip` - archive extraction
- `ca-certificates` - SSL certificates for secure connections

### Configure git with your identity

```bash
git config --global user.name "<real-name>"
git config --global user.email "<github-email>"
git config --global init.defaultBranch main
```

**Important:** The email must be added to your GitHub account at github.com/settings/emails for commits to attribute to your profile.

### Verify

```bash
git --version
git config --global --list
gcc --version
```

Expected: git 2.x, your name/email/main visible, gcc version printed.

---

## Step 3: Install Python 3.11 via pyenv

**Time:** 20-30 minutes (mostly compile time)

### Install pyenv build dependencies

These are libraries Python needs to compile cleanly. Skipping them causes builds to succeed but be missing critical features (SSL, sqlite, compression).

```bash
sudo apt install -y make libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
  libsqlite3-dev libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
  libffi-dev liblzma-dev
```

### Install pyenv

```bash
curl -fsSL https://pyenv.run | bash
```

This installs pyenv into `~/.pyenv/`. Expected: brief output ending with a warning about adding pyenv to load path - we fix this next.

### Add pyenv to shell configuration

```bash
nano ~/.bashrc
```

Scroll to the end of the file (`Ctrl+End` or hold Down arrow). Add these three lines at the bottom:

```bash
# pyenv configuration
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
```

Save and exit nano: `Ctrl+O`, Enter, `Ctrl+X`.

**Note on pasting in WSL terminal:** Right-click in the terminal to paste (Ctrl+V doesn't work in most terminals). Shift+Insert also works.

### Reload shell config

```bash
source ~/.bashrc
```

### Verify pyenv

```bash
pyenv --version
```

Expected: `pyenv 2.x.x`. If "command not found," the bashrc additions didn't take effect - re-check the file.

### Install Python 3.11.9

```bash
pyenv install 3.11.9
```

This compiles Python from source. Takes 5-10 minutes. **The "Installing Python-3.11.9..." line will appear stuck - this is normal.** Wait.

### Set as global default

```bash
pyenv global 3.11.9
```

### Verify Python works

```bash
python --version
which python
python -m pip --version
python -c "import ssl; import sqlite3; import bz2; print('All critical modules OK')"
```

Expected:
- `Python 3.11.9`
- Path under `/home/<linux-user>/.pyenv/shims/python`
- pip 23.x or 24.x
- "All critical modules OK"

---

## Step 4: Install Node.js via nvm

**Time:** 5 minutes

Required because Claude Code is built on Node.js.

### Install nvm

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```

This auto-appends nvm config to your `~/.bashrc` (unlike pyenv, no manual edit needed).

### Reload shell

```bash
source ~/.bashrc
```

### Install Node.js LTS

```bash
nvm install --lts
nvm use --lts
nvm alias default 'lts/*'
```

The first command installs the latest LTS Node. The third sets it as default for new terminals.

### Verify

```bash
node --version
npm --version
which node
```

Expected:
- v20.x or v22.x (current LTS at install time)
- npm 10.x or 11.x
- Path under `~/.nvm/versions/node/...`

---

## Step 5: Install Claude Code

**Time:** 5 minutes

### Install via npm globally

```bash
npm install -g @anthropic-ai/claude-code
```

Expected: 30-90 seconds. Deprecation warnings are noise - ignore. Final message should say "added X packages."

### Verify

```bash
claude --version
which claude
```

Expected: Version number printed, path under nvm-managed Node directory.

### First-time authentication

```bash
claude
```

A URL appears in the terminal. Open it in your Windows browser (WSL can sometimes auto-launch, but copy-paste also works). Log in with your Anthropic account. Browser confirms authentication.

Test inside the Claude Code prompt:

```
What's in my current directory?
```

Claude Code should respond with a listing. Exit with `/exit`.

---

## Step 6: VS Code with WSL Integration

**Time:** 15 minutes

### Install VS Code on Windows (if not already)

Download from https://code.visualstudio.com/. Install with defaults.

### Install the WSL extension

In Windows VS Code:
1. Press `Ctrl+Shift+X` (Extensions panel)
2. Search "WSL"
3. Install **"WSL"** by Microsoft (extension ID: `ms-vscode-remote.remote-wsl`)
4. No restart required

### Launch VS Code from WSL

From your Ubuntu terminal:

```bash
cd ~
code .
```

**First run:** VS Code downloads and installs a small server inside WSL. Takes 30-60 seconds.

VS Code on Windows opens, connected to your Linux environment.

### Verify WSL connection

Look at the **bottom-left corner** of VS Code. Should show:

```
WSL: Ubuntu
```

(or `WSL: Ubuntu-26.04` etc.)

### Install Python tooling extensions inside the WSL context

Important: extensions installed on "Local" don't apply in WSL context. You need to install them "in WSL."

In VS Code Extensions panel (`Ctrl+Shift+X`), the panel splits into:
- **LOCAL - INSTALLED** (Windows-side extensions)
- **WSL: UBUNTU - INSTALLED** (Linux-side extensions)

Search each extension name and click **"Install in WSL: Ubuntu"** (not just "Install"):

| Extension | Publisher | Extension ID |
|-----------|-----------|--------------|
| Python | Microsoft | `ms-python.python` |
| Pylance | Microsoft | `ms-python.vscode-pylance` |
| Jupyter | Microsoft | `ms-toolsai.jupyter` |
| Ruff | Astral Software | `charliermarsh.ruff` |
| GitLens | GitKraken | `eamodio.gitlens` |
| Even Better TOML | tamasfe | `tamasfe.even-better-toml` |
| Error Lens | Alexander | `usernamehw.errorlens` |

Note: Installing Python and Jupyter pulls in dependent extensions automatically (debugpy, jupyter-keymap, jupyter-renderers, etc.) - that's expected.

### Verify extensions installed in WSL

In WSL terminal:

```bash
code --list-extensions
```

Should list all extensions, headed with "Extensions installed on WSL: Ubuntu:"

---

## Step 7: Project structure + venv + Anthropic API

**Time:** 15 minutes

### Create project directory

```bash
cd ~
mkdir -p projects/<project-name>
cd projects/<project-name>
```

Verify:
```bash
pwd
```
Expected: `/home/<linux-user>/projects/<project-name>`

### Create subdirectory structure

Use underscores (not hyphens) for Python package compatibility:

```bash
mkdir -p modules/01_<module_name> \
         modules/02_<module_name> \
         shared/data \
         shared/llm \
         shared/utils \
         notebooks \
         tests \
         docs/architecture \
         docs/product_briefs \
         docs/eval_reports
```

Adjust module names to your project's structure.

### Initialize git

```bash
git init
git status
```

Expected: "On branch main / No commits yet"

### Create virtual environment

```bash
python -m venv .venv
```

Verify it was created:
```bash
ls -la .venv
```

Should show `bin/`, `lib/`, `include/`, `pyvenv.cfg`.

### Activate virtual environment

```bash
source .venv/bin/activate
```

**Your prompt should now show `(.venv)` prefix:**
```
(.venv) <linux-user>@<hostname>:~/projects/<project-name>$
```

Verify:
```bash
which python
python --version
```

Expected:
- Path inside `.venv/bin/python`
- Python 3.11.9

**Reminder:** You must run `source .venv/bin/activate` every time you start work in a new terminal.

### Create requirements.txt

```bash
nano requirements.txt
```

Paste (adjust packages for your project):

```
# Core data
pandas==2.2.3
numpy==2.1.3
scipy==1.14.1

# Visualization
matplotlib==3.9.2
plotly==5.24.1

# Data sources
yfinance==1.3.0

# Notebooks
jupyter==1.1.1
ipykernel==6.29.5

# LLM
anthropic==0.97.0

# Web/API
fastapi==0.115.5
uvicorn==0.32.1
streamlit==1.40.2

# Dev tooling
ruff==0.8.2
pytest==8.3.4
python-dotenv==1.0.1
```

Save and exit (`Ctrl+O`, Enter, `Ctrl+X`).

### Install dependencies

```bash
pip install -r requirements.txt
```

Expected: 3-8 minutes. Watch for `ERROR` lines (warnings are usually fine).

### Verify packages work

```bash
python -c "import pandas; import numpy; import anthropic; print('All packages OK')"
```

### Create .gitignore

```bash
nano .gitignore
```

Paste:

```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/

# Virtual environments
.venv/
venv/
env/

# Environment files (NEVER commit secrets)
.env
.env.local

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Project-specific
data/raw/
data/cache/
*.log
logs/

# Test artifacts
.pytest_cache/
.coverage
htmlcov/
```

### Create .env.example (template, goes into git)

```bash
nano .env.example
```

```
# Anthropic API
ANTHROPIC_API_KEY=

# Add other API keys as needed
```

### Create real .env (gitignored, never committed)

```bash
nano .env
```

```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Verify .env is properly ignored

```bash
git status
git check-ignore -v .env
```

- `git status` should NOT show `.env` in untracked files
- `git check-ignore -v .env` should output something like: `.gitignore:15:.env	.env`

If `.env` appears in `git status` output, stop and fix `.gitignore` before proceeding.

### Test Anthropic API works

Create test script:

```bash
nano test_api.py
```

```python
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Reply with exactly: 'WSL Python API works'"}]
)
print(msg.content[0].text)
```

**Note on model names:** Anthropic's model naming evolves. If the model name above fails with "model not found," check console.anthropic.com → Models for current identifier and update.

Run:

```bash
python test_api.py
```

Expected: API responds with the requested phrase.

Delete the test:

```bash
rm test_api.py
```

### How the API key flow works (reference)

```
.env file → load_dotenv() reads it → ANTHROPIC_API_KEY in os.environ → 
Anthropic() SDK reads it implicitly → never appears in source code
```

This is the standard secure pattern - works locally with .env, works in production with cloud secrets, no code changes needed.

### Create initial README.md

```bash
nano README.md
```

Customize for your project:

```markdown
# <project-name>

Brief description of what this project does.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then add your API key
```

## Tech Stack

- Python 3.11 (managed via pyenv)
- Anthropic API
- [other libraries]
```

### First commit

```bash
git add .
git status
```

Verify staged files. Should NOT include `.env` or `.venv/`. If they appear, stop and fix `.gitignore`.

```bash
git commit -m "Initial project structure"
git log
```

---

## Step 8: GitHub setup with SSH

**Time:** 10 minutes

### Generate SSH key

Check for existing keys:

```bash
ls -la ~/.ssh/
```

If no `id_ed25519` file exists, generate one:

```bash
ssh-keygen -t ed25519 -C "<github-email>"
```

When prompted:
1. **File location:** Press Enter for default
2. **Passphrase:** Optional. Empty is simpler.
3. **Confirm passphrase:** Same as above

### Start SSH agent and add key

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### Get public key

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the entire output (starts with `ssh-ed25519` and ends with your email).

### Add to GitHub

In browser:
1. Go to https://github.com/settings/keys
2. Click "New SSH key"
3. Title: descriptive name like "WSL Ubuntu - <hostname>"
4. Key type: Authentication Key (default)
5. Key: paste public key
6. Click "Add SSH key"

### Test SSH connection

```bash
ssh -T git@github.com
```

First time: type `yes` when prompted about authenticity.

Expected:
```
Hi <github-username>! You've successfully authenticated, but GitHub does not provide shell access.
```

### Create GitHub repository

In browser:
1. Go to https://github.com/new
2. Repository name: matches your local folder name
3. Description: project description
4. Visibility: Private (recommended initially)
5. **Do NOT** check "Add a README/.gitignore/license" (you have them locally)
6. Click "Create repository"

### Link local repo to GitHub

```bash
git remote add origin git@github.com:<github-username>/<project-name>.git
git remote -v
```

### Push to GitHub

```bash
git push -u origin main
```

The `-u` sets up tracking - future pushes can just be `git push`.

### Verify on GitHub

Open `https://github.com/<github-username>/<project-name>` in browser. Should show your files and one commit.

### Preserve empty directories (optional)

Git doesn't track empty directories. To preserve structure:

```bash
touch modules/01_<module_name>/.gitkeep \
      modules/02_<module_name>/.gitkeep \
      shared/data/.gitkeep \
      shared/llm/.gitkeep \
      shared/utils/.gitkeep \
      notebooks/.gitkeep \
      tests/.gitkeep \
      docs/architecture/.gitkeep \
      docs/product_briefs/.gitkeep \
      docs/eval_reports/.gitkeep
```

Commit and push:

```bash
git add .
git commit -m "Add .gitkeep files to preserve directory structure"
git push
```

---

## Step 9: Final verification

**Time:** 10 minutes

### Open VS Code from project

```bash
cd ~/projects/<project-name>
source .venv/bin/activate
code .
```

### Verify interpreter

In bottom-left of VS Code, look for:
- "WSL: Ubuntu" - confirms WSL connection
- Python interpreter showing 3.11.9 from `.venv`

If interpreter isn't auto-selected:
- `Ctrl+Shift+P`
- Type "Python: Select Interpreter"
- Pick the one with path `./.venv/bin/python` (marked "Recommended")

### Verify integrated terminal activates venv

Press `` Ctrl+` `` to open integrated terminal. Should show `(.venv)` prefix automatically.

If not, run `source .venv/bin/activate` manually. Not a critical issue.

### Final commit

If you have a CONTEXT.md or similar tracking document, update it with completion of setup. Commit and push.

---

## What you've accomplished

After all 9 steps:

- Real Linux dev environment on Windows
- Python 3.11 managed by pyenv (project-isolated)
- Node + Claude Code working
- VS Code editing WSL files seamlessly
- Project structure with venv, .env, .gitignore
- Anthropic API verified
- Initial commit pushed to GitHub
- Foundation that scales for years of development

---

## Common stumbles and fixes

| Stumble | Cause | Fix |
|---------|-------|-----|
| `wsl --install` fails | Virtualization disabled in BIOS | Enable VT-x/AMD-V in BIOS settings |
| pyenv install fails | Missing build dependency | Re-run the apt install command in Step 3 |
| Python compile takes forever | Normal | Be patient, 5-10 min is expected |
| `code .` doesn't open VS Code | WSL extension missing | Install Microsoft WSL extension on Windows VS Code |
| Extensions don't show in WSL context | Installed on Local | Re-install with "Install in WSL: Ubuntu" button |
| `claude` works in WSL but not VS Code terminal | nvm path not loaded | Restart VS Code or run `source ~/.bashrc` |
| Git push fails: "Permission denied (publickey)" | SSH key not added to GitHub | Re-run ssh-keygen + add to GitHub steps |
| `.env` shows in `git status` | .gitignore incorrect | Check .gitignore syntax, no leading slash on `.env` |
| API model not found | Model name changed | Check console.anthropic.com for current model identifier |

---

## Daily workflow after setup

When returning to work:

```bash
# Open Ubuntu terminal or VS Code integrated terminal
cd ~/projects/<project-name>
source .venv/bin/activate
code .  # if not already open
```

Make changes, then:

```bash
git add .
git commit -m "Descriptive message"
git push
```

---

## Stack versions installed (reference)

For reproducibility. Current latest versions are usually fine.

| Component | Version |
|-----------|---------|
| Ubuntu | 26.04 LTS |
| Python | 3.11.9 (via pyenv) |
| Node | v24.16.0 (via nvm) |
| Claude Code | 2.1.150 |
| anthropic SDK | 0.97.0 |
| pandas | 2.2.3 |
| numpy | 2.1.3 |
| scipy | 1.14.1 |
| yfinance | 1.3.0 |
| jupyter | 1.1.1 |
| fastapi | 0.115.5 |
| streamlit | 1.40.2 |
| ruff | 0.8.2 |
| pytest | 8.3.4 |

---

## File location for this guide

Save this file in your project repo at root level alongside README.md and CONTEXT.md:

```
<project-name>/
├── README.md
├── CONTEXT.md
├── curriculum.md
├── environment_setup.md  ← this file
└── ...
```
