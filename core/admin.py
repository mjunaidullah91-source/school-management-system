"""Django Admin configuration for EduManage School Management."""
from django.contrib import admin
from .models import (
    SchoolSetting, Staff, Student, Subject, Fee, Exam, ExamSchedule,
    Result, StudentAttendance, StaffAttendance, LeaveApplication,
    SMSAlertLog, Payroll, Book, BookIssue, Asset, StockItem,
    Certificate, Homework, Notice, Timetable, Notification
)


@admin.register(SchoolSetting)
class SchoolSettingAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'registration_no', 'contact_phone', 'email', 'principal_name']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['emp_id', 'name', 'designation', 'department', 'contact', 'basic_salary', 'is_active']
    list_filter = ['department', 'gender', 'is_active']
    search_fields = ['name', 'emp_id', 'contact', 'cnic_or_nid']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ['roll_no', 'name', 'student_class', 'section', 'contact', 'monthly_fee', 'concession_percent', 'is_active']
    list_filter   = ['student_class', 'section', 'gender', 'blood_group', 'is_active']
    search_fields = ['name', 'roll_no', 'admission_no', 'father_name', 'contact']
    ordering      = ['student_class', 'section', 'roll_no']


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display  = ['voucher_no', 'student', 'fee_type', 'month', 'year', 'amount', 'paid_amount', 'status']
    list_filter   = ['status', 'fee_type', 'year', 'month']
    search_fields = ['voucher_no', 'student__name', 'student__roll_no']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ['name', 'code', 'student_class', 'max_marks', 'passing_marks', 'teacher']
    list_filter   = ['student_class']
    search_fields = ['name', 'code']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'exam_type', 'academic_year', 'start_date', 'end_date', 'is_active']
    list_filter = ['exam_type', 'academic_year', 'is_active']


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ['exam', 'student_class', 'subject', 'exam_date', 'start_time', 'end_time', 'room_no']
    list_filter = ['student_class', 'exam']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display  = ['student', 'subject', 'exam_type', 'year', 'marks_obtained', 'max_marks', 'grade', 'gpa']
    list_filter   = ['exam_type', 'year', 'grade']
    search_fields = ['student__name', 'student__roll_no', 'subject__name']


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'remarks']
    list_filter = ['status', 'date', 'student__student_class']
    search_fields = ['student__name', 'student__roll_no']


@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'status', 'in_time', 'out_time']
    list_filter = ['status', 'date', 'staff__department']
    search_fields = ['staff__name', 'staff__emp_id']


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant_type', 'student', 'staff', 'leave_type', 'from_date', 'to_date', 'status']
    list_filter = ['applicant_type', 'status', 'leave_type']


@admin.register(SMSAlertLog)
class SMSAlertLogAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'alert_type', 'sent_at', 'status']
    list_filter = ['alert_type', 'status']
    search_fields = ['recipient', 'message']


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['staff', 'month', 'year', 'basic_salary', 'net_salary', 'status', 'payment_date']
    list_filter = ['status', 'year', 'month']
    search_fields = ['staff__name', 'staff__emp_id']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'total_copies', 'available_copies']
    search_fields = ['title', 'author', 'isbn']


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ['book', 'borrower_type', 'student', 'staff', 'issue_date', 'due_date', 'status', 'fine_amount']
    list_filter = ['status', 'borrower_type']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'asset_code', 'category', 'location_room', 'condition', 'purchase_cost']
    list_filter = ['category', 'condition']


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'min_alert_quantity', 'unit', 'unit_price']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_no', 'certificate_type', 'student', 'issue_date', 'is_issued']
    list_filter = ['certificate_type', 'is_issued']


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'student_class', 'section', 'subject', 'teacher', 'assigned_date', 'due_date']
    list_filter = ['student_class', 'section']


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'target_audience', 'publish_date', 'is_pinned', 'is_active']
    list_filter = ['category', 'target_audience', 'is_pinned', 'is_active']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['student_class', 'section', 'day', 'period_number', 'subject', 'teacher', 'room_number']
    list_filter = ['student_class', 'section', 'day']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_read', 'created_at']
