"""
Enterprise Forms for School Management System.
Covers: Students, Staff/HR, Fees & Vouchers, Exams & Results, Attendance,
Leaves, Library, Assets, Certificates, Homework, Notices, Timetable, School Settings.
"""
from django import forms
from .models import (
    Student, Staff, Subject, Fee, Exam, ExamSchedule, Result,
    StudentAttendance, StaffAttendance, LeaveApplication,
    Book, BookIssue, Asset, StockItem, Certificate,
    Homework, Notice, Timetable, SchoolSetting, Payroll,
    CLASS_CHOICES, SECTION_CHOICES, FEE_TYPE, MONTH_CHOICES
)


# ─── 1. SCHOOL SETTINGS FORM ──────────────────────────────────────────────────
class SchoolSettingForm(forms.ModelForm):
    class Meta:
        model = SchoolSetting
        fields = '__all__'
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tagline': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_no': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_title': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_no': forms.TextInput(attrs={'class': 'form-control'}),
            'iban': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_branch': forms.TextInput(attrs={'class': 'form-control'}),
            'currency_symbol': forms.TextInput(attrs={'class': 'form-control'}),
            'late_fee_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'principal_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ─── 2. STUDENT FORMS ─────────────────────────────────────────────────────────
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'roll_no', 'admission_no', 'name', 'father_name', 'father_occupation',
            'mother_name', 'gender', 'blood_group', 'dob', 'student_class',
            'section', 'contact', 'emergency_contact', 'email', 'address',
            'photo', 'admission_date', 'monthly_fee', 'concession_percent',
            'concession_reason', 'is_active'
        ]
        widgets = {
            'roll_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. STD-2026-001'}),
            'admission_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ADM-9801'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's Name"}),
            'father_occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Occupation'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's Name"}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0300-1234567'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Phone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Residential Address'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monthly_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'concession_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0 to 100%'}),
            'concession_reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sibling Concession / Merit'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StudentSearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name, roll no, phone...'}))
    student_class = forms.ChoiceField(required=False, choices=[('', 'All Classes')] + Student._meta.get_field('student_class').choices, widget=forms.Select(attrs={'class': 'form-select'}))
    section = forms.ChoiceField(required=False, choices=[('', 'All Sections')] + Student._meta.get_field('section').choices, widget=forms.Select(attrs={'class': 'form-select'}))


# ─── 3. STAFF & HR FORMS ──────────────────────────────────────────────────────
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            'emp_id', 'name', 'father_or_spouse', 'designation', 'department',
            'qualification', 'gender', 'blood_group', 'dob', 'contact',
            'emergency_contact', 'email', 'cnic_or_nid', 'address', 'photo',
            'joining_date', 'basic_salary', 'is_active'
        ]
        widgets = {
            'emp_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. EMP-101'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee Name'}),
            'father_or_spouse': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Math Teacher'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. M.Sc Mathematics, B.Ed'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0300-XXXXXXX'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cnic_or_nid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXXX-XXXXXXX-X'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['staff', 'month', 'year', 'basic_salary', 'allowance', 'bonus', 'deductions', 'advance_deduction', 'status', 'payment_date', 'payment_mode', 'remarks']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'allowance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'advance_deduction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_mode': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


# ─── 4. FEE & CHALLAN FORMS ───────────────────────────────────────────────────
class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = [
            'student', 'fee_type', 'month', 'year', 'tuition_fee', 'admission_fee',
            'exam_fee', 'other_fee', 'late_fee_fine', 'concession', 'paid_amount',
            'due_date', 'paid_date', 'payment_mode', 'remarks'
        ]
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'fee_type': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'tuition_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'admission_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'exam_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'late_fee_fine': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'concession': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'paid_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class BulkVoucherForm(forms.Form):
    student_class = forms.ChoiceField(choices=[('All', 'All Classes')] + CLASS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    section = forms.ChoiceField(choices=[('All', 'All Sections')] + SECTION_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    fee_type = forms.ChoiceField(choices=FEE_TYPE, initial='Monthly', widget=forms.Select(attrs={'class': 'form-select'}))
    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    year = forms.IntegerField(initial=2026, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    due_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    exam_fee = forms.DecimalField(required=False, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    other_fee = forms.DecimalField(required=False, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control'}))


# ─── 5. SUBJECTS, EXAMS & RESULTS ─────────────────────────────────────────────
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'max_marks', 'passing_marks', 'student_class', 'teacher']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mathematics'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MATH-10'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'exam_type', 'academic_year', 'start_date', 'end_date', 'instructions', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Annual Examination 2026'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExamScheduleForm(forms.ModelForm):
    class Meta:
        model = ExamSchedule
        fields = ['exam', 'student_class', 'subject', 'exam_date', 'start_time', 'end_time', 'room_no']
        widgets = {
            'exam': forms.Select(attrs={'class': 'form-select'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'exam_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Exam Hall / Room'}),
        }


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['exam', 'student', 'subject', 'exam_type', 'year', 'marks_obtained', 'max_marks', 'teacher_remarks']
        widgets = {
            'exam': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'teacher_remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Performance remarks'}),
        }


# ─── 6. ATTENDANCE & LEAVE FORMS ──────────────────────────────────────────────
class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['applicant_type', 'student', 'staff', 'leave_type', 'from_date', 'to_date', 'reason', 'status', 'admin_remarks']
        widgets = {
            'applicant_type': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'from_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_remarks': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ─── 7. LIBRARY FORMS ─────────────────────────────────────────────────────────
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'rack_number': forms.TextInput(attrs={'class': 'form-control'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class BookIssueForm(forms.ModelForm):
    class Meta:
        model = BookIssue
        fields = ['book', 'borrower_type', 'student', 'staff', 'issue_date', 'due_date', 'return_date', 'fine_amount', 'status', 'remarks']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-select'}),
            'borrower_type': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fine_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ─── 8. ASSET & INVENTORY FORMS ───────────────────────────────────────────────
class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = '__all__'
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_code': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location_room': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_alert_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


# ─── 9. CERTIFICATE FORM ──────────────────────────────────────────────────────
class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['certificate_type', 'certificate_no', 'student', 'issue_date', 'session', 'reason_for_leaving', 'conduct_remarks', 'is_issued']
        widgets = {
            'certificate_type': forms.Select(attrs={'class': 'form-select'}),
            'certificate_no': forms.TextInput(attrs={'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'session': forms.TextInput(attrs={'class': 'form-control'}),
            'reason_for_leaving': forms.TextInput(attrs={'class': 'form-control'}),
            'conduct_remarks': forms.TextInput(attrs={'class': 'form-control'}),
            'is_issued': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ─── 10. HOMEWORK, NOTICE & TIMETABLE FORMS ───────────────────────────────────
class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['student_class', 'section', 'subject', 'teacher', 'title', 'description', 'assigned_date', 'due_date']
        widgets = {
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'category', 'target_audience', 'content', 'publish_date', 'is_pinned', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'target_audience': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'publish_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = '__all__'
        widgets = {
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'day': forms.Select(attrs={'class': 'form-select'}),
            'period_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
