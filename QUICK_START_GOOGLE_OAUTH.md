# 🚀 Quick Start: Google OAuth Setup

## What's Been Done ✅

1. ✅ Installed `django-allauth` package
2. ✅ Configured settings.py for Google OAuth
3. ✅ Created custom adapter for student role assignment
4. ✅ Updated login/register pages with Google buttons
5. ✅ Added required middleware and URLs
6. ✅ Ran database migrations

## What You Need To Do 📝

### Step 1: Get Google Credentials (5 minutes)

1. Visit: https://console.cloud.google.com/
2. Create/select project
3. Enable "Google+ API" (APIs & Services > Library)
4. Create OAuth 2.0 credentials (APIs & Services > Credentials)
5. Add redirect URIs:
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
6. Copy Client ID and Client Secret

### Step 2: Update .env File

Add to your `.env` file:

```env
GOOGLE_CLIENT_ID=paste_your_client_id_here
GOOGLE_CLIENT_SECRET=paste_your_client_secret_here
```

### Step 3: Configure Django Site

Run:
```bash
python manage.py shell
```

Then paste:
```python
from django.contrib.sites.models import Site
site = Site.objects.get_current()
site.domain = 'localhost:8000'
site.name = 'BrightTrack LMS'
site.save()
print("✅ Site configured!")
exit()
```

Or use the setup script:
```bash
python manage.py shell < setup_google_oauth.py
```

### Step 4: Test It!

```bash
python manage.py runserver
```

Visit: http://localhost:8000/login/

You should see:
- Traditional login form
- "Or continue with" divider
- "Sign in with Google" button

## How Students Use It

### Option 1: Google Sign-In
1. Click "Sign in with Google"
2. Choose Gmail account
3. Complete profile (Year Level, Section, etc.)
4. Auto-enrolled in classes
5. Redirected to dashboard

### Option 2: Traditional Registration
1. Click "Register here"
2. Fill form (Name, Email, Password, Year Level, Gender)
3. Complete profile (Section, Student Number, etc.)
4. Auto-enrolled in classes
5. Redirected to dashboard

## Both Options Lead To:
- ✅ Student account created
- ✅ Profile completion required
- ✅ Section + Year Level based auto-enrollment
- ✅ Access to student dashboard

## Troubleshooting

**Google button not working?**
- Check .env has correct credentials
- Restart Django server
- Clear browser cache

**Redirect URI mismatch?**
- Verify URIs in Google Console match exactly
- Include both localhost and 127.0.0.1

**Site not found error?**
- Run Step 3 again to configure Django site

## Files Created/Modified

**New Files:**
- `accounts/adapters.py` - Custom social account adapter
- `GOOGLE_OAUTH_SETUP.md` - Detailed setup guide
- `setup_google_oauth.py` - Quick setup script
- `QUICK_START_GOOGLE_OAUTH.md` - This file

**Modified Files:**
- `campus_care/settings.py` - Added allauth config
- `campus_care/urls.py` - Added allauth URLs
- `accounts/urls.py` - Added Google login URL
- `templates/accounts/login.html` - Added Google button
- `templates/accounts/register.html` - Added Google button

## Need Help?

See detailed guide: `GOOGLE_OAUTH_SETUP.md`

## Summary

✅ Google OAuth fully integrated
✅ Traditional registration still works
✅ Both options require profile completion
✅ Auto-enrollment based on section + year level
✅ Modern UI with Google branding
✅ Secure authentication flow

**Ready to test!** 🎉
