# 🏫 Ittihad Model School Management System (EduManage)

> **Enterprise-Grade School Administration & Student Information System**
> Built with Django 4.2 + PostgreSQL 18 | 4-Role RBAC | 50+ Templates | PDF/Excel Reports

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-green?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Installation & Setup](#installation--setup)
- [Database Configuration](#database-configuration)
- [Running the Application](#running-the-application)
- [User Roles & Access Control](#user-roles--access-control)
- [Modules & Endpoints](#modules--endpoints)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)

---

## Overview

**Ittihad Model School Management System** (EduManage) is a full-featured, production-ready school administration platform designed for Pakistani educational institutions. It handles everything from student admissions and fee challans to examination results, staff payroll, library management, and more — all from a unified, role-based dashboard.

The system is built to run on **PostgreSQL** as the sole and primary database engine, ensuring enterprise-grade data integrity, performance, and scalability.

---

## Key Features

### 🎓 Student Information System (SIS)
- Complete student admission & profile management
- 360° Student Dossier — fees, results, attendance, library, certificates all in one view
- Automated digital ID card generation on admission
- Roll number-based fast search & jump navigation
- Bulk & individual student ID card PDF generation
- Student directory Excel export

### 💰 Fee & Challan Management
- 3-copy bank fee challan PDF generation (Student / Bank / School copies)
- Bulk monthly fee voucher generation (class-wide)
- Auto late-fee calculation with configurable per-day fine
- Fee concession/scholarship support with percentage discounts
- Individual student fee ledger view
- Fee ledger Excel export
- SMS reminder simulation for overdue fees

### 📝 Examination & Results Engine
- Exam creation with date sheets & scheduling
- Admit card PDF generation per student
- Result entry with auto grade & GPA calculation (A+ to F scale)
- Official result card PDF generation
- Bulk class result cards PDF
- Class-wise merit list reports

### 👨‍🏫 Staff & HR Management
- Complete staff directory with department-wise categorization
- Staff ID card PDF generation
- Monthly payroll generation with allowances, bonuses & deductions
- Payroll slip PDF
- Payroll report Excel export
- Teacher salary disbursement & quick-pay system

### 📅 Attendance & Leave Management
- Daily student attendance marking with Present/Absent/Late/Leave/Half Day statuses
- Staff attendance with in/out time tracking
- Automated attendance percentage calculation
- Leave application workflow (Apply → Approve/Reject)
- SMS alert simulation on student absence

### 📚 Library Management
- Book catalogue with ISBN tracking & rack numbers
- Book issue & circulation system (Student/Staff borrowers)
- Auto overdue fine calculation (PKR 10/day)
- Book return processing

### 🏢 Inventory & Asset Management
- Fixed asset tracking with condition monitoring (Good/Fair/Needs Repair/Discarded)
- Consumable stock management with low-stock alerts
- Category-wise asset organization (Computers, Lab, Furniture, AV, Sports, Electrical)

### 📜 Official Certificates
- School Leaving / Transfer Certificate (TC)
- Character & Conduct Certificate
- Bonafide / Student Status Certificate
- Academic Merit Certificate
- Auto-numbered certificate system

### 📋 Homework, Notices & Timetable
- Class-wise homework assignment with due dates
- Digital notice board with categories & pinning
- Auto-generated class timetable from subjects
- Drag-and-shift period management via AJAX
- Full weekly timetable view (Monday–Saturday)

### 🔔 Notifications & Search
- System notification feed
- Global search across students, staff, fees, results, and more
- Real-time search API with keyboard shortcut (`Ctrl+K`)
- Dashboard stats JSON API

---

## Tech Stack

| Component           | Technology                                      |
|---------------------|------------------------------------------------|
| **Backend**         | Python 3.10+, Django 4.2+                      |
| **Database**        | PostgreSQL 18 (via `psycopg2-binary`)          |
| **PDF Generation**  | ReportLab 4.0+                                 |
| **Excel Export**    | openpyxl 3.1+                                  |
| **Image Processing**| Pillow 10.0+                                   |
| **Static Assets**   | WhiteNoise 6.6+ (production)                   |
| **Environment**     | python-dotenv 1.0+                             |
| **Frontend**        | Django Templates, HTML5, CSS3, JavaScript       |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    BROWSER / CLIENT                      │
│         (Admin / Teacher / Student / Accountant)         │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/HTTPS
┌─────────────────────▼───────────────────────────────────┐
│                 DJANGO APPLICATION                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  URL Router  │  │  Views (105K)│  │  Templates    │  │
│  │  (130 routes)│  │  + Role RBAC │  │  (52 pages)   │  │
│  └──────┬──────┘  └──────┬───────┘  └───────────────┘  │
│         │                │                               │
│  ┌──────▼────────────────▼──────────────────────────┐   │
│  │              14 Django Models                     │   │
│  │  SchoolSetting │ Student │ Staff │ Fee │ Exam     │   │
│  │  Result │ Attendance │ Payroll │ Book │ Asset     │   │
│  │  Certificate │ Homework │ Notice │ Timetable     │   │
│  └──────────────────────┬───────────────────────────┘   │
│                         │                                │
│  ┌──────────────────────▼───────────────────────────┐   │
│  │         PDF Utils    │    Excel Utils             │   │
│  │  (ReportLab Engine)  │  (openpyxl Engine)         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────┘
                      │ psycopg2
┌─────────────────────▼───────────────────────────────────┐
│              PostgreSQL 18 Database                      │
│              (edumanage_db)                               │
└─────────────────────────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites

- **Python 3.10+** installed
- **PostgreSQL 14+** installed and running
- **pip** package manager

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/school-management-system.git
cd school-management-system
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
```
Django>=4.2
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
Pillow>=10.0
reportlab>=4.0
openpyxl>=3.1
whitenoise>=6.6
```

### 3. Environment Configuration

Copy the example `.env` file and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL settings:

```env
# Database (PostgreSQL) Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=edumanage_db
DB_USER=postgres
DB_PASSWORD=YourPasswordHere
DB_HOST=127.0.0.1
DB_PORT=5432
CONN_MAX_AGE=600

# Security
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=*
```

---

## Database Configuration

### Create the PostgreSQL Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE edumanage_db;

-- Exit
\q
```

Or using Python:

```python
import psycopg2
conn = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='YourPassword', dbname='postgres')
conn.autocommit = True
cur = conn.cursor()
cur.execute("CREATE DATABASE edumanage_db")
conn.close()
```

### Run Migrations

```bash
python manage.py migrate
```

### Seed Initial Data (Optional)

```bash
python seed_initial_data.py
```

This creates demo users, students, staff, subjects, fees, results, and more for testing.

---

## Running the Application

### Development Server

```bash
python manage.py runserver
```

Access at: **http://127.0.0.1:8000**

### Network Access (LAN)

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## User Roles & Access Control

The system implements **4-Role RBAC** (Role-Based Access Control):

| Role | Username | Password | Portal URL | Permissions |
|------|----------|----------|-----------|-------------|
| 🔴 **Admin** | `admin` | `admin` | `/dashboard/` | Full system access — all modules, settings, reports |
| 💰 **Accountant** | `accountant` | `accountant123` | `/portal/accountant/` | Fee management, challans, fee exports |
| 👨‍🏫 **Teacher** | `teacher` | `teacher123` | `/portal/teacher/` | Homework, exams, results, assigned classes |
| 🎓 **Student** | `1001` (Roll No) | `12345678` | `/portal/student/` | View own profile, fees, results, attendance |

### Security Features
- Role-based redirect on login (auto-routes to correct portal)
- Unauthorized access blocked with redirect to user's portal
- CSRF protection on all forms
- Session-based authentication with 24-hour validity
- Password change support for students
- Admin can reset student passwords
- `models.PROTECT` on financial/audit foreign keys (prevents accidental data deletion)

---

## Modules & Endpoints

### Authentication & Portals
| Endpoint | Description |
|----------|-------------|
| `/login/` | Universal login page |
| `/logout/` | Logout |
| `/dashboard/` | Admin command center with stats |
| `/portal/teacher/` | Teacher dashboard |
| `/portal/student/` | Student self-service portal |
| `/portal/accountant/` | Accountant fee management portal |

### Students (SIS)
| Endpoint | Description |
|----------|-------------|
| `/students/` | Student directory with filters |
| `/students/add/` | New student admission form |
| `/students/<id>/` | 360° student profile dossier |
| `/students/<id>/id-card/` | Individual student ID card PDF |
| `/students/search-jump/?q=` | Fast search by roll no / name |
| `/students/export/excel/` | Export directory to Excel |
| `/students/export/id-cards/` | Bulk student ID cards PDF |

### Fees & Challans
| Endpoint | Description |
|----------|-------------|
| `/fees/` | Fee management dashboard |
| `/fees/add/` | Generate new fee voucher |
| `/fees/bulk-generate/` | Bulk monthly fee generation |
| `/fees/<id>/voucher-pdf/` | 3-copy bank fee challan PDF |
| `/fees/bulk-class-pdf/` | Bulk class fee vouchers PDF |
| `/fees/student/<id>/` | Individual student fee ledger |
| `/fees/export/excel/` | Fee ledger Excel export |

### Staff & Payroll
| Endpoint | Description |
|----------|-------------|
| `/staff/` | Staff & HR directory |
| `/staff/export/id-cards/` | Staff ID cards PDF |
| `/payroll/` | Payroll management |
| `/payroll/generate/` | Generate monthly payroll |
| `/payroll/<id>/slip/` | Payroll slip PDF |
| `/payroll/export/excel/` | Payroll Excel report |

### Exams & Results
| Endpoint | Description |
|----------|-------------|
| `/exams/` | Exam schedule & date sheets |
| `/results/` | Results ledger |
| `/results/student/<id>/pdf/` | Official result card PDF |
| `/results/bulk-class-pdf/` | Bulk class result cards |
| `/results/merit-list/` | Class merit list report |

### Attendance & Leaves
| Endpoint | Description |
|----------|-------------|
| `/attendance/students/` | Student attendance register |
| `/attendance/staff/` | Staff attendance register |
| `/leaves/` | Leave applications desk |
| `/sms-logs/` | SMS alert audit logs |

### Library, Inventory, Certificates
| Endpoint | Description |
|----------|-------------|
| `/library/books/` | Library catalogue |
| `/library/issues/` | Book circulation |
| `/inventory/assets/` | Asset & stock inventory |
| `/certificates/` | Official certificates registry |

### Homework, Notices, Timetable
| Endpoint | Description |
|----------|-------------|
| `/homework/` | Homework assignments |
| `/notices/` | Digital notice board |
| `/timetable/` | Class timetable & schedules |

### Settings & API
| Endpoint | Description |
|----------|-------------|
| `/settings/school/` | School profile & branding settings |
| `/notifications/` | System notification feed |
| `/search/` | Global search results page |
| `/api/global-search/` | Search JSON API |
| `/api/dashboard-stats/` | Dashboard statistics JSON API |

---

## Project Structure

```
Apna School ManageMent/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (PostgreSQL config)
├── .env.example                 # Environment template
├── seed_initial_data.py         # Demo data seeder
├── audit_all_routes.py          # Comprehensive 4-role route audit script
│
├── school_management/           # Django project settings
│   ├── settings.py              # PostgreSQL + WhiteNoise config
│   ├── urls.py                  # Root URL configuration
│   └── wsgi.py                  # WSGI entry point
│
├── core/                        # Main Django application
│   ├── models.py                # 14 enterprise models (795 lines)
│   ├── views.py                 # All views & RBAC logic (105K)
│   ├── urls.py                  # 130 URL routes
│   ├── forms.py                 # Django forms (23K)
│   ├── admin.py                 # Django admin configuration
│   ├── context_processors.py    # School settings context processor
│   ├── pdf_utils.py             # ReportLab PDF generation (55K)
│   ├── excel_utils.py           # openpyxl Excel export utilities
│   ├── sms_utils.py             # SMS alert simulation
│   └── templatetags/            # Custom template tags
│
├── templates/
│   ├── base.html                # Master layout template (31K)
│   └── core/                    # 52 page templates
│       ├── dashboard.html
│       ├── login.html
│       ├── student_list.html
│       ├── student_detail.html  # 360° dossier view
│       ├── fee_list.html
│       ├── timetable_list.html
│       └── ... (48 more templates)
│
├── static/                      # CSS, JS, images
├── staticfiles/                 # Collected static files (production)
├── media/                       # Uploaded files (photos, branding)
│
├── test_dashboard.py            # Dashboard tests
├── test_password_lifecycle.py   # Password management tests
├── test_salary_and_pdf_headers.py # Payroll & PDF tests
├── test_search_features.py      # Search functionality tests
├── test_student_security.py     # Student security tests
└── test_ui_and_bulk_pdfs.py     # UI & bulk PDF generation tests
```

---

## API Endpoints

| Endpoint | Method | Response | Description |
|----------|--------|----------|-------------|
| `/api/dashboard-stats/` | GET | JSON | Real-time dashboard statistics |
| `/api/global-search/?q=` | GET | JSON | Search across all modules |

### Dashboard Stats Response Example:
```json
{
    "total_students": 150,
    "total_staff": 25,
    "total_fee_collected": 450000,
    "total_fee_pending": 120000,
    "attendance_today": 142
}
```

---

## Running Tests

```bash
# Run all test scripts
python test_dashboard.py
python test_search_features.py
python test_student_security.py
python test_password_lifecycle.py
python test_salary_and_pdf_headers.py
python test_ui_and_bulk_pdfs.py

# Run comprehensive 4-role audit
python audit_all_routes.py
```

---

## School Branding

The system supports full school branding customization via `/settings/school/`:

- School name & tagline
- Registration number
- Contact details (phone, email, website)
- School logo upload
- Bank details for fee challans (Bank name, account, IBAN, branch)
- Currency symbol
- Late fee per-day configuration
- Principal name (for certificates)

---

## Production Deployment

### Security Hardening
Set these in your `.env` for production:

```env
DEBUG=False
SECRET_KEY=your-very-strong-production-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

WhiteNoise will automatically serve compressed & cached static files in production.

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-module`)
3. Commit your changes (`git commit -m 'Add new module'`)
4. Push to the branch (`git push origin feature/new-module`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

<p align="center">
  <strong>Built with ❤️ for Pakistani Educational Institutions</strong><br>
  <em>Ittihad Model School Management System — Excellence in Education & Character Building</em>
</p>
