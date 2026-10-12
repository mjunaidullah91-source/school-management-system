import os
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import (
    SchoolSetting, Student, Staff, Subject, Fee, Exam, ExamSchedule, Result,
    StudentAttendance, StaffAttendance, LeaveApplication, SMSAlertLog,
    Payroll, Book, BookIssue, Asset, StockItem, Certificate,
    Homework, Notice, Timetable, Notification
)
from core.views import get_or_create_student_user

print("1. Seeding School Settings...")
setting = SchoolSetting.get_settings()
setting.school_name = "Ittihad Model School"
setting.tagline = "Excellence in Education & Character Building"
setting.registration_no = "REG-IMS-2026-987"
setting.contact_phone = "+92 51 9876543 / 0300-1234567"
setting.email = "info@ittihadmodelschool.edu.pk"
setting.bank_name = "National Allied Bank Ltd"
setting.bank_account_title = "Ittihad Model School Trust"
setting.bank_account_no = "0123-4567890123"
setting.iban = "PK36NABL0000012345678901"
setting.bank_branch = "Main Campus Branch (Code: 0422)"
setting.principal_name = "Prof. Dr. Sarah Jenkins"
setting.save()

print("2. Creating Superuser & Staff Accounts...")
# Admin
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser('admin', 'admin@ittihadmodelschool.edu.pk', 'admin')
    admin_user.first_name = "System"
    admin_user.last_name = "Administrator"
    admin_user.save()
else:
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin')
    admin_user.save()

# Teacher 1
teacher_user, _ = User.objects.get_or_create(
    username='teacher',
    defaults={'email': 'teacher@ittihadmodelschool.edu.pk', 'first_name': 'Prof. Tariq', 'last_name': 'Mahmood'}
)
teacher_user.set_password('teacher123')
teacher_user.save()

staff1, _ = Staff.objects.get_or_create(
    emp_id='EMP-001',
    defaults={
        'user': teacher_user,
        'name': 'Prof. Tariq Mahmood',
        'designation': 'Senior Science Master',
        'department': 'Academics',
        'contact': '0300-9876541',
        'email': 'teacher@ittihadmodelschool.edu.pk',
        'basic_salary': Decimal('65000.00'),
    }
)
staff1.user = teacher_user
staff1.save()

# Staff 2
staff2, _ = Staff.objects.get_or_create(
    emp_id='EMP-002',
    defaults={
        'name': 'Ms. Ayesha Khan',
        'designation': 'Head of Mathematics',
        'department': 'Academics',
        'contact': '0300-9876542',
        'email': 'ayesha@ittihadmodelschool.edu.pk',
        'basic_salary': Decimal('58000.00'),
    }
)

print("3. Creating Subjects...")
sub_math, _ = Subject.objects.get_or_create(code='MATH-10', defaults={'name': 'Mathematics', 'max_marks': 100, 'passing_marks': 40, 'student_class': '10', 'teacher': staff2})
sub_sci, _  = Subject.objects.get_or_create(code='PHY-10',  defaults={'name': 'Physics', 'max_marks': 100, 'passing_marks': 40, 'student_class': '10', 'teacher': staff1})
sub_eng, _  = Subject.objects.get_or_create(code='ENG-10',  defaults={'name': 'English Literature', 'max_marks': 100, 'passing_marks': 40, 'student_class': '10', 'teacher': staff1})
sub_chem, _ = Subject.objects.get_or_create(code='CHEM-10', defaults={'name': 'Chemistry', 'max_marks': 100, 'passing_marks': 40, 'student_class': '10', 'teacher': staff1})

print("4. Creating Students & Auto-Provisioning User Accounts...")
students_data = [
    ('1001', 'Muhammad Ali', 'Class 10', 'A', 'Bashir Ahmed', '0300-1111001', Decimal('3500.00'), Decimal('0.00')),
    ('1002', 'Fatima Zahra', 'Class 10', 'A', 'Tariq Hussain', '0300-1111002', Decimal('3500.00'), Decimal('10.00')),
    ('1003', 'Ahmed Hassan', 'Class 10', 'A', 'Hassan Raza', '0300-1111003', Decimal('3500.00'), Decimal('0.00')),
    ('1004', 'Zainab Bibi', 'Class 9', 'A', 'Muhammad Aslam', '0300-1111004', Decimal('3200.00'), Decimal('0.00')),
    ('1005', 'Hamza Khan', 'Class 9', 'A', 'Imran Khan', '0300-1111005', Decimal('3200.00'), Decimal('20.00')),
]

