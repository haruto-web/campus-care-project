# BT AI Assistant Chatbot - Implementation Guide

## Overview
BT (BrightTrack) AI Assistant is an intelligent chatbot integrated into the Campus Care system to help counselors and admins with their daily tasks using AI-powered insights.

## Features

### Counselor Chatbot (`/ai/counselor/`)
**Greeting:** "Hi! I'm BT, your AI assistant. I'm here to help you with student interventions, reports, and counseling insights."

#### Quick Actions:
1. **Create Intervention for Student**
   - Input: Student ID
   - Output: AI-generated intervention recommendations based on student profile
   - Uses: Student risk assessment, grades, attendance, wellness data

2. **Generate Report Summary**
   - Input: None (automatic)
   - Output: Professional summary of:
     - High-risk student count
     - Medium-risk student count
     - Unresolved alerts
     - Pending interventions

3. **Search Student**
   - Input: Natural language query (e.g., "grade 7 section apple high")
   - Filters:
     - Grade level (7-10)
     - Section
     - Severity (low/medium/high/critical)
   - Output: List of matching students with ID, name, grade, section

4. **Ask AI**
   - Input: Any question about counseling, student support, interventions
   - Output: AI-generated response using Gemini API

---

### Admin Chatbot (`/ai/admin/`)
**Greeting:** "Hi! I'm BT, your AI assistant admin. I'm here to help you with system reports, analytics, and administrative insights."

#### Quick Actions:
1. **Generate System Report**
   - Input: None (automatic)
   - Output: Executive summary of:
     - Total students
     - Total teachers
     - Total counselors
     - High-risk students

2. **Ask AI**
   - Input: Any question about system administration, analytics, management
   - Output: AI-generated response using Gemini API

---

## Technical Implementation

### Backend (ai_assistant/views.py)
- `counselor_chat_view()` - Renders counselor chatbox page
- `admin_chat_view()` - Renders admin chatbox page
- `counselor_chat()` - API endpoint for counselor actions (POST)
- `admin_chat()` - API endpoint for admin actions (POST)

### Frontend Templates
- `templates/ai_assistant/counselor_chat.html` - Counselor chatbox UI
- `templates/ai_assistant/admin_chat.html` - Admin chatbox UI

### URLs
- `/ai/counselor/` - Counselor chatbox page
- `/ai/admin/` - Admin chatbox page
- `/ai/counselor/chat/` - Counselor API endpoint
- `/ai/admin/chat/` - Admin API endpoint

### Navigation
- **Counselor:** Added "BT AI Assistant" link in counselor sidebar
- **Admin:** Added "BT AI Assistant" button in admin dashboard header

---

## API Request Format

### Counselor Chat API
```json
POST /ai/counselor/chat/
{
  "action": "create_intervention|generate_report|search_student|ask_ai",
  "student_id": 123,  // for create_intervention
  "filters": {        // for search_student
    "year_level": "7",
    "section": "apple",
    "severity": "high"
  },
  "message": "Your question here"  // for ask_ai
}
```

### Admin Chat API
```json
POST /ai/admin/chat/
{
  "action": "generate_report|ask_ai",
  "message": "Your question here"  // for ask_ai
}
```

---

## UI Design

### Chat Interface
- **Avatar:** Circular gradient badge with "BT" initials
- **User Messages:** Purple background, right-aligned
- **AI Messages:** White background, left-aligned with avatar
- **Quick Actions:** Colored buttons (blue, green, purple, indigo)
- **Input Area:** Hidden by default, shows when action selected

### Color Scheme
- **Counselor:** Purple/Indigo gradient
- **Admin:** Blue/Cyan gradient

---

## Dependencies
- Gemini API (ml_models.gemini_client)
- Django JsonResponse
- CSRF protection
- User authentication

---

## Usage Flow

### Counselor Example:
1. Click "Create Intervention"
2. Enter student ID (e.g., "5")
3. AI analyzes student profile
4. Returns intervention recommendations

### Admin Example:
1. Click "Generate System Report"
2. AI generates executive summary
3. Displays system statistics and insights

---

## Future Enhancements
- Voice input support
- Chat history persistence
- Export chat transcripts
- Multi-language support
- Sentiment analysis of conversations
- Proactive AI suggestions
- Integration with calendar for scheduling
- File upload support for document analysis
