"""
Enterprise Models for EduManage School Management System.
Includes: Student, Staff/HR, Fees & Challan, Exams & Grading, Attendance,
Library, Inventory, Certificates, Homework, Notices, Timetable, School Profile.

Optimized with db_index=True on key query fields, models.PROTECT on financial/audit FKs,
and performance-tuned properties.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, datetime
from decimal import Decimal


# ─── ENUMS & CHOICES ─────────────────────────────────────────────────────────
CLASS_CHOICES = [
    ('Nursery', 'Nursery'), ('Prep', 'Prep'), ('KG', 'Kindergarten'),
    ('1', 'Class 1'), ('2', 'Class 2'), ('3', 'Class 3'),
    ('4', 'Class 4'), ('5', 'Class 5'), ('6', 'Class 6'),
    ('7', 'Class 7'), ('8', 'Class 8'), ('9', 'Class 9'),
    ('10', 'Class 10'), ('11', 'Class 11'), ('12', 'Class 12'),
]

SECTION_CHOICES = [
    ('A', 'Section A'), ('B', 'Section B'),
    ('C', 'Section C'), ('D', 'Section D'),
]

GENDER_CHOICES = [
    ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other'),
]

BLOOD_GROUPS = [
    ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
    ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('Unknown', 'Unknown'),
]

DAYS_OF_WEEK = [
    ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),
]

ATTENDANCE_STATUS = [
    ('Present', 'Present'),
    ('Absent', 'Absent'),
    ('Late', 'Late'),
    ('Leave', 'Leave'),
    ('Half Day', 'Half Day'),
]

FEE_STATUS = [
    ('Paid', 'Paid'),
    ('Unpaid', 'Unpaid'),
    ('Partial', 'Partial'),
    ('Overdue', 'Overdue'),
]

FEE_TYPE = [
    ('Monthly', 'Monthly Tuition Fee'),
    ('Admission', 'Admission Fee'),
    ('Exam', 'Exam Fee'),
    ('Library', 'Library Fee'),
    ('Laboratory', 'Laboratory Fee'),
    ('Sports', 'Sports Fee'),
    ('Annual', 'Annual Charges'),
    ('Custom', 'Custom / Other Fee'),
]

EXAM_TYPE = [
    ('Monthly', 'Monthly Assessment'),
    ('Mid-Term', 'Mid-Term Examination'),
    ('Final', 'Annual / Final Examination'),
    ('Quiz', 'Quiz / Class Test'),
]

MONTH_CHOICES = [
    ('January', 'January'), ('February', 'February'), ('March', 'March'),
    ('April', 'April'), ('May', 'May'), ('June', 'June'),
    ('July', 'July'), ('August', 'August'), ('September', 'September'),
    ('October', 'October'), ('November', 'November'), ('December', 'December'),
]


# ─── 1. SCHOOL PROFILE & SYSTEM SETTINGS ──────────────────────────────────────
class SchoolSetting(models.Model):
    school_name        = models.CharField(max_length=200, default='Ittihad Model School')
    tagline            = models.CharField(max_length=250, default='Excellence in Education & Character Building')
    registration_no    = models.CharField(max_length=100, default='REG-IMS-2026-987')
    address            = models.TextField(default='Sector H-9, Educational Complex, Capital City')
    contact_phone      = models.CharField(max_length=50, default='+92 51 9876543 / 0300-1234567')
    email              = models.EmailField(default='info@ittihadmodelschool.edu.pk')
    website            = models.URLField(default='https://ittihadmodelschool.edu.pk', blank=True)
    logo               = models.ImageField(upload_to='school_branding/', default='school_branding/logo.png', blank=True, null=True)
    bank_name          = models.CharField(max_length=100, default='National Allied Bank Ltd')
    bank_account_title = models.CharField(max_length=150, default='Ittihad Model School Trust')
    bank_account_no    = models.CharField(max_length=50, default='0123-4567890123')
    iban               = models.CharField(max_length=50, default='PK36NABL0000012345678901')
    bank_branch        = models.CharField(max_length=100, default='Main Campus Branch (Code: 0422)')
    currency_symbol    = models.CharField(max_length=10, default='PKR')
    late_fee_per_day   = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)
    principal_name     = models.CharField(max_length=100, default='Prof. Dr. Sarah Jenkins')

    def __str__(self):
        return self.school_name

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(
            id=1,
            defaults={
                'school_name': 'Ittihad Model School',
                'tagline': 'Excellence in Education & Character Building',
                'logo': 'school_branding/logo.png',
            }
        )
        return obj


# ─── 2. STAFF & HR MANAGEMENT ────────────────────────────────────────────────
class Staff(models.Model):
    DEPARTMENT_CHOICES = [
        ('Academics', 'Academics / Teaching'),
        ('Administration', 'Administration'),
        ('Finance', 'Finance & Accounts'),
        ('Library', 'Library & Resource'),
        ('IT', 'IT & Computer Lab'),
        ('Support', 'Support & Maintenance'),
    ]

    user           = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_profile')
    emp_id         = models.CharField(max_length=20, unique=True, db_index=True)
    name           = models.CharField(max_length=120, db_index=True)
    father_or_spouse = models.CharField(max_length=120, blank=True)
    designation    = models.CharField(max_length=100)
    department     = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='Academics', db_index=True)
    qualification  = models.CharField(max_length=150, blank=True)
    gender         = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    blood_group    = models.CharField(max_length=10, choices=BLOOD_GROUPS, default='Unknown')
    dob            = models.DateField(null=True, blank=True)
    contact        = models.CharField(max_length=25, db_index=True)
    emergency_contact = models.CharField(max_length=25, blank=True)
    email          = models.EmailField(blank=True)
    cnic_or_nid    = models.CharField(max_length=30, blank=True, db_index=True)
    address        = models.TextField(blank=True)
    photo          = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    joining_date   = models.DateField(default=date.today)
    basic_salary   = models.DecimalField(max_digits=10, decimal_places=2, default=35000.00)
    is_active      = models.BooleanField(default=True, db_index=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['emp_id']

    def __str__(self):
        return f"{self.name} ({self.emp_id}) - {self.designation}"


# ─── 3. STUDENT MODEL ─────────────────────────────────────────────────────────
class Student(models.Model):
    user           = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_profile')
    roll_no        = models.CharField(max_length=20, unique=True, db_index=True)
    admission_no   = models.CharField(max_length=30, blank=True, db_index=True)
    name           = models.CharField(max_length=100, db_index=True)
    father_name    = models.CharField(max_length=100, blank=True)
    father_occupation = models.CharField(max_length=100, blank=True)
    mother_name    = models.CharField(max_length=100, blank=True)
    gender         = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    blood_group    = models.CharField(max_length=10, choices=BLOOD_GROUPS, default='Unknown')
    dob            = models.DateField(null=True, blank=True)
    student_class  = models.CharField(max_length=10, choices=CLASS_CHOICES, db_index=True)
    section        = models.CharField(max_length=5, choices=SECTION_CHOICES, default='A', db_index=True)
    contact        = models.CharField(max_length=25, blank=True, db_index=True)
    emergency_contact = models.CharField(max_length=25, blank=True, db_index=True)
    email          = models.EmailField(blank=True)
    address        = models.TextField(blank=True)
    photo          = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    admission_date = models.DateField(default=date.today)
    
    # Financial details
    monthly_fee    = models.DecimalField(max_digits=10, decimal_places=2, default=3500.00)
    concession_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    concession_reason  = models.CharField(max_length=150, blank=True, help_text="e.g. Merit Scholarship, Siblings")
    
    is_active      = models.BooleanField(default=True, db_index=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_class', 'section', 'roll_no']

    def __str__(self):
        return f"{self.name} ({self.roll_no}) - Class {self.student_class}-{self.section}"

    def get_effective_monthly_fee(self):
        discount = (self.monthly_fee * (self.concession_percent / Decimal(100)))
        return self.monthly_fee - discount

    def get_total_fees_paid(self):
        return self.fee_set.filter(status='Paid').aggregate(
            total=models.Sum('paid_amount'))['total'] or Decimal('0.00')

    def get_total_fees_due(self):
        unpaid = self.fee_set.filter(status__in=['Unpaid', 'Partial', 'Overdue'])
        total_due = Decimal('0.00')
        for f in unpaid:
            total_due += f.balance()
        return total_due

    def get_attendance_percentage(self, current_month_only=False):
        records = self.attendance_records.all()
        if current_month_only:
            today = date.today()
            records = records.filter(date__year=today.year, date__month=today.month)
        total = records.count()
        if total == 0:
            return 100.0
        present = records.filter(status__in=['Present', 'Late', 'Half Day']).count()
        return round((present / total) * 100, 1)


# ─── 4. SUBJECTS & CURRICULUM ────────────────────────────────────────────────
class Subject(models.Model):
    name          = models.CharField(max_length=100)
    code          = models.CharField(max_length=15, unique=True, db_index=True)
    max_marks     = models.IntegerField(default=100)
    passing_marks = models.IntegerField(default=40)
    student_class = models.CharField(max_length=10, choices=CLASS_CHOICES, blank=True, db_index=True)
    teacher       = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_subjects')

    class Meta:
        ordering = ['student_class', 'name']

    def __str__(self):
        return f"{self.name} ({self.code}) - Class {self.student_class}"


# ─── 5. FEE & CHALLAN VOUCHER SYSTEM (PROTECTED FK) ──────────────────────────
class Fee(models.Model):
    voucher_no   = models.CharField(max_length=30, unique=True, blank=True, db_index=True)
    # Protected against accidental student deletion destroying financial audits
    student      = models.ForeignKey(Student, on_delete=models.PROTECT)
    fee_type     = models.CharField(max_length=20, choices=FEE_TYPE, default='Monthly', db_index=True)
    month        = models.CharField(max_length=15, choices=MONTH_CHOICES, blank=True, db_index=True)
    year         = models.IntegerField(default=date.today().year, db_index=True)
    
    # Financial breakdown
    tuition_fee  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exam_fee     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_fee    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee_fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    concession   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    amount       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status       = models.CharField(max_length=15, choices=FEE_STATUS, default='Unpaid', db_index=True)
    
    issue_date   = models.DateField(default=date.today, db_index=True)
    due_date     = models.DateField(null=True, blank=True, db_index=True)
    paid_date    = models.DateField(null=True, blank=True)
    payment_mode = models.CharField(max_length=30, default='Cash', choices=[('Cash','Cash'),('Bank Deposit','Bank Deposit'),('Pay Order','Pay Order'),('Online Transfer','Online Transfer')])
    remarks      = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-id']

    def __str__(self):
        return f"{self.voucher_no or 'VCH'} - {self.student.name} ({self.month} {self.year})"

    def balance(self):
        return max(Decimal('0.00'), self.amount - self.paid_amount)

    def calculate_total(self):
        gross = self.tuition_fee + self.admission_fee + self.exam_fee + self.other_fee + self.late_fee_fine
        net = max(Decimal('0.00'), gross - self.concession)
        return net

    def save(self, *args, **kwargs):
        # Auto calculate amount if breakdown is given
        if self.tuition_fee > 0 or self.admission_fee > 0 or self.exam_fee > 0 or self.other_fee > 0:
            self.amount = self.calculate_total()

        # Check late fee if past due date and unpaid
        if self.due_date and date.today() > self.due_date and self.paid_amount < self.amount:
            if self.status != 'Paid' and self.late_fee_fine == 0:
                settings = SchoolSetting.get_settings()
                days_late = (date.today() - self.due_date).days
                if days_late > 0:
                    self.late_fee_fine = min(Decimal('1000.00'), settings.late_fee_per_day * days_late)
                    self.amount = self.calculate_total()

        # Update status
        if self.paid_amount >= self.amount and self.amount > 0:
            self.status = 'Paid'
        elif self.paid_amount > 0:
            self.status = 'Partial'
        elif self.due_date and date.today() > self.due_date:
            self.status = 'Overdue'
        else:
            self.status = 'Unpaid'

        # Generate unique voucher number before insert if missing
        if not self.voucher_no:
            import time, random
            unique_suffix = f"{int(time.time() * 1000) % 1000000:06d}{random.randint(10,99)}"
            self.voucher_no = f"VCH-{self.year}-{unique_suffix}"

        super().save(*args, **kwargs)


# ─── 6. EXAMINATIONS, ADMIT CARDS & RESULTS (PROTECTED FK) ────────────────────
class Exam(models.Model):
    title         = models.CharField(max_length=150)
    exam_type     = models.CharField(max_length=20, choices=EXAM_TYPE, default='Final')
    academic_year = models.IntegerField(default=date.today().year, db_index=True)
    start_date    = models.DateField()
    end_date      = models.DateField()
    instructions  = models.TextField(blank=True, default="Students must arrive 15 minutes before exam start time with Admit Card and ID Card.")
    is_active     = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return f"{self.title} ({self.academic_year})"


class ExamSchedule(models.Model):
    exam          = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedules')
    student_class = models.CharField(max_length=10, choices=CLASS_CHOICES, db_index=True)
    subject       = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_date     = models.DateField(db_index=True)
    start_time    = models.TimeField()
    end_time      = models.TimeField()
    room_no       = models.CharField(max_length=30, default='Exam Hall 1')

    class Meta:
        ordering = ['exam_date', 'start_time']

    def __str__(self):
        return f"{self.exam.title} - {self.subject.name} (Class {self.student_class})"


class Result(models.Model):
    exam          = models.ForeignKey(Exam, on_delete=models.SET_NULL, null=True, blank=True)
    # Protected against accidental student deletion destroying official historical transcripts
    student       = models.ForeignKey(Student, on_delete=models.PROTECT)
    subject       = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type     = models.CharField(max_length=15, choices=EXAM_TYPE, default='Final', db_index=True)
    year          = models.IntegerField(default=date.today().year, db_index=True)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_marks     = models.IntegerField(default=100)
    grade         = models.CharField(max_length=5, blank=True, db_index=True)
    gpa           = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    teacher_remarks = models.CharField(max_length=250, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'subject', 'exam_type', 'year']
        ordering = ['subject__name']

    def __str__(self):
        return f"{self.student.name} - {self.subject.name}: {self.marks_obtained}/{self.max_marks}"

    def percentage(self):
        if self.max_marks > 0:
            return round((self.marks_obtained / self.max_marks) * 100, 2)
        return Decimal('0.00')

    def calculate_grade_and_gpa(self):
        pct = self.percentage()
        if pct >= 90:
            return 'A+', Decimal('4.00')
        elif pct >= 80:
            return 'A', Decimal('3.70')
        elif pct >= 70:
            return 'B', Decimal('3.00')
        elif pct >= 60:
            return 'C', Decimal('2.00')
        elif pct >= 50:
            return 'D', Decimal('1.00')
        else:
            return 'F', Decimal('0.00')

    def save(self, *args, **kwargs):
        self.grade, self.gpa = self.calculate_grade_and_gpa()
        super().save(*args, **kwargs)


# ─── 7. ATTENDANCE & LEAVE MANAGEMENT ─────────────────────────────────────────
class StudentAttendance(models.Model):
    student    = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date       = models.DateField(default=date.today, db_index=True)
    status     = models.CharField(max_length=15, choices=ATTENDANCE_STATUS, default='Present', db_index=True)
    remarks    = models.CharField(max_length=150, blank=True)

    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date', 'student__roll_no']

    def __str__(self):
        return f"{self.student.name} - {self.date}: {self.status}"


class StaffAttendance(models.Model):
    staff      = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='attendance_records')
    date       = models.DateField(default=date.today, db_index=True)
    status     = models.CharField(max_length=15, choices=ATTENDANCE_STATUS, default='Present', db_index=True)
    in_time    = models.TimeField(null=True, blank=True)
    out_time   = models.TimeField(null=True, blank=True)
    remarks    = models.CharField(max_length=150, blank=True)

    class Meta:
        unique_together = ['staff', 'date']
        ordering = ['-date', 'staff__emp_id']

    def __str__(self):
        return f"{self.staff.name} - {self.date}: {self.status}"


class LeaveApplication(models.Model):
    APPLICANT_TYPE = [('Student', 'Student'), ('Staff', 'Staff')]
    LEAVE_STATUS = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    LEAVE_TYPE = [('Sick', 'Sick Leave'), ('Casual', 'Casual Leave'), ('Emergency', 'Emergency Leave'), ('Maternity', 'Maternity Leave')]

    applicant_type = models.CharField(max_length=10, choices=APPLICANT_TYPE, default='Student', db_index=True)
    student        = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    staff          = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    leave_type     = models.CharField(max_length=20, choices=LEAVE_TYPE, default='Sick')
    from_date      = models.DateField(db_index=True)
    to_date        = models.DateField(db_index=True)
    reason         = models.TextField()
    status         = models.CharField(max_length=15, choices=LEAVE_STATUS, default='Pending', db_index=True)
    admin_remarks  = models.CharField(max_length=250, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def total_days(self):
        if self.to_date and self.from_date:
            return (self.to_date - self.from_date).days + 1
        return 1


class SMSAlertLog(models.Model):
    student      = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    recipient    = models.CharField(max_length=30)
    alert_type   = models.CharField(max_length=30, default='Attendance Alert')
    message      = models.TextField()
    sent_at      = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(max_length=20, default='Sent (Simulated)')

    class Meta:
        ordering = ['-sent_at']


# ─── 8. STAFF PAYROLL & HR (PROTECTED FK) ────────────────────────────────────
class Payroll(models.Model):
    PAYROLL_STATUS = [('Generated', 'Generated'), ('Paid', 'Paid'), ('Hold', 'On Hold')]

    # Protected against accidental deletion of staff profile destroying financial tax/salary records
    staff              = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name='payrolls')
    month              = models.CharField(max_length=15, choices=MONTH_CHOICES, db_index=True)
    year               = models.IntegerField(default=date.today().year, db_index=True)
    basic_salary       = models.DecimalField(max_digits=10, decimal_places=2)
    allowance          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus              = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_deduction  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary         = models.DecimalField(max_digits=10, decimal_places=2)
    status             = models.CharField(max_length=15, choices=PAYROLL_STATUS, default='Generated', db_index=True)
    payment_date       = models.DateField(null=True, blank=True)
    payment_mode       = models.CharField(max_length=30, default='Bank Transfer')
    remarks            = models.TextField(blank=True)
    created_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['staff', 'month', 'year']
        ordering = ['-year', '-id']

    def __str__(self):
        return f"{self.staff.name} - {self.month} {self.year}: Net PKR {self.net_salary}"

    def calculate_net(self):
        gross = self.basic_salary + self.allowance + self.bonus
        total_ded = self.deductions + self.advance_deduction
        return max(Decimal('0.00'), gross - total_ded)

    def save(self, *args, **kwargs):
        self.net_salary = self.calculate_net()
        super().save(*args, **kwargs)


# ─── 9. LIBRARY MANAGEMENT ───────────────────────────────────────────────────
class Book(models.Model):
    title            = models.CharField(max_length=200)
    author           = models.CharField(max_length=150)
    isbn             = models.CharField(max_length=30, unique=True, db_index=True)
    category         = models.CharField(max_length=80, default='General Science', db_index=True)
    rack_number      = models.CharField(max_length=30, blank=True, default='R-101')
    total_copies     = models.PositiveIntegerField(default=5)
    available_copies = models.PositiveIntegerField(default=5)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"


class BookIssue(models.Model):
    ISSUE_STATUS = [('Issued', 'Issued'), ('Returned', 'Returned'), ('Overdue', 'Overdue')]

    book         = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='issue_records')
    borrower_type = models.CharField(max_length=10, choices=[('Student','Student'), ('Staff','Staff')], default='Student')
    student      = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    staff        = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    issue_date   = models.DateField(default=date.today)
    due_date     = models.DateField(db_index=True)
    return_date  = models.DateField(null=True, blank=True)
    fine_amount  = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status       = models.CharField(max_length=15, choices=ISSUE_STATUS, default='Issued', db_index=True)
    remarks      = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-issue_date']

    def calculate_fine(self):
        if not self.return_date and date.today() > self.due_date:
            days = (date.today() - self.due_date).days
            return Decimal(days * 10)  # PKR 10 per overdue day
        elif self.return_date and self.return_date > self.due_date:
            days = (self.return_date - self.due_date).days
            return Decimal(days * 10)
        return Decimal('0.00')


# ─── 10. INVENTORY & ASSET MANAGEMENT ────────────────────────────────────────
class Asset(models.Model):
    CONDITION_CHOICES = [
        ('Good', 'Good / Operational'),
        ('Fair', 'Fair / Minor Wear'),
        ('Needs Repair', 'Needs Repair'),
        ('Discarded', 'Discarded / Scrapped'),
    ]
    CATEGORY_CHOICES = [
        ('Computers', 'Computer & IT Hardware'),
        ('Laboratory', 'Science & Lab Equipment'),
        ('Furniture', 'Desks, Chairs & Furniture'),
        ('AudioVisual', 'Projectors, Smart Boards & AV'),
        ('Sports', 'Sports Equipment'),
        ('Electrical', 'Fans, ACs & Electrical'),
    ]

    item_name       = models.CharField(max_length=150)
    asset_code      = models.CharField(max_length=30, unique=True, db_index=True)
    category        = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='Computers', db_index=True)
    location_room   = models.CharField(max_length=80, default='Computer Lab 1')
    purchase_date   = models.DateField(default=date.today)
    purchase_cost   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    condition       = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='Good', db_index=True)
    remarks         = models.TextField(blank=True)

    class Meta:
        ordering = ['asset_code']

    def __str__(self):
        return f"{self.item_name} [{self.asset_code}] - {self.location_room}"


class StockItem(models.Model):
    name               = models.CharField(max_length=120)
    category           = models.CharField(max_length=80, default='Stationery', db_index=True)
    unit               = models.CharField(max_length=30, default='Pcs', help_text="e.g. Boxes, Pcs, Reams")
    quantity           = models.PositiveIntegerField(default=0)
    min_alert_quantity = models.PositiveIntegerField(default=10)
    unit_price         = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ['name']

    def is_low_stock(self):
        return self.quantity <= self.min_alert_quantity


# ─── 11. CERTIFICATES & OFFICIAL DOCUMENTS (PROTECTED FK) ─────────────────────
class Certificate(models.Model):
    CERTIFICATE_TYPES = [
        ('Leaving_TC', 'School Leaving / Transfer Certificate (TC)'),
        ('Character', 'Character & Conduct Certificate'),
        ('Bonafide', 'Bonafide / Student Status Certificate'),
        ('Merit', 'Academic Merit Certificate'),
    ]

    certificate_type  = models.CharField(max_length=25, choices=CERTIFICATE_TYPES, default='Leaving_TC', db_index=True)
    certificate_no    = models.CharField(max_length=40, unique=True, db_index=True)
    # Protected against accidental student deletion destroying official legal credential logs
    student           = models.ForeignKey(Student, on_delete=models.PROTECT)
    issue_date        = models.DateField(default=date.today, db_index=True)
    reason_for_leaving = models.CharField(max_length=200, blank=True, default='Completed Academic Session / Parent Relocation')
    conduct_remarks   = models.CharField(max_length=200, default='Exemplary moral character and diligent student.')
    session           = models.CharField(max_length=30, default='2025-2026')
    is_issued         = models.BooleanField(default=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.get_certificate_type_display()} - {self.student.name} ({self.certificate_no})"


# ─── 12. HOMEWORK & DIGITAL NOTICE BOARD ──────────────────────────────────────
class Homework(models.Model):
    student_class = models.CharField(max_length=10, choices=CLASS_CHOICES, db_index=True)
    section       = models.CharField(max_length=5, choices=SECTION_CHOICES, default='A', db_index=True)
    subject       = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher       = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    title         = models.CharField(max_length=200)
    description   = models.TextField()
    assigned_date = models.DateField(default=date.today, db_index=True)
    due_date      = models.DateField(db_index=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-assigned_date']

    def __str__(self):
        return f"Class {self.student_class}-{self.section}: {self.subject.name} - {self.title}"


class Notice(models.Model):
    TARGET_AUDIENCE = [('All', 'Everyone'), ('Teachers', 'Staff & Teachers'), ('Students', 'Students & Parents')]
    CATEGORY_CHOICES = [('Academic', 'Academic'), ('Event', 'School Event'), ('Holiday', 'Holiday Announcement'), ('Emergency', 'Urgent Notice'), ('Fee', 'Fee Notification')]

    title           = models.CharField(max_length=200)
    category        = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Academic', db_index=True)
    target_audience = models.CharField(max_length=15, choices=TARGET_AUDIENCE, default='All', db_index=True)
    content         = models.TextField()
    publish_date    = models.DateField(default=date.today, db_index=True)
    is_pinned       = models.BooleanField(default=False, db_index=True)
    is_active       = models.BooleanField(default=True, db_index=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-publish_date', '-created_at']

    def __str__(self):
        return f"[{self.category}] {self.title}"


# ─── 13. TIMETABLE & CLASS SCHEDULE ──────────────────────────────────────────
class Timetable(models.Model):
    student_class = models.CharField(max_length=10, choices=CLASS_CHOICES, db_index=True)
    section       = models.CharField(max_length=5, choices=SECTION_CHOICES, default='A', db_index=True)
    day           = models.CharField(max_length=15, choices=DAYS_OF_WEEK, db_index=True)
    period_number = models.PositiveSmallIntegerField(default=1)
    start_time    = models.TimeField()
    end_time      = models.TimeField()
    subject       = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher       = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    room_number   = models.CharField(max_length=30, default='Room 101')

    class Meta:
        unique_together = [
            ['student_class', 'section', 'day', 'period_number'],
            ['teacher', 'day', 'period_number'],
        ]
        ordering = ['day', 'period_number']

    def __str__(self):
        return f"Class {self.student_class}-{self.section} | {self.day} Period {self.period_number}: {self.subject.name}"


# ─── 14. NOTIFICATION MODEL ───────────────────────────────────────────────────
class Notification(models.Model):
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ─── AUTO-TIMETABLE GENERATOR & SIGNALS ───────────────────────────────────────
from django.db.models.signals import post_save
from django.dispatch import receiver

DEFAULT_PERIOD_TIMINGS = {
    1: ("08:00", "08:45"),
    2: ("08:45", "09:30"),
    3: ("09:30", "10:15"),
    4: ("10:15", "11:00"),
    5: ("11:30", "12:15"),
    6: ("12:15", "13:00"),
    7: ("13:00", "13:40"),
    8: ("13:40", "14:20"),
}

def auto_generate_timetable_for_subject(subject):
    """
    Automatically creates timetable period slots for a subject across weekdays (Mon-Fri)
    avoiding period collisions for class and teacher.
    """
    if not subject.student_class:
        return []

    target_class = subject.student_class
    sections = ['A']
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    created_slots = []

    for sec in sections:
        for day in weekdays:
            # Check if this subject already has a period on this day
            if Timetable.objects.filter(student_class=target_class, section=sec, day=day, subject=subject).exists():
                continue

            # Find first free period (1 to 8) for the class
            assigned = False
            for p_num in range(1, 9):
                class_busy = Timetable.objects.filter(
                    student_class=target_class, section=sec, day=day, period_number=p_num
                ).exists()
                if class_busy:
                    continue

                assigned_teacher = subject.teacher
                if assigned_teacher:
                    teacher_busy = Timetable.objects.filter(
                        teacher=assigned_teacher, day=day, period_number=p_num
                    ).exists()
                    if teacher_busy:
                        # Don't let teacher clash block period creation
                        assigned_teacher = None

                start_s, end_s = DEFAULT_PERIOD_TIMINGS.get(p_num, ("08:00", "08:45"))
                start_t = datetime.strptime(start_s, "%H:%M").time()
                end_t = datetime.strptime(end_s, "%H:%M").time()

                slot = Timetable.objects.create(
                    student_class=target_class,
                    section=sec,
                    day=day,
                    period_number=p_num,
                    start_time=start_t,
                    end_time=end_t,
                    subject=subject,
                    teacher=assigned_teacher,
                    room_number=f"Room {target_class}"
                )
                created_slots.append(slot)
                assigned = True
                break

    return created_slots


@receiver(post_save, sender=Subject)
def subject_auto_timetable_receiver(sender, instance, created, **kwargs):
    if created:
        auto_generate_timetable_for_subject(instance)


@receiver(post_save, sender=Student)
def student_auto_user_account_receiver(sender, instance, created, **kwargs):
    """
    Guarantees every Student has a linked Django User account upon creation.
    Default password: '12345678' (securely hashed via set_password).
    """
    if created or not instance.user:
        clean_roll = instance.roll_no.strip().lower().replace('/', '-').replace(' ', '')
        username = f"std_{clean_roll}"
        user = User.objects.filter(username=username).first()
        if not user:
            user = User(
                username=username,
                email=instance.email or f"{username}@ittihadmodelschool.edu.pk",
                first_name=instance.name
            )
            user.set_password('12345678')
            user.save()
        if instance.user != user:
            Student.objects.filter(pk=instance.pk).update(user=user)

