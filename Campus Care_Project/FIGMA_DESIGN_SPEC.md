# Campus Care - Figma Design Specification

## Design System

### Colors
```
Primary Blue: #0D6EFD
Success Green: #198754
Warning Yellow: #FFC107
Danger Red: #DC3545
Info Cyan: #0DCAF0

Background: #F8F9FA
White: #FFFFFF
Text Dark: #212529
Text Muted: #6C757D
Border: #DEE2E6
```

### Typography
```
Font Family: System UI, -apple-system, "Segoe UI", Roboto
Headings: Bold, 24-32px
Body: Regular, 16px
Small Text: 14px
Labels: 14px, Medium weight
```

### Spacing
```
xs: 4px
sm: 8px
md: 16px
lg: 24px
xl: 32px
xxl: 48px
```

---

## Screens to Design in Figma

### 1. LOGIN SCREEN (1920x1080)
**Layout:**
- Centered card (500px width)
- Logo icon at top (heart-pulse, 48px)
- Title "Campus Care" (32px, bold)
- Subtitle "Student Support Monitoring System" (14px, muted)
- Username input field
- Password input field
- Login button (full width, primary blue)
- "Register here" link at bottom
- Test accounts card below

**Components:**
- Input fields: 48px height, rounded corners (8px)
- Button: 48px height, rounded (8px), primary blue
- Card: White background, shadow, 32px padding

---

### 2. REGISTRATION SCREEN (1920x1080)
**Layout:**
- Centered card (600px width)
- Person-plus icon at top (48px)
- Title "Create Account"
- Role dropdown (Student/Teacher/Counselor)
- First Name & Last Name (2 columns)
- Email input
- Username input
- Phone input (optional)
- Password input
- Confirm Password input
- Register button (full width)
- "Login here" link

---

### 3. STUDENT DASHBOARD (1920x1080)
**Layout:**
- Top Navigation Bar (60px height, primary blue)
  - Logo + "Campus Care" (left)
  - Menu items: Dashboard, My Classes, Assignments
  - User profile dropdown (right)

- Main Content (2 columns: 8-4 grid)
  
**Left Column (66%):**
- Welcome heading "Welcome, [Student Name]!"
- My Classes Card
  - Header: "My Classes" with book icon
  - List of classes (CS101, CS201)
  - Each class shows: code, name, teacher, semester badge
- Upcoming Assignments Card
  - Header: "Upcoming Assignments" with clipboard icon
  - List of assignments with due dates and points

**Right Column (33%):**
- Wellness Check-in Card (green header)
  - "How are you feeling today?"
  - "Take Check-in Survey" button
  - Last check-in date
- My Stats Card
  - Attendance Rate with progress bar
  - Current GPA
  - Missing Assignments count

---

### 4. TEACHER DASHBOARD (1920x1080)
**Layout:**
- Same navigation as student

**Left Column:**
- My Classes Card
  - List of classes taught
  - Student count per class
- Students Needing Attention Card (warning yellow header)
  - List of at-risk students
  - Risk level badges

**Right Column:**
- Quick Actions Card (green header)
  - "Create Assignment" button
  - "Mark Attendance" button
  - "Report Concern" button
- Overview Card
  - Total Students count
  - Pending Grades count
  - At-Risk Students count

---

### 5. COUNSELOR DASHBOARD (1920x1080)
**Layout:**
- Same navigation

**Top Row (4 stat cards):**
- High Risk Students (red card, large number)
- Medium Risk Students (yellow card)
- Pending Interventions (cyan card)
- Unread Alerts (blue card)

**Main Content (2 columns: 8-4 grid):**

**Left Column:**
- High Risk Students Table (red header)
  - Columns: Student, Risk Score, GPA, Attendance, Missing, Action
  - View button for each student
- Recent Alerts Card (yellow header)
  - List of alerts with badges
  - Alert type, message, student name, date

**Right Column:**
- Quick Actions Card
  - "Create Intervention" button
  - "View All Students" button
  - "Generate Report" button
- Upcoming Interventions Card
  - List of scheduled interventions
  - Student name, type, date/time

---

## Component Library for Figma

### Buttons
```
Primary: Blue background, white text, 8px radius
Secondary: White background, blue border, blue text
Success: Green background, white text
Warning: Yellow background, dark text
Danger: Red background, white text
```

### Cards
```
Background: White
Border: 1px solid #DEE2E6
Border Radius: 8px
Shadow: 0 2px 4px rgba(0,0,0,0.1)
Padding: 24px
```

### Badges
```
Small pill shape (16px radius)
Padding: 4px 12px
Font size: 12px
Colors: Info (blue), Success (green), Warning (yellow), Danger (red)
```

### Tables
```
Header: Light gray background
Rows: Hover effect (light blue)
Borders: 1px solid #DEE2E6
Cell padding: 12px
```

### Progress Bars
```
Height: 8px
Border radius: 4px
Background: Light gray
Fill: Success green
```

### Navigation Bar
```
Height: 60px
Background: Primary blue
Text: White
Logo: Heart-pulse icon + text
Dropdown: White background, shadow
```

---

## Figma Frame Sizes

```
Desktop: 1920 x 1080
Tablet: 768 x 1024
Mobile: 375 x 812
```

---

## Icons to Use (Bootstrap Icons)

```
heart-pulse - Logo
person-circle - User profile
book - Classes
clipboard-check - Assignments
heart - Wellness
graph-up - Stats
exclamation-triangle - Warnings
bell - Alerts
calendar-check - Interventions
plus-circle - Add actions
people - Students
flag - Report concern
```

---

## How to Create in Figma

1. **Create New File** - "Campus Care Prototype"

2. **Set up Design System**
   - Create color styles
   - Create text styles
   - Create component library

3. **Create Frames** (1920x1080 each)
   - Frame 1: Login
   - Frame 2: Register
   - Frame 3: Student Dashboard
   - Frame 4: Teacher Dashboard
   - Frame 5: Counselor Dashboard

4. **Add Components**
   - Navigation bar (reusable)
   - Cards (reusable)
   - Buttons (variants)
   - Input fields (variants)

5. **Add Interactions**
   - Login button → Student Dashboard
   - Register link → Register screen
   - Navigation items → Respective pages

6. **Create Prototype Flow**
   - Start: Login screen
   - Click Login → Dashboard (based on role)
   - Click Register → Registration screen
   - Navigation between pages

---

## Export Settings

- Format: PNG
- Scale: 2x
- Include: All frames
- Use for: Presentation/Documentation
