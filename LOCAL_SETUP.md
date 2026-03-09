# BrightTrack — Local Setup Guide for Classmates

---

## Requirements

Install these before starting:

| Tool | Download |
|------|----------|
| Python 3.12 | https://www.python.org/downloads/release/python-3120/ |
| PostgreSQL | https://www.postgresql.org/download/ |
| Git | https://git-scm.com/downloads |

> During Python install, check **"Add Python to PATH"**

---

## Step 1 — Clone the Project

```bash
git clone <repo-url>
cd campus-care-project
```

---

## Step 2 — Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4 — Create the Database

Open **pgAdmin** or **psql** and run:

```sql
CREATE DATABASE campus_care_db;
```

> Default PostgreSQL user is `postgres`. Remember the password you set during PostgreSQL installation.

---

## Step 5 — Create the `.env` File

Create a file named `.env` in the project root (same folder as `manage.py`) with this content:

```
DEBUG=True
SECRET_KEY=any-random-string-here

# Database
DB_NAME=campus_care_db
DB_USER=postgres
DB_PASSWORD=your-postgres-password-here
DB_HOST=localhost
DB_PORT=5432

# Email OTP (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password

# Leave these blank for local dev
BREVO_API_KEY=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
GEMINI_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### How to get a Gmail App Password
1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Search for **"App Passwords"**
4. Create one → select **Mail** → copy the 16-character password
5. Paste it as `EMAIL_HOST_PASSWORD`

> If you don't want to set up email, change `EMAIL_BACKEND` to:
> `django.core.mail.backends.console.EmailBackend`
> OTP codes will print in the terminal instead of being sent to email.

---

## Step 6 — Run Migrations

```bash
python manage.py migrate
```

---

## Step 7 — Create an Admin Account

```bash
python manage.py createsuperuser
```

Fill in username, email, and password when prompted.

Then set the role to admin by running:

```bash
python manage.py shell
```

```python
from accounts.models import User
u = User.objects.get(username='your-username-here')
u.role = 'admin'
u.profile_completed = True
u.is_staff = True
u.is_superuser = True
u.save()
exit()
```

---

## Step 8 — Run the Server

```bash
python manage.py runserver
```

Open your browser and go to: **http://127.0.0.1:8000**

---

## Common Issues

**`ModuleNotFoundError`** — Make sure your virtual environment is activated before running any command.

**`password authentication failed for user "postgres"`** — Wrong `DB_PASSWORD` in `.env`. Use the password you set when installing PostgreSQL.

**`database "campus_care_db" does not exist`** — You skipped Step 4. Create the database first.

**`Failed to send verification code`** — Your email/app password is wrong, or you haven't set up 2FA on your Google account. Use the console backend instead (see Step 5 note).

**Static files not loading** — Run `python manage.py collectstatic` then restart the server.

---

## Notes

- Google OAuth (Sign in with Google) will **not work** locally unless you configure your own Google OAuth credentials. You can ignore it and use the normal login/OTP flow.
- AI features (Gemini) will be disabled if `GEMINI_API_KEY` is blank — the rest of the app works fine.
- File uploads will save locally to the `media/` folder (Cloudinary is only used in production).
