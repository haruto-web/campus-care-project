# BT AI Chatbot - Setup Instructions

## ✅ Installation Complete!

The BT AI Assistant chatbot has been successfully installed.

## 🔄 IMPORTANT: Restart Django Server

**You MUST restart your Django development server for the changes to take effect:**

```bash
# Stop the current server (Ctrl+C)
# Then restart:
python manage.py runserver
```

## 📍 Access URLs

### For Counselors:
- Navigate to: **http://localhost:8000/ai/counselor/**
- Or click "BT AI Assistant" in the counselor sidebar

### For Admins:
- Navigate to: **http://localhost:8000/ai/admin/**
- Or click "BT AI Assistant" button in admin dashboard

## 🧪 Quick Test

After restarting the server, test the URLs:

1. Login as counselor
2. Look for "BT AI Assistant" link in the left sidebar (with robot icon)
3. Click it to open the chatbox

OR

1. Login as admin
2. Look for "BT AI Assistant" button in the dashboard header
3. Click it to open the chatbox

## ❗ Troubleshooting

If you still don't see the links:

1. **Clear browser cache** (Ctrl+Shift+R or Ctrl+F5)
2. **Check you're logged in** as counselor or admin
3. **Verify server is running** without errors
4. **Check console** for any JavaScript errors (F12)

## 📝 Features Available

### Counselor Chatbot:
- ✅ Create Intervention (enter student ID)
- ✅ Generate Report Summary
- ✅ Search Student (by grade, section, severity)
- ✅ Ask AI (general questions)

### Admin Chatbot:
- ✅ Generate System Report
- ✅ Ask AI (general questions)

## 🎨 UI Elements

- Purple/Indigo gradient for counselor
- Blue/Cyan gradient for admin
- Chat bubbles with BT avatar
- Quick action buttons
- Real-time responses

---

**Need help?** Make sure:
1. Server is restarted ✓
2. You're logged in as counselor/admin ✓
3. Browser cache is cleared ✓
