# Live Server 500 Error Analysis

## Two Render Deployments

| Property | `bright-track-project` | `campus-care-project-y74p` |
|----------|----------------------|--------------------------|
| **URL** | https://bright-track-project.onrender.com | https://campus-care-project-y74p.onrender.com |
| **Source Repo** | `haruto-web/campus-care-project` | `haruto-web/campus-care-project` |
| **Landing page** | ✅ Works | ✅ Works |
| **Login `/login/`** | ✅ Works | ❌ 500 Error |
| **Student `/student/verify/`** | ✅ Works | ❌ 500 Error |

## Root Cause

Both services deploy the **exact same code** from the same GitHub repo. The landing page (`landing.html`) works on both because it is a **standalone template** — it does NOT extend `base.html` and does NOT use `{% load static %}`.

However, `/login/` and `/student/verify/` **extend `base.html`**, which:
1. Uses `{% load static %}` and references `{% static 'css/design-system.css' %}`
2. Triggers WhiteNoise's `CompressedManifestStaticFilesStorage` to look up static file hashes

Since the code is identical, the 500 on `campus-care-project-y74p` is caused by a **difference in environment configuration** between the two Render services. The most likely causes:

### 1. Missing or incomplete environment variables
The `campus-care-project-y74p` service may be missing one or more of these required env vars:

| Variable | Required For |
|----------|-------------|
| `DATABASE_URL` | Database connection (PostgreSQL) |
| `SECRET_KEY` | Django security — will crash if not set and default is invalid |
| `ALLOWED_HOSTS` | If set incorrectly, causes `DisallowedHost` (400, not 500) |

### 2. Database not connected or migrations not run
If `DATABASE_URL` points to a different (or non-existent) database, Django may crash when the `messaging.context_processors.unread_messages_count` context processor tries to query the `messaging_message` table on every page load (including login pages, because `base.html` includes `{% if user.is_authenticated %}` checks but the context processor still runs).

### 3. `collectstatic` failed during build
WhiteNoise's `CompressedManifestStaticFilesStorage` throws a `ValueError` if a static file referenced in templates (like `css/design-system.css`) is not in the manifest. If `python manage.py collectstatic` failed during the build on that service, every page that uses `{% static %}` would 500.

## How to Diagnose (1 minute)

Go to your **Render Dashboard** → `campus-care-project-y74p` service → **Logs** tab.

Look for a Python traceback. It will tell you exactly which error is occurring. Common patterns:

| Traceback Contains | Meaning | Fix |
|---|---|---|
| `ValueError: Missing staticfiles manifest` | `collectstatic` failed | Redeploy or check build logs |
| `OperationalError: could not connect to server` | No `DATABASE_URL` set | Add the env var in Render settings |
| `relation "messaging_conversation" does not exist` | Migrations not run | Run `python manage.py migrate` via shell |
| `DisallowedHost` | `ALLOWED_HOSTS` wrong | Add the hostname to `ALLOWED_HOSTS` env var |

## Quick Fix Options

### Option A: Fix `campus-care-project-y74p` environment
1. Go to Render Dashboard → `campus-care-project-y74p` → **Environment**
2. Ensure all env vars match `bright-track-project` (especially `DATABASE_URL`, `SECRET_KEY`)
3. Trigger a **Manual Deploy** to re-run `build.sh` (which runs `collectstatic` and `migrate`)

### Option B: Delete the broken service (recommended if not needed)
If `bright-track-project` is your primary server and `campus-care-project-y74p` is just a duplicate:
1. Go to Render Dashboard → `campus-care-project-y74p` → **Settings** → **Delete Service**
2. This has zero impact on `bright-track-project`

### Option C: Share the same database
If you want both running, ensure both services have the **exact same `DATABASE_URL`** pointing to the same PostgreSQL instance. Then trigger a manual deploy on `campus-care-project-y74p`.
