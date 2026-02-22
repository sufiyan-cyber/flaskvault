# FlaskVault — Deployment Guide (Render)

This guide walks you through deploying FlaskVault to **Render** from scratch.
No prior deployment experience required.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Push to GitHub](#2-push-to-github)
3. [Create a Render Account](#3-create-a-render-account)
4. [Create a PostgreSQL Database](#4-create-a-postgresql-database)
5. [Create a Web Service](#5-create-a-web-service)
6. [Set Environment Variables](#6-set-environment-variables)
7. [Initialise the Database](#7-initialise-the-database)
8. [Persistent File Uploads (Render Disk)](#8-persistent-file-uploads-render-disk)
9. [Access Your Site](#9-access-your-site)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| **Git** | Version control | [git-scm.com](https://git-scm.com/) |
| **GitHub account** | Hosts your repository | [github.com](https://github.com/) |
| **Render account** | Cloud hosting (free tier) | [render.com](https://render.com/) |
| **Python 3.10+** | Local development | [python.org](https://python.org/) |

---

## 2. Push to GitHub

Open a terminal in the project folder (`Authentication/`) and run:

```bash
git init
git add .
git commit -m "Initial commit — FlaskVault"
```

Then create a **new repository** on GitHub (do NOT add a README):

```bash
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git branch -M main
git push -u origin main
```

> **Tip:** Make sure your `.gitignore` is committed so `instance/`, `uploads/`, `.env`, and `.venv/` are excluded.

---

## 3. Create a Render Account

1. Go to [render.com](https://render.com/) and click **Get Started for Free**.
2. Sign up with GitHub (recommended — it makes connecting repos easier).
3. Verify your email if prompted.

---

## 4. Create a PostgreSQL Database

1. In the Render dashboard, click **New → PostgreSQL**.
2. Fill in:
   - **Name:** `flaskvault-db` (or anything you like)
   - **Region:** choose the one closest to your users
   - **Plan:** **Free** (sufficient for learning)
3. Click **Create Database**.
4. After creation, open the database page and find the **Internal Database URL**
   (starts with `postgresql://`). **Copy it** — you'll need it in the next step.

> ⚠️ The free PostgreSQL database expires after 90 days. Render will warn you before deletion.

---

## 5. Create a Web Service

1. In the Render dashboard, click **New → Web Service**.
2. Connect your GitHub repository (`YOUR-REPO`).
3. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `flaskvault` |
| **Region** | Same as your database |
| **Branch** | `main` |
| **Runtime** | `Python` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn wsgi:app` |
| **Plan** | **Free** |

4. Click **Create Web Service** (don't deploy yet — set env vars first).

---

## 6. Set Environment Variables

In your Render **Web Service → Environment**, add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | A long random string | Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | The **Internal Database URL** you copied in Step 4 | Starts with `postgresql://...` |
| `PYTHON_VERSION` | `3.11.6` | (Optional) Pins the Python version on Render |

Click **Save Changes**. Render will now redeploy with the new variables.

---

## 7. Initialise the Database

After the first deploy succeeds, you need to create the tables.

### Option A — Render Shell (easiest)

1. Go to your **Web Service → Shell** tab.
2. Run:

```bash
flask init-db
```

You should see: `✅ Database tables created.`

### Option B — One-off Job

1. In the Render dashboard, click **New → Job**.
2. Use the same repo and environment.
3. Set the command to:

```bash
flask init-db
```

4. Run the job once.

### Option C — Build Command (auto-create on every deploy)

Change your **Build Command** to:

```bash
pip install -r requirements.txt && flask init-db
```

> This runs `flask init-db` on every deploy. Since `CREATE TABLE IF NOT EXISTS` is used
> internally by SQLAlchemy, it's safe to run repeatedly.

---

## 8. Persistent File Uploads (Render Disk)

By default, the free tier's filesystem is **ephemeral** — files disappear on redeploy.

To persist uploads:

1. Go to your Web Service → **Disks** tab.
2. Click **Add Disk**:
   - **Name:** `uploads`
   - **Mount Path:** `/opt/render/project/src/uploads`
   - **Size:** `1 GB` (adjust as needed — requires paid plan)
3. Update your **environment variable** (optional):
   - `UPLOAD_FOLDER` = `/opt/render/project/src/uploads`

> 💡 On the free plan without a disk, uploaded files survive until the next deploy.
> For a student project or demo this is usually fine.

---

## 9. Access Your Site

After deployment finishes, Render gives you a URL like:

```
https://flaskvault.onrender.com
```

1. Open the URL in your browser.
2. Register a new account.
3. Log in, upload files, download them — everything should work!

> **Note:** On the free tier, the service spins down after ~15 minutes of inactivity.
> The first request after idle takes ~30-60 seconds to wake up.

---

## 10. Troubleshooting

### "Application Error" on Render

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError` | Missing package in `requirements.txt`. Add it and redeploy. |
| `sqlalchemy.exc.OperationalError` | `DATABASE_URL` not set or incorrect. Check Environment tab. |
| `KeyError: 'SECRET_KEY'` | You forgot to set `SECRET_KEY` in Render's Environment. |

**Check logs:** Go to your Web Service → **Logs** tab to see error details.

### Common local development issues

| Symptom | Fix |
|---------|-----|
| `ImportError: cannot import name 'create_app'` | Make sure you're running from the project root, not inside `app/`. |
| `OperationalError: no such table` | Run `python wsgi.py` once (it auto-creates tables), or run `flask init-db`. |
| Port 5000 in use | Another process is using it. Kill it or set `app.run(port=5001)`. |

### Database not working

```bash
# Verify your DATABASE_URL is set:
echo $DATABASE_URL        # Linux/Mac
echo %DATABASE_URL%       # Windows CMD
$env:DATABASE_URL         # Windows PowerShell

# If empty, the app falls back to SQLite (which is fine for local dev)
```

### CSS / styles not loading

- Clear your browser cache (Ctrl+Shift+R).
- Make sure the `static/css/styles.css` file exists.

### File upload fails

- Check the file extension is in the allowed list (pdf, png, jpg, etc.).
- Check the file size is under 16 MB.
- Make sure the `uploads/` directory exists (it's created automatically).

---

## Quick Reference

```bash
# ── Local development ──────────────────────────────────────
pip install -r requirements.txt
python wsgi.py                    # starts on http://127.0.0.1:5000

# ── Create tables manually ─────────────────────────────────
flask init-db

# ── Production (Render) ────────────────────────────────────
# Build command:
pip install -r requirements.txt

# Start command:
gunicorn wsgi:app
```
