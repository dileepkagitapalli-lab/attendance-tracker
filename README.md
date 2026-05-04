# 📊 AttendTrack — Smart Attendance Tracking System

**Author:** Dileep Kumar

> A smart, student-centric attendance management system that replaces manual tracking with an automated, analytical, and visually intuitive experience.

---

## ✨ Overview

**AttendTrack** is a Django-based web application designed to help students efficiently manage attendance using a personalized timetable.

It combines:

* 📅 Structured scheduling
* 🧠 Intelligent tracking
* 📊 Real-time analytics

All wrapped in a **modern glassmorphic UI** for a clean and engaging experience.

---

## 🎬 System Flow

```
[ REGISTER / LOGIN ]
        ↓
[ CREATE TIMETABLE ]
        ↓
[ CONFIRM SCHEDULE ]
        ↓
[ DAILY ATTENDANCE MARKING ]
        ↓
[ DASHBOARD ANALYTICS ]
        ↓
[ REPORT EXPORT / ALERTS ]
```

---

## 🧩 Core Features

### 🔐 Authentication

* Student registration with unique Roll Number
* Password-less login (Name + Roll No)
* Secure access control system

---

### 📅 Timetable Management

* Day-wise schedule creation (Mon–Sat)
* Custom subject input
* Start/End time selection with AM/PM
* Final confirmation before saving

---

### 🧠 Smart Attendance Tracking

* Auto-detects current day
* Displays relevant subjects only
* Mark attendance (Present / Absent)
* Unit-based calculation (duration → units)

---

### 📆 Working Day Logic

* Mark day as working or holiday
* Automatically skips attendance for holidays

---

### ➕ Extra Class Handling

* Add custom extra classes
* Fully integrated into attendance calculations

---

### 📊 Dashboard Analytics

* Overall attendance percentage
* Subject-wise breakdown:

  * Total units
  * Attended units
  * Percentage
* Visual indicators:

  * 🟢 Safe
  * 🔴 Warning

---

### ⚠️ Attendance Alerts

* Warning when attendance drops below **75%**

---

### 📅 Subject Detail View

* Complete attendance history
* Upcoming 5 scheduled classes

---

### 📥 Export System

* 📄 PDF report generation
* 📊 Excel data export

---

## 🧠 Tech Stack

| Layer     | Technology              | Purpose                |
| --------- | ----------------------- | ---------------------- |
| Backend   | Django 5.1 (Python)     | Core application logic |
| Frontend  | HTML5, CSS3, JavaScript | UI & interaction       |
| Database  | SQLite                  | Data storage           |
| Reporting | xhtml2pdf, openpyxl     | Export features        |

---

## 🗂️ Project Structure

```
AttendTrack/
│
├── attendance/          # Models, Views, Business Logic
├── config/              # Django Settings & Configurations
├── static/              # CSS, JS, Images
├── templates/           # HTML Templates
├── screenshots/         # UI Previews
├── db.sqlite3           # Database
└── README.md
```

---

## ⚙️ Application Workflow

### Step 1: User Registration

User creates profile using academic details.

### Step 2: Timetable Setup

Subjects and time slots are entered day-wise.

### Step 3: Confirmation

User verifies timetable before saving.

### Step 4: Daily Usage

Attendance is marked dynamically based on current schedule.

### Step 5: Analysis

Dashboard provides real-time insights and warnings.

---

## 📊 System Logic

* Attendance is calculated using **unit-based tracking**
* Extra classes are dynamically merged
* Real-time percentage updates
* Threshold monitoring (75%)

---

## 🎨 UI Design

| Element    | Description                 |
| ---------- | --------------------------- |
| Theme      | Glassmorphism UI            |
| Layout     | Clean, student-friendly     |
| Indicators | Color-coded (Green / Red)   |
| Experience | Minimal, intuitive workflow |

---

## 🔒 Data Handling

* Local database (SQLite)
* No external data sharing
* User-specific records
* Secure access control

---

## 🚀 Future Enhancements

* 🤖 AI-based attendance prediction
* 📱 Mobile application (Android/iOS)
* 🔔 Notifications for reminders
* ☁️ Cloud database (PostgreSQL)

---

## ▶️ Running the Project

```bash
git clone https://github.com/your-username/attendance-tracker.git
cd attendance-tracker
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 👨‍💻 Author

**Dileep Kumar**

---

## 📜 License

This project is for educational purposes.

---

> *"Track smart. Stay above 75%. Stay stress-free."*