created_students = []
for roll, name, cls, sec, f_name, contact, fee, conc in students_data:
    cls_clean = cls.replace('Class ', '')
    st, _ = Student.objects.get_or_create(
        roll_no=roll,
        defaults={
            'admission_no': f'ADM-{roll}',
            'name': name,
            'father_name': f_name,
            'student_class': cls_clean,
            'section': sec,
            'contact': contact,
            'emergency_contact': contact,
            'monthly_fee': fee,
            'concession_percent': conc,
        }
    )
    # Ensure user account with password 12345678
    user = get_or_create_student_user(st)
    user.set_password('12345678')
    user.save()
    created_students.append(st)

print("5. Generating Fees & Challans...")
today = date.today()
for st in created_students:
    Fee.objects.get_or_create(
        voucher_no=f"VCH-{st.roll_no}-{today.year}-{today.month:02d}",
        student=st,
        month='October',
        year=today.year,
        defaults={
            'fee_type': 'Monthly',
            'tuition_fee': st.monthly_fee,
            'amount': st.get_effective_monthly_fee(),
            'paid_amount': st.get_effective_monthly_fee() if st.roll_no == '1001' else Decimal('0.00'),
            'status': 'Paid' if st.roll_no == '1001' else 'Unpaid',
            'issue_date': today,
            'due_date': today + timedelta(days=10),
        }
    )

print("6. Generating Examination & Results...")
exam, _ = Exam.objects.get_or_create(title="Mid-Term Examinations 2026", defaults={'exam_type': 'Mid-Term', 'start_date': today + timedelta(days=15), 'end_date': today + timedelta(days=25)})
ExamSchedule.objects.get_or_create(exam=exam, subject=sub_math, defaults={'student_class': '10', 'exam_date': today + timedelta(days=15), 'start_time': '09:00:00', 'end_time': '12:00:00', 'room_no': 'Hall A'})
ExamSchedule.objects.get_or_create(exam=exam, subject=sub_sci,  defaults={'student_class': '10', 'exam_date': today + timedelta(days=17), 'start_time': '09:00:00', 'end_time': '12:00:00', 'room_no': 'Hall A'})

# Results for Student 1001
s1 = created_students[0]
Result.objects.get_or_create(student=s1, subject=sub_math, exam=exam, exam_type='Mid-Term', year=2026, defaults={'marks_obtained': 92, 'max_marks': 100, 'teacher_remarks': 'Outstanding performance'})
Result.objects.get_or_create(student=s1, subject=sub_sci,  exam=exam, exam_type='Mid-Term', year=2026, defaults={'marks_obtained': 88, 'max_marks': 100, 'teacher_remarks': 'Very Good'})
Result.objects.get_or_create(student=s1, subject=sub_eng,  exam=exam, exam_type='Mid-Term', year=2026, defaults={'marks_obtained': 85, 'max_marks': 100, 'teacher_remarks': 'Well done'})

print("7. Generating Attendance & Homework...")
for d_offset in range(10):
    att_d = today - timedelta(days=d_offset)
    for st in created_students:
        StudentAttendance.objects.get_or_create(student=st, date=att_d, defaults={'status': 'Present'})

Homework.objects.get_or_create(
    title="Quadratic Equations Exercise 3.2",
    subject=sub_math,
    teacher=staff2,
    student_class="10",
    section="A",
    defaults={'description': 'Solve problems 1 to 15 from textbook page 78 in neat notebooks.', 'assigned_date': today, 'due_date': today + timedelta(days=2)}
)

Notice.objects.get_or_create(
    title="Mid-Term Date Sheet Announcement",
    defaults={'category': 'Academic', 'content': 'Mid-term examinations for classes 9 & 10 will commence from 22nd October 2026. Please collect admit cards.', 'target_audience': 'All', 'is_active': True}
)

Notification.objects.get_or_create(
    title="System Initialized",
    defaults={'message': 'Ittihad Model School Management System initialized with enterprise production datasets.'}
)

print("\n=== INITIAL SEEDING COMPLETE ===")
print(f"Total Students: {Student.objects.count()}")
print(f"Total Staff: {Staff.objects.count()}")
print(f"Total Fees: {Fee.objects.count()}")
print(f"Total Results: {Result.objects.count()}")
