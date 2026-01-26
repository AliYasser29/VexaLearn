# 🎓 VexaLearn - Advanced Academy Management System (LMS)

**VexaLearn** is a powerful, Django-based Learning Management System (LMS) designed to digitize the operations of educational academies and tutoring centers. It goes beyond simple administration by offering a "Smart Enrollment" system, isolating student-teacher interactions per course, and providing robust tools for attendance, academic materials, and performance tracking.

---

## 🚀 Key Features (Comprehensive List)

### 1. 👥 Advanced Role Management
The system is built on a strict role-based architecture:
* **Super Admin / Manager:** Full control over financial settings, system configuration, user management, and global chat monitoring.
* **Supervisor:** Manages assigned student groups, tracks attendance, and acts as a bridge between parents and teachers.
* **Teacher:**
    * Managed by **Subject** specialization (e.g., Physics, Math).
    * Can upload course materials.
    * Create and grade Quizzes.
    * Send Daily Reports to students.
* **Student:** Access to enrolled courses, materials library, quiz grades, and direct chat with assigned teachers.
* **Ghost User Cleanup:** Automated **Signals** ensuring that if a profile (Teacher/Student) is deleted, the associated login account is automatically deactivated to secure the system.

### 2. 📚 Smart Academic Structure
Unlike traditional systems, VexaLearn uses a flexible academic hierarchy:
* **Multi-National Support:** Define Countries, Curriculums, and Academic Years.
* **Subject-Based Logic:** Teachers are linked to **Subjects**, not just generic courses.
* **The "Smart Enrollment" Logic:**
    * Courses are created as "Curriculums" (e.g., "High School Math").
    * When enrolling a student, the admin selects the **Specific Teacher** for that student in that course.
    * *Benefit:* Multiple teachers can teach the same course content, but each student is linked to only one specific teacher for follow-up.

### 3. 📂 Context-Aware Material Library
A smart file sharing system for educational resources:
* **For Teachers:** Upload files (PDFs, Docs, Images) linked to specific courses they teach.
* **For Students:** When accessing the library, the system intelligently filters files to show **only** materials uploaded by *their* assigned teacher for that course.
* **Features:** File type icons, download tracking, and description support.

### 4. 📝 Quiz & Grading System
* **Creation:** Teachers can create quizzes with titles, descriptions, pass marks, and duration.
* **Tracking:** Students' attempts are recorded.
* **Profile Integration:** Students can view their quiz history and grades directly on their profile card.

### 5. ✅ Attendance & Renewal Alerts
* **Digital Attendance:** Supervisors mark "Present" or "Absent".
* **Session Tracking:** The system calculates the percentage of course completion based on session counts.
* **Smart Alerts:**
    * **Instant Email:** Sent to parents immediately upon marking attendance.
    * **Renewal Warning:** Automated emails sent when a subscription is near expiration (e.g., < 25% sessions remaining).

### 6. 💬 Communication Hub
* **Real-Time Chat:** Integrated messaging system between Students, Teachers, and Supervisors.
* **Chat Monitoring:** Admins can view conversation logs for quality assurance using a dedicated "Universal Chat Monitor" dashboard.
* **Video Call Integration:** Built-in support for **Agora SDK** for creating video sessions/classes.
* **Daily Reports:** Teachers can submit performance reports (with attachments) that appear on the student's timeline.

### 7. 🔔 Notification System
* **Async Emails:** All emails are sent asynchronously (using threading) to ensure the UI never freezes during bulk operations.
* **In-App Notifications:** Real-time bell notifications for students regarding:
    * Attendance/Absence recording.
    * New Quizzes.
    * New Materials.

### 8. 🛠️ Admin & UI Experience
* **Modern UI:** Built with **Django Unfold** for a clean, responsive admin panel.
* **AJAX Interactivity:** Dynamic dropdowns (e.g., selecting a course automatically filters the list of available teachers for that subject).
* **Landing Page:** Public-facing page with country/academy filtering.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.x, Django 5.x
* **Database:** SQLite (Dev) / PostgreSQL (Prod recommended)
* **Frontend:** HTML5, CSS3, JavaScript (jQuery/AJAX), FontAwesome
* **Admin Theme:** `django-unfold`
* **Video Calls:** Agora RTC
* **Utils:** `django-import-export`, `Pillow`

---

## 📂 Project Structure

```bash
Academy System/
├── academy_project/      # Settings, URLs, WSGI
├── core/                 # Main Application
│   ├── models.py         # Database Schema (Subject, Teacher, Enrollment, Material...)
│   ├── views.py          # Logic (Smart Library, Chat, AJAX Handlers)
│   ├── forms.py          # Dynamic Forms (Teacher filtering)
│   ├── signals.py        # Automation (Emails, Cleanup)
│   ├── utils.py          # Async Email Function
│   └── templates/        # Frontend (Profile, Library, Dashboards)
├── quiz/                 # (Optional) Quiz App Logic
├── manage.py
└── requirements.txt

git clone [https://github.com/yourusername/vexalearn.git](https://github.com/yourusername/vexalearn.git)
cd vexalearn

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt

Configure Settings:

Update .env with your Email credentials (SMTP) and Agora Keys.

python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

📖 Usage Guide (The New Workflow)
1. Initial Setup (Admin)
Go to Admin Panel.

Add Countries, Education Types, and Academic Years.

Add Subjects (linked to Education Types).

Add Teachers and assign them Subjects (e.g., Teacher A teaches Math).

Create Courses (linked to a Subject, NOT a specific teacher yet).

2. Registering a Student
Go to the Admin Panel Dashboard.

Fill in the Student's basic info (Name, Parent Phone, etc.).

The system creates the account and auto-redirects you to the Enrollment Page.

Select a Course -> The system filters Teachers who teach this Subject -> Select the specific Teacher -> Save.

3. Using the Library
Teacher: Logs in -> Clicks "Upload Material" -> Selects one of their courses -> Uploads file.

Student: Logs in -> Goes to Profile -> Clicks "Library" next to the course -> Sees files uploaded by their specific teacher only.

🔒 Security
CSRF Protection: Enabled on all forms.

Role Decorators: @login_required and custom permission checks on all views.

Data Isolation: Strict queries ensure students/teachers access only their own relevant data.

Developed with ❤️ by VexaLearn Team