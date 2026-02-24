# AI Features - What They Actually Do

## 🤖 AI Does NOT Automatically Create Interventions

**IMPORTANT**: AI only provides **recommendations** and **analysis**. Counselors must manually create interventions.

---

## ✅ What AI Actually Does

### 1. **Sentiment Analysis** (Wellness Check-in)

**When**: Student submits wellness check-in with text comments

**What happens**:
- AI analyzes the text for emotional distress
- Determines sentiment: positive/neutral/negative
- Assigns alert level: none/low/medium/high/critical
- Identifies concerning phrases

**Example - John Doe**:
```
Comments: "im tired, to many workloads"
AI Analysis:
  - Sentiment: negative
  - Alert Level: medium
  - Confidence: 90%
  - Concerning Phrases: ["im tired", "to many workloads"]
```

**Result**: 
- ❌ NO automatic intervention created
- ✅ Alert created ONLY if alert level is "high" or "critical"
- John Doe's alert level was "medium" → NO alert created by AI

---

### 2. **Risk Prediction** (Daily Command)

**When**: Admin runs `python manage.py predict_risks`

**What happens**:
- AI analyzes each student's data (GPA, attendance, missing assignments, stress)
- Predicts risk level: low/medium/high
- Provides risk factors and recommendations
- Saves to database

**Where to see it**:
- Student profile page → "AI Risk Analysis" section (purple card)

**Result**:
- ❌ NO automatic intervention created
- ✅ Shows AI predictions on profile page

---

### 3. **Intervention Recommendations** (On-demand)

**When**: Counselor creates intervention for medium/high-risk student

**What happens**:
- AI suggests top 2 intervention types
- Provides success probability for each
- Explains reasoning

**Where to see it**:
- Create Intervention page → Purple "AI-Recommended Interventions" card at top

**Example**:
```
Recommended Interventions:
1. Academic Tutoring (75% success rate)
   Reasoning: Student shows low GPA and high stress related to workload
   
2. Counseling Session (65% success rate)
   Reasoning: Negative sentiment detected in wellness check-in
```

**Result**:
- ❌ NO automatic intervention created
- ✅ Counselor sees recommendations and manually creates intervention

---

## 📊 John Doe's Current Status

### Wellness Check-in:
- Stress: 5/5 (Very High)
- Motivation: 1/5 (Very Low)
- Comments: "im tired, to many workloads"

### AI Sentiment Analysis:
- Sentiment: **negative**
- Alert Level: **medium** (not high enough for automatic alert)
- Concerning Phrases: "im tired", "to many workloads"

### Risk Assessment:
- Risk Level: **HIGH**
- Risk Score: 80

### Alerts:
- Total: 2 alerts
- Types: wellness_concern (from stress 5/5, motivation 1/5)
- **NO emotional_distress alert** (because AI alert level was "medium", not "high")

---

## 🎯 How to Trigger AI Alert Creation

For AI to automatically create an **emotional_distress alert**, the student needs to write comments with more severe language:

### Examples that would trigger HIGH alert:
- "I feel hopeless and don't want to continue"
- "I'm having thoughts of hurting myself"
- "I can't take this anymore, everything is falling apart"
- "I want to give up on everything"
- "Nobody cares about me, I'm worthless"

### John Doe's comment was NOT severe enough:
- "im tired, to many workloads" → **medium** alert level
- This is negative but not critical distress

---

## 📍 Where to See AI Features

### For Counselors:

1. **Student Profile** (`/student/<id>/`)
   - Scroll down to "AI Risk Analysis" section (purple card)
   - See risk prediction, factors, recommendations

2. **Create Intervention** (`/wellness/intervention/create/<student_id>/`)
   - See "AI-Recommended Interventions" at top (purple card)
   - Shows suggested intervention types with success rates

3. **Alerts Page** (`/wellness/alerts/`)
   - See alerts including emotional_distress alerts (if AI detected high distress)

### For Admins:

1. **Run Risk Predictions**:
   ```bash
   python manage.py predict_risks
   ```
   - Analyzes all students
   - Updates risk predictions

2. **Analyze Existing Check-ins**:
   ```bash
   python manage.py analyze_existing_checkins
   ```
   - Retroactively analyzes wellness check-ins

---

## 🔧 Summary

| AI Feature | Creates Intervention? | Creates Alert? | Where to See |
|------------|----------------------|----------------|--------------|
| Sentiment Analysis | ❌ NO | ✅ YES (if high/critical) | Alerts page |
| Risk Prediction | ❌ NO | ❌ NO | Student profile |
| Intervention Recommendations | ❌ NO | ❌ NO | Create intervention form |

**Key Point**: AI provides **insights and recommendations**. Counselors make the final decisions and manually create interventions.
