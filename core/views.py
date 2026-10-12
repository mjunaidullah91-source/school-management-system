"""
Enterprise Views for EduManage School Management System.
Handles all business logic, role-based portals, document generators, and data exports.

Optimized with:
- select_related() & prefetch_related() to eliminate N+1 query bottlenecks
- transaction.atomic() for all bulk inserts/updates
- Secure parameter parsing and object retrieval (get_object_or_404)
"""
import io
import json
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Sum, Count, Q, F, Avg
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    Student, Staff, Subject, Fee, Exam, ExamSchedule, Result,
    StudentAttendance, StaffAttendance, LeaveApplication, SMSAlertLog,
    Payroll, Book, BookIssue, Asset, StockItem, Certificate,
    Homework, Notice, Timetable, SchoolSetting, Notification,
    CLASS_CHOICES, SECTION_CHOICES, MONTH_CHOICES, EXAM_TYPE
)
from .forms import (
    StudentForm, StudentSearchForm, StaffForm, PayrollForm,
    FeeForm, BulkVoucherForm, SubjectForm, ExamForm, ExamScheduleForm,
    ResultForm, LeaveApplicationForm, BookForm, BookIssueForm,
    AssetForm, StockItemForm, CertificateForm, HomeworkForm,
    NoticeForm, TimetableForm, SchoolSettingForm
)
from .pdf_utils import (
    generate_fee_voucher_pdf, generate_result_card_pdf, generate_bulk_result_cards_pdf,
    generate_admit_card_pdf, generate_id_cards_pdf, generate_certificate_pdf,
    generate_salary_slip_pdf
)
from .excel_utils import (
    export_students_excel_sheet, export_fees_excel_sheet,
    export_payroll_excel_sheet, export_merit_list_excel_sheet
)
from functools import wraps
from django.contrib.auth.models import User
from .sms_utils import dispatch_absence_alert, dispatch_fee_reminder


# ═══════════════════════════════════════════════════════════════════════════════
#  SECURITY & ROLE ACCESS DECORATORS
# ═══════════════════════════════════════════════════════════════════════════════
def admin_or_staff_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is an Admin or Staff member.
    If a logged-in student tries to access admin views, they are securely redirected to their student portal.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'student_profile') and not (request.user.is_staff or request.user.is_superuser):
            messages.warning(request, "Access restricted. You have been redirected to your Student Portal.")
            return redirect('student_portal')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def get_or_create_student_user(student):
    """
    Ensures every individual student has a linked Django User account for portal authentication.
    Username format: std_<roll_no> (e.g. std_ims-001)
    Default initial password: '12345678' (securely hashed via set_password)
    """
    if student.user:
        return student.user

    clean_roll = student.roll_no.strip().lower().replace('/', '-').replace(' ', '')
    username = f"std_{clean_roll}"

    user = User.objects.filter(username=username).first()
    if not user:
        user = User(
            username=username,
            email=student.email or f"{username}@ittihadmodelschool.edu.pk",
            first_name=student.name
        )
        user.set_password('12345678')
        user.save()

    student.user = user
    student.save(update_fields=['user'])
    return user


# ═══════════════════════════════════════════════════════════════════════════════
#  1. AUTHENTICATION & ROLE-BASED ROUTING
# ═══════════════════════════════════════════════════════════════════════════════
def login_view(request):
    """Unified login for Admins, Teachers, and Students/Parents."""
    if request.user.is_authenticated:
        if hasattr(request.user, 'student_profile') and not request.user.is_superuser:
            return redirect('student_portal')
        elif hasattr(request.user, 'staff_profile') and not request.user.is_superuser:
            return redirect('teacher_portal')
        return redirect('dashboard')

    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            
            # Check portal routing
            if hasattr(user, 'student_profile') and not user.is_superuser:
                return redirect('student_portal')
            elif hasattr(user, 'staff_profile') and not user.is_superuser:
                return redirect('teacher_portal')
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials. Please verify username and password.")
    
    settings = SchoolSetting.get_settings()
    return render(request, 'core/login.html', {'school_setting': settings})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


# ═══════════════════════════════════════════════════════════════════════════════
#  2. MAIN ADMIN DASHBOARD & LIVE STATS API
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
@admin_or_staff_required
def dashboard(request):
    """Central analytics command center optimized with eager loading."""
    settings = SchoolSetting.get_settings()
    total_students = Student.objects.filter(is_active=True).count()
    total_staff    = Staff.objects.filter(is_active=True).count()
    
    # Financial metrics
    total_collected = Fee.objects.filter(status='Paid').aggregate(t=Sum('paid_amount'))['t'] or Decimal('0.00')
    pending_fees = Fee.objects.filter(status__in=['Unpaid', 'Partial', 'Overdue']).aggregate(
        t=Sum(F('amount') - F('paid_amount')))['t'] or Decimal('0.00')
    pending_count = Fee.objects.filter(status__in=['Unpaid', 'Partial', 'Overdue']).count()
    
    # Attendance for today
    today = date.today()
    att_today_present = StudentAttendance.objects.filter(date=today, status='Present').count()
    att_today_absent  = StudentAttendance.objects.filter(date=today, status='Absent').count()
    att_rate = round((att_today_present / (total_students or 1)) * 100, 1)

    # Class-wise distribution for Doughnut Chart
    class_data = (
        Student.objects.filter(is_active=True)
        .values('student_class')
        .annotate(count=Count('id'))
        .order_by('student_class')
    )

    # Monthly fee collection this year for Bar Chart
    current_year = today.year
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    monthly_fees = []
    for m in months:
        amt = Fee.objects.filter(month=m, year=current_year, status='Paid').aggregate(t=Sum('paid_amount'))['t'] or 0
        monthly_fees.append(float(amt))

    # Overdue fee alerts - select_related prevents student query loop
    overdue_fees = Fee.objects.filter(status__in=['Unpaid', 'Overdue']).select_related('student')[:6]
    recent_students = Student.objects.filter(is_active=True).order_by('-created_at')[:5]
    latest_notices = Notice.objects.filter(is_active=True)[:4]
    unread_notifications = Notification.objects.filter(is_read=False).count()

    context = {
        'school_setting': settings,
        'total_students': total_students,
        'total_staff': total_staff,
        'total_fees_collected': total_collected,
        'pending_fees': pending_fees,
        'pending_fees_count': pending_count,
        'attendance_rate': att_rate,
        'today_absent': att_today_absent,
        'class_data': json.dumps(list(class_data), default=str),
        'monthly_fees': json.dumps(monthly_fees),
        'months_labels': json.dumps(months),
        'overdue_fees': overdue_fees,
        'recent_students': recent_students,
        'latest_notices': latest_notices,
        'unread_notifications': unread_notifications,
        'current_year': current_year,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
@admin_or_staff_required
def dashboard_stats_api(request):
    """Real-time JSON stats for live dashboards."""
    data = {
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_staff': Staff.objects.filter(is_active=True).count(),
        'total_fees_collected': float(Fee.objects.filter(status='Paid').aggregate(t=Sum('paid_amount'))['t'] or 0),
        'pending_fees': float(Fee.objects.filter(status__in=['Unpaid','Partial','Overdue']).aggregate(t=Sum(F('amount') - F('paid_amount')))['t'] or 0),
    }
    return JsonResponse(data)


# ═══════════════════════════════════════════════════════════════════════════════
#  3. TEACHER & STUDENT / PARENT PORTALS
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
def teacher_portal(request):
    """Portal for Teachers: My Classes, Assigned Subjects, Today's Timetable, Homework."""
    staff = getattr(request.user, 'staff_profile', None)
    if not staff and not request.user.is_superuser:
        messages.error(request, "Access restricted to teaching staff.")
        return redirect('dashboard')

    today_name = date.today().strftime('%A')
    my_subjects = Subject.objects.filter(teacher=staff) if staff else Subject.objects.all()[:10]
    today_timetable = Timetable.objects.filter(teacher=staff, day=today_name).select_related('subject').order_by('period_number') if staff else []
    my_homework = Homework.objects.filter(teacher=staff).select_related('subject').order_by('-assigned_date')[:6] if staff else []

    return render(request, 'core/teacher_portal.html', {
        'staff': staff,
        'my_subjects': my_subjects,
        'today_timetable': today_timetable,
        'my_homework': my_homework,
        'today_name': today_name,
    })


@login_required
def student_portal(request):
    """
    Portal for Individual Students/Parents: Fees, Attendance, Results, Homework, Notices.
    Strictly isolated: Individual students can ONLY see their own records.
    """
    if hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
    elif request.user.is_staff or request.user.is_superuser:
        student_id = request.GET.get('student_id')
        if student_id:
            student = get_object_or_404(Student, pk=student_id)
        else:
            student = Student.objects.filter(is_active=True).first()
    else:
        messages.error(request, "No student profile is attached to your account.")
        return redirect('login')

    if not student:
        messages.info(request, "No student record found.")
        return redirect('dashboard')

    fees = Fee.objects.filter(student=student).order_by('-year', '-id')
    results = Result.objects.filter(student=student).select_related('subject', 'exam')
    attendance = StudentAttendance.objects.filter(student=student).order_by('-date')[:25]
    homework = Homework.objects.filter(student_class=student.student_class, section=student.section).select_related('subject', 'teacher').order_by('-assigned_date')[:8]
    notices = Notice.objects.filter(is_active=True).filter(Q(target_audience='All') | Q(target_audience='Students'))[:5]

    return render(request, 'core/student_portal.html', {
        'student': student,
        'fees': fees,
        'results': results,
        'attendance': attendance,
        'homework': homework,
        'notices': notices,
        'paid_total': student.get_total_fees_paid(),
        'due_total': student.get_total_fees_due(),
        'attendance_pct': student.get_attendance_percentage(),
    })


@login_required
def student_change_password(request):
    """
    Secure password change view for students in the Student Portal.
    Allows logged-in students to update their password from default '12345678' to a new password.
    """
    if not hasattr(request.user, 'student_profile') and not request.user.is_superuser:
        messages.error(request, "Access restricted to student accounts.")
        return redirect('dashboard')

    student = getattr(request.user, 'student_profile', None)

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the student logged in
            messages.success(request, "Your password has been successfully updated!")
            return redirect('student_portal')
        else:
            messages.error(request, "Please correct the errors below to update your password.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'core/student_change_password.html', {
        'form': form,
        'student': student,
        'school_setting': SchoolSetting.get_settings(),
    })



# ═══════════════════════════════════════════════════════════════════════════════
#  4. STUDENT MANAGEMENT (SIS)
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
@admin_or_staff_required
def student_list(request):
    form = StudentSearchForm(request.GET or None)
    students = Student.objects.select_related('user').all()

    if form.is_valid():
        q   = form.cleaned_data.get('query', '')
        cls = form.cleaned_data.get('student_class', '')
        sec = form.cleaned_data.get('section', '')
        if q:
            students = students.filter(
                Q(name__icontains=q) | Q(roll_no__icontains=q) |
                Q(father_name__icontains=q) | Q(contact__icontains=q) |
                Q(admission_no__icontains=q)
            )
        if cls:
            students = students.filter(student_class=cls)
        if sec:
            students = students.filter(section=sec)

    return render(request, 'core/student_list.html', {
        'students': students,
        'form': form,
        'total': students.count(),
        'classes': CLASS_CHOICES,
    })


@login_required
@admin_or_staff_required
def student_add(request):
    form = StudentForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        student = form.save()
        # Automatically provision unique user login account for the student
        user_account = get_or_create_student_user(student)
        Notification.objects.create(
            title="New Student Admitted",
            message=f"{student.name} (Roll No: {student.roll_no}) admitted. Portal account: {user_account.username}"
        )
        messages.success(request, f"Student '{student.name}' added successfully! Portal Username: {user_account.username}")
        return redirect('student_detail', pk=student.pk)
    return render(request, 'core/student_form.html', {'form': form, 'title': 'Admit New Student', 'action': 'Add'})


@login_required
@admin_or_staff_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, request.FILES or None, instance=student)
    if form.is_valid():
        student = form.save()
        # Ensure account is linked and synced
        get_or_create_student_user(student)
        messages.success(request, f"Student '{student.name}' updated successfully!")
        return redirect('student_detail', pk=student.pk)
    return render(request, 'core/student_form.html', {'form': form, 'title': 'Edit Student Profile', 'action': 'Update', 'student': student})


@login_required
@admin_or_staff_required
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related('user'), pk=pk)
    fees = Fee.objects.filter(student=student).order_by('-year', '-id')
    results = Result.objects.filter(student=student).select_related('subject', 'exam')
    attendance = StudentAttendance.objects.filter(student=student).order_by('-date')[:30]
    certificates = Certificate.objects.filter(student=student)

    result_groups = {}
    for r in results:
        key = f"{r.exam_type} {r.year}"
        result_groups.setdefault(key, []).append(r)

    context = {
        'student': student,
        'fees': fees,
        'result_groups': result_groups,
        'attendance': attendance,
        'certificates': certificates,
        'paid_total': student.get_total_fees_paid(),
        'due_total': student.get_total_fees_due(),
        'attendance_pct': student.get_attendance_percentage(),
    }
    return render(request, 'core/student_detail.html', context)


@login_required
@admin_or_staff_required
def student_reset_password(request, pk):
    """
    Admin/Principal action to reset a student's portal password back to default '12345678'.
    """
    student = get_object_or_404(Student, pk=pk)
    user = student.user
    if not user:
        user = get_or_create_student_user(student)
    
    user.set_password('12345678')
    user.save()

    messages.success(
        request,
        f"Password for student '{student.name}' (Username: {user.username}) has been successfully reset to default: 12345678"
    )
    return redirect('student_detail', pk=student.pk)



@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        # Check protected foreign key constraints gracefully
        if student.fee_set.exists():
            messages.error(request, f"Cannot delete student '{student.name}' because existing fee/financial records are attached. Archive or clear fees first.")
            return redirect('student_detail', pk=student.pk)
        if student.result_set.exists():
            messages.error(request, f"Cannot delete student '{student.name}' because historical examination transcripts exist.")
            return redirect('student_detail', pk=student.pk)

        name = student.name
        student.delete()
        messages.success(request, f"Student '{name}' has been deleted.")
        return redirect('student_list')
    return render(request, 'core/confirm_delete.html', {'object': student, 'type': 'Student', 'cancel_url': 'student_list'})


@login_required
def export_students_excel(request):
    students = Student.objects.select_related('user').all().order_by('student_class', 'section', 'roll_no')
    buffer = export_students_excel_sheet(students)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Students_Directory.xlsx"'
    return response


@login_required
def student_id_cards_pdf(request):
    """Generates printable ID Cards for selected class or all students."""
    cls = request.GET.get('student_class', '')
    sec = request.GET.get('section', '')
    students = Student.objects.filter(is_active=True)
    if cls:
        students = students.filter(student_class=cls)
    if sec:
        students = students.filter(section=sec)

    if not students.exists():
        messages.warning(request, "No active students found for ID Card printing.")
        return redirect('student_list')

    settings = SchoolSetting.get_settings()
    pdf_buffer = generate_id_cards_pdf(students, card_type='student', school_setting=settings)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Student_ID_Cards.pdf"'
    return response


# ═══════════════════════════════════════════════════════════════════════════════
#  5. STAFF, HR & PAYROLL MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
def staff_list(request):
    dept = request.GET.get('department', '')
    q    = request.GET.get('q', '')
    staff_members = Staff.objects.select_related('user').all()
    if dept:
        staff_members = staff_members.filter(department=dept)
    if q:
        staff_members = staff_members.filter(Q(name__icontains=q) | Q(emp_id__icontains=q) | Q(designation__icontains=q))

    return render(request, 'core/staff_list.html', {
        'staff_members': staff_members,
        'departments': Staff.DEPARTMENT_CHOICES,
        'selected_dept': dept,
        'search_query': q,
    })


@login_required
def staff_add(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        staff = form.save()
        messages.success(request, f"Staff member '{staff.name}' added successfully.")
        return redirect('staff_list')
    return render(request, 'core/staff_form.html', {'form': form, 'title': 'Register Staff Member', 'action': 'Add'})


@login_required
def staff_edit(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    form = StaffForm(request.POST or None, request.FILES or None, instance=staff)
    if form.is_valid():
        form.save()
        messages.success(request, f"Staff member '{staff.name}' updated.")
        return redirect('staff_list')
    return render(request, 'core/staff_form.html', {'form': form, 'title': 'Edit Staff Member', 'action': 'Update', 'staff': staff})


@login_required
def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        if staff.payrolls.exists():
            messages.error(request, f"Cannot delete staff member '{staff.name}' because historical salary records are attached.")
            return redirect('staff_list')
        name = staff.name
        staff.delete()
        messages.success(request, f"Staff '{name}' deleted.")
        return redirect('staff_list')
    return render(request, 'core/confirm_delete.html', {'object': staff, 'type': 'Staff Member', 'cancel_url': 'staff_list'})


@login_required
def staff_id_cards_pdf(request):
    staff_members = Staff.objects.filter(is_active=True)
    if not staff_members.exists():
        messages.warning(request, "No active staff members found.")
        return redirect('staff_list')
    settings = SchoolSetting.get_settings()
    pdf_buffer = generate_id_cards_pdf(staff_members, card_type='staff', school_setting=settings)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Staff_ID_Cards.pdf"'
    return response


@login_required
def payroll_list(request):
    month = request.GET.get('month', '')
    year  = int(request.GET.get('year', date.today().year))
    payrolls = Payroll.objects.select_related('staff').filter(year=year)
    if month:
        payrolls = payrolls.filter(month=month)

    total_net = payrolls.aggregate(t=Sum('net_salary'))['t'] or Decimal('0.00')

    return render(request, 'core/payroll_list.html', {
        'payrolls': payrolls,
        'months': MONTH_CHOICES,
        'selected_month': month,
        'selected_year': year,
        'years': range(2022, date.today().year + 2),
        'total_net': total_net,
    })


@login_required
def payroll_generate(request):
    """Batch generate payroll wrapped in transaction.atomic() for data safety."""
    if request.method == 'POST':
        month = request.POST.get('month')
        year  = int(request.POST.get('year', date.today().year))
        active_staff = Staff.objects.filter(is_active=True)

        created_count = 0
        with transaction.atomic():
            for s in active_staff:
                obj, created = Payroll.objects.get_or_create(
                    staff=s, month=month, year=year,
                    defaults={'basic_salary': s.basic_salary, 'status': 'Generated'}
                )
                if created:
                    created_count += 1

        messages.success(request, f"Generated payroll for {created_count} staff members for {month} {year}.")
        return redirect('payroll_list')
    return render(request, 'core/payroll_generate.html', {'months': MONTH_CHOICES, 'current_year': date.today().year})


@login_required
def payroll_slip_pdf(request, pk):
    payroll = get_object_or_404(Payroll.objects.select_related('staff'), pk=pk)
    settings = SchoolSetting.get_settings()
    pdf_buffer = generate_salary_slip_pdf(payroll, settings)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="SalarySlip_{payroll.staff.emp_id}_{payroll.month}_{payroll.year}.pdf"'
    return response


@login_required
def export_payroll_excel(request):
    payrolls = Payroll.objects.select_related('staff').all()
    buffer = export_payroll_excel_sheet(payrolls)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Staff_Payroll_Register.xlsx"'
    return response


# ═══════════════════════════════════════════════════════════════════════════════
#  6. ADVANCED FEE MANAGEMENT & CHALLAN VOUCHERS
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
def fee_list(request):
    status_filter = request.GET.get('status', '')
    year_filter   = request.GET.get('year', '')
    month_filter  = request.GET.get('month', '')
    search        = request.GET.get('q', '')

    fees = Fee.objects.select_related('student').order_by('-id')
    if status_filter:
        fees = fees.filter(status=status_filter)
    if year_filter:
        fees = fees.filter(year=year_filter)
    if month_filter:
        fees = fees.filter(month=month_filter)
    if search:
        fees = fees.filter(Q(student__name__icontains=search) | Q(student__roll_no__icontains=search) | Q(voucher_no__icontains=search))

    total_collected = fees.filter(status='Paid').aggregate(t=Sum('paid_amount'))['t'] or Decimal('0.00')
    total_pending   = fees.filter(status__in=['Unpaid','Partial','Overdue']).aggregate(t=Sum(F('amount') - F('paid_amount')))['t'] or Decimal('0.00')

    return render(request, 'core/fee_list.html', {
        'fees': fees,
        'status_filter': status_filter,
        'year_filter': year_filter,
        'month_filter': month_filter,
        'search': search,
        'total_collected': total_collected,
        'total_pending': total_pending,
        'months': MONTH_CHOICES,
        'years': range(2022, date.today().year + 2),
    })


@login_required
def fee_add(request):
    initial = {}
    student_id = request.GET.get('student_id')
    if student_id:
        std = get_object_or_404(Student, pk=student_id)
        initial['student'] = std
        initial['tuition_fee'] = std.get_effective_monthly_fee()
        initial['concession'] = std.monthly_fee * (std.concession_percent / Decimal(100))

    form = FeeForm(request.POST or None, initial=initial)
    if form.is_valid():
        fee = form.save()
        messages.success(request, f"Fee Voucher #{fee.voucher_no} generated for {fee.student.name}.")
        return redirect('fee_list')
    return render(request, 'core/fee_form.html', {'form': form, 'title': 'Create Fee Voucher', 'action': 'Create'})


@login_required
def fee_edit(request, pk):
    fee = get_object_or_404(Fee.objects.select_related('student'), pk=pk)
    form = FeeForm(request.POST or None, instance=fee)
    if form.is_valid():
        form.save()
        messages.success(request, f"Fee Voucher #{fee.voucher_no} updated successfully.")
        return redirect('fee_list')
    return render(request, 'core/fee_form.html', {'form': form, 'title': 'Edit Fee Voucher', 'action': 'Update', 'fee': fee})


@login_required
def fee_delete(request, pk):
    fee = get_object_or_404(Fee, pk=pk)
    if request.method == 'POST':
        vch = fee.voucher_no
        fee.delete()
        messages.success(request, f"Fee Voucher #{vch} deleted.")
        return redirect('fee_list')
    return render(request, 'core/confirm_delete.html', {'object': fee, 'type': 'Fee Voucher', 'cancel_url': 'fee_list'})


@login_required
def bulk_voucher_generate(request):
    """Generates monthly fee vouchers inside transaction.atomic() to ensure consistency."""
    form = BulkVoucherForm(request.POST or None)
    if form.is_valid():
        cls = form.cleaned_data['student_class']
        sec = form.cleaned_data['section']
        month = form.cleaned_data['month']
        year  = form.cleaned_data['year']
        due_date = form.cleaned_data['due_date']
        fee_type = form.cleaned_data['fee_type']
        exam_fee = form.cleaned_data['exam_fee'] or Decimal('0.00')
        other_fee = form.cleaned_data['other_fee'] or Decimal('0.00')

        students = Student.objects.filter(is_active=True)
        if cls != 'All':
            students = students.filter(student_class=cls)
        if sec != 'All':
            students = students.filter(section=sec)

        count = 0
        with transaction.atomic():
            for s in students:
                if not Fee.objects.filter(student=s, fee_type=fee_type, month=month, year=year).exists():
                    concession = s.monthly_fee * (s.concession_percent / Decimal(100))
                    Fee.objects.create(
                        student=s,
                        fee_type=fee_type,
                        month=month,
                        year=year,
                        tuition_fee=s.monthly_fee,
                        exam_fee=exam_fee,
                        other_fee=other_fee,
                        concession=concession,
                        amount=max(Decimal('0.00'), (s.monthly_fee + exam_fee + other_fee) - concession),
                        due_date=due_date,
                        status='Unpaid'
                    )
                    count += 1

        messages.success(request, f"Successfully created {count} fee vouchers for {month} {year}!")
        return redirect('fee_list')

    return render(request, 'core/bulk_voucher_form.html', {'form': form, 'title': 'Bulk Fee Voucher Builder'})


@login_required
def fee_voucher_pdf(request, pk):
    """Generates 3-Copy Bank Challan PDF for single voucher."""
    fee = get_object_or_404(Fee.objects.select_related('student'), pk=pk)
    settings = SchoolSetting.get_settings()
    pdf_buffer = generate_fee_voucher_pdf(fee, settings)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Challan_{fee.voucher_no}_{fee.student.roll_no}.pdf"'
    return response


@login_required
def bulk_class_vouchers_pdf(request):
    """Generates a combined multi-page 3-part bank challan PDF for an entire class."""
    cls = request.GET.get('student_class', '')
    sec = request.GET.get('section', '')
    month = request.GET.get('month', '')
    year = int(request.GET.get('year', date.today().year))

    fees = Fee.objects.select_related('student').filter(year=year)
    if month:
        fees = fees.filter(month=month)
    if cls:
        fees = fees.filter(student__student_class=cls)
    if sec:
        fees = fees.filter(student__section=sec)

    if not fees.exists():
        messages.warning(request, "No fee vouchers found matching the specified filters.")
        return redirect('fee_list')

    settings = SchoolSetting.get_settings()
    pdf_buffer = generate_fee_voucher_pdf(list(fees), settings)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Bulk_Challans_Class_{cls or "All"}_{month}_{year}.pdf"'
    return response


@login_required
def fee_reminder_sms(request, pk):
    fee = get_object_or_404(Fee.objects.select_related('student'), pk=pk)
    log = dispatch_fee_reminder(fee)
    messages.success(request, f"Fee reminder alert dispatched to parent of {fee.student.name} ({log.recipient}).")
    return redirect('fee_list')


@login_required
def export_fees_excel(request):
    fees = Fee.objects.select_related('student').all()
    buffer = export_fees_excel_sheet(fees)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Fees_Collection_Ledger.xlsx"'
    return response


@login_required
def student_fee_detail(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    fees = Fee.objects.filter(student=student).order_by('-year', '-id')
    return render(request, 'core/student_fee_detail.html', {
        'student': student,
        'fees': fees,
        'paid': student.get_total_fees_paid(),
        'due': student.get_total_fees_due(),
    })


# ═══════════════════════════════════════════════════════════════════════════════
#  7. EXAMINATIONS, ADMIT CARDS, RESULTS & MERIT RANKINGS
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
def exam_list(request):
    exams = Exam.objects.all().order_by('-academic_year', '-start_date')
    return render(request, 'core/exam_list.html', {'exams': exams})


@login_required
def exam_add(request):
    form = ExamForm(request.POST or None)
    if form.is_valid():
        exam = form.save()
        messages.success(request, f"Exam session '{exam.title}' created.")
        return redirect('exam_list')
    return render(request, 'core/exam_form.html', {'form': form, 'title': 'Create Examination Session', 'action': 'Create'})


@login_required
def exam_edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    form = ExamForm(request.POST or None, instance=exam)
    if form.is_valid():
        form.save()
        messages.success(request, f"Exam '{exam.title}' updated.")
        return redirect('exam_list')
    return render(request, 'core/exam_form.html', {'form': form, 'title': 'Edit Examination Session', 'action': 'Update', 'exam': exam})


@login_required
def exam_schedule_list(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    schedules = exam.schedules.all().select_related('subject')
    return render(request, 'core/exam_schedule_list.html', {'exam': exam, 'schedules': schedules})


@login_required
def exam_schedule_add(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    form = ExamScheduleForm(request.POST or None, initial={'exam': exam})
    if form.is_valid():
        form.save()
        messages.success(request, "Exam timetable slot added.")
        return redirect('exam_schedule_list', exam_id=exam.pk)
    return render(request, 'core/exam_schedule_form.html', {'form': form, 'exam': exam, 'title': 'Add Timetable Slot'})


@login_required
def exam_admit_card_pdf(request, exam_id, student_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    student = get_object_or_404(Student, pk=student_id)
    schedules = ExamSchedule.objects.filter(exam=exam, student_class=student.student_class).select_related('subject')
    settings = SchoolSetting.get_settings()
    pdf_buffer = generate_admit_card_pdf(student, exam, schedules, settings)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="AdmitCard_{student.roll_no}_{exam.academic_year}.pdf"'
    return response


@login_required
def result_list(request):
    student_filter = request.GET.get('student', '')
    exam_filter    = request.GET.get('exam_type', '')
    year_filter    = request.GET.get('year', '')
    class_filter   = request.GET.get('student_class', '')

    results = Result.objects.select_related('student', 'subject', 'exam').order_by('-year', 'student__roll_no')
    if student_filter:
        results = results.filter(student_id=student_filter)
    if exam_filter:
        results = results.filter(exam_type=exam_filter)
    if year_filter:
        results = results.filter(year=year_filter)
    if class_filter:
        results = results.filter(student__student_class=class_filter)

    return render(request, 'core/result_list.html', {
        'results': results,
        'students': Student.objects.filter(is_active=True),
        'classes': CLASS_CHOICES,
        'student_filter': student_filter,
        'exam_filter': exam_filter,
        'year_filter': year_filter,
        'class_filter': class_filter,
        'years': range(2022, date.today().year + 2),
    })


@login_required
def result_add(request):
    form = ResultForm(request.POST or None)
    if form.is_valid():
        res = form.save()
        messages.success(request, f"Result recorded for {res.student.name} ({res.subject.name}).")
        return redirect('result_list')
    return render(request, 'core/result_form.html', {'form': form, 'title': 'Record Subject Result', 'action': 'Save'})


@login_required
def result_edit(request, pk):
    result = get_object_or_404(Result.objects.select_related('student', 'subject'), pk=pk)
    form = ResultForm(request.POST or None, instance=result)
    if form.is_valid():
        form.save()
        messages.success(request, "Result updated.")
        return redirect('result_list')
    return render(request, 'core/result_form.html', {'form': form, 'title': 'Edit Result', 'action': 'Update', 'result': result})


@login_required
def result_delete(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.method == 'POST':
        result.delete()
        messages.success(request, "Result entry removed.")
        return redirect('result_list')
    return render(request, 'core/confirm_delete.html', {'object': result, 'type': 'Result Record', 'cancel_url': 'result_list'})


@login_required
def student_result_detail(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    exam_type = request.GET.get('exam_type', 'Final')
    year      = int(request.GET.get('year', date.today().year))

    results = Result.objects.filter(student=student, exam_type=exam_type, year=year).select_related('subject')

    total_marks    = sum(r.max_marks for r in results)
    obtained_marks = sum(float(r.marks_obtained) for r in results)
    percentage     = round((obtained_marks / total_marks) * 100, 2) if total_marks else 0
    avg_gpa        = round(sum(r.gpa for r in results) / Decimal(len(results)), 2) if results else Decimal('0.00')

    if percentage >= 90:   overall_grade = 'A+'
    elif percentage >= 80: overall_grade = 'A'
    elif percentage >= 70: overall_grade = 'B'
    elif percentage >= 60: overall_grade = 'C'
    elif percentage >= 50: overall_grade = 'D'
    else:                  overall_grade = 'F'

    class_students = Student.objects.filter(student_class=student.student_class, is_active=True)
    rankings = []
    for s in class_students:
        s_res = Result.objects.filter(student=s, exam_type=exam_type, year=year)
        s_tot = sum(r.max_marks for r in s_res)
        s_obt = sum(float(r.marks_obtained) for r in s_res)
        s_pct = round((s_obt / s_tot) * 100, 2) if s_tot else 0
        if s_tot > 0:
            rankings.append({'student': s, 'pct': s_pct})

    rankings.sort(key=lambda x: x['pct'], reverse=True)
    position_text = "—"
    for idx, rk in enumerate(rankings, 1):
        if rk['student'].pk == student.pk:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(idx if idx < 20 else idx % 10, 'th')
            position_text = f"{idx}{suffix} of {len(rankings)}"
            break

    return render(request, 'core/student_result_detail.html', {
        'student': student,
        'results': results,
        'total_marks': total_marks,
        'obtained_marks': obtained_marks,
        'percentage': percentage,
        'avg_gpa': avg_gpa,
        'overall_grade': overall_grade,
        'position_text': position_text,
        'exam_type': exam_type,
        'year': year,
        'years': range(2022, date.today().year + 2),
    })


@login_required
def result_pdf(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    exam_type = request.GET.get('exam_type', 'Final')
    year      = int(request.GET.get('year', date.today().year))
    results   = Result.objects.filter(student=student, exam_type=exam_type, year=year).select_related('subject')

    if not results.exists():
        messages.warning(request, "No examination results found for PDF generation.")
        return redirect('student_result_detail', student_id=student.pk)

    settings = SchoolSetting.get_settings()
    pdf_buffer = generate_result_card_pdf(
        student, exam_type, year, results, settings,
        position_text="1st", attendance_pct=student.get_attendance_percentage()
    )
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="ResultCard_{student.roll_no}_{exam_type}_{year}.pdf"'
    return response


@login_required
def bulk_result_cards_pdf(request):
    """Generates multi-page PDF with Report Cards for every student in a class."""
    cls = request.GET.get('student_class', '1')
    exam_type = request.GET.get('exam_type', 'Final')
    year = int(request.GET.get('year', date.today().year))

    students = Student.objects.filter(student_class=cls, is_active=True)
    students_data = []

    for s in students:
        res = Result.objects.filter(student=s, exam_type=exam_type, year=year).select_related('subject')
        if res.exists():
            students_data.append((s, res, "Merit Card", s.get_attendance_percentage()))

    if not students_data:
        messages.warning(request, f"No exam results found for Class {cls} ({exam_type} {year}).")
        return redirect('result_list')

    settings = SchoolSetting.get_settings()
    pdf_buffer = generate_bulk_result_cards_pdf(students_data, exam_type, year, settings)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Bulk_Result_Cards_Class_{cls}_{exam_type}_{year}.pdf"'
    return response


@login_required
def merit_list_view(request):
    """Calculates 1st, 2nd, 3rd rank and full merit position list per class."""
    cls = request.GET.get('student_class', '10')
    exam_type = request.GET.get('exam_type', 'Final')
    year = int(request.GET.get('year', date.today().year))

    students = Student.objects.filter(student_class=cls, is_active=True)
    merit_data = []

    for s in students:
        res = Result.objects.filter(student=s, exam_type=exam_type, year=year)
        if res.exists():
            tot_max = sum(r.max_marks for r in res)
            tot_obt = sum(float(r.marks_obtained) for r in res)
            pct = round((tot_obt / tot_max) * 100, 2) if tot_max else 0
            cgpa = round(sum(r.gpa for r in res) / Decimal(len(res)), 2)
            grd = 'A+' if pct >= 90 else 'A' if pct >= 80 else 'B' if pct >= 70 else 'C' if pct >= 60 else 'D' if pct >= 50 else 'F'
            merit_data.append({
                'student': s,
                'total_max': tot_max,
                'total_obtained': tot_obt,
                'percentage': pct,
                'cgpa': cgpa,
                'grade': grd,
            })

    merit_data.sort(key=lambda x: x['percentage'], reverse=True)
    for idx, item in enumerate(merit_data, 1):
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(idx if idx < 20 else idx % 10, 'th')
        item['position_text'] = f"{idx}{suffix}"

    if request.GET.get('export') == 'excel':
        buffer = export_merit_list_excel_sheet(merit_data, exam_type, cls)
        response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Merit_List_Class_{cls}_{exam_type}.xlsx"'
        return response

    return render(request, 'core/merit_list.html', {
        'merit_data': merit_data,
        'selected_class': cls,
        'selected_exam': exam_type,
        'selected_year': year,
        'classes': CLASS_CHOICES,
        'exams': EXAM_TYPE,
        'years': range(2022, date.today().year + 2),
    })


# ═══════════════════════════════════════════════════════════════════════════════
#  8. ATTENDANCE & LEAVE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
def student_attendance_view(request):
    """Daily Attendance Mark Interface wrapped in transaction.atomic()."""
    cls = request.GET.get('student_class', '1')
    sec = request.GET.get('section', 'A')
    att_date_str = request.GET.get('date', str(date.today()))
    att_date = datetime.strptime(att_date_str, '%Y-%m-%d').date()

    students = Student.objects.filter(student_class=cls, section=sec, is_active=True)

    if request.method == 'POST':
        saved_count = 0
        absent_count = 0
        with transaction.atomic():
            for s in students:
                status_val = request.POST.get(f"status_{s.pk}", 'Present')
                remarks_val = request.POST.get(f"remarks_{s.pk}", '')
                
                att, created = StudentAttendance.objects.update_or_create(
                    student=s, date=att_date,
                    defaults={'status': status_val, 'remarks': remarks_val}
                )
                saved_count += 1
                if status_val == 'Absent':
                    dispatch_absence_alert(s, att_date)
                    absent_count += 1

        messages.success(request, f"Attendance logged for {saved_count} students! ({absent_count} absence SMS alerts dispatched).")
        return redirect(f"{request.path}?student_class={cls}&section={sec}&date={att_date_str}")

    existing = {a.student_id: a for a in StudentAttendance.objects.filter(date=att_date, student__in=students)}

    return render(request, 'core/student_attendance.html', {
        'students': students,
        'existing': existing,
        'selected_class': cls,
        'selected_section': sec,
        'selected_date': att_date_str,
        'classes': CLASS_CHOICES,
        'sections': SECTION_CHOICES,
        'status_choices': ['Present', 'Absent', 'Late', 'Leave', 'Half Day'],
    })


@login_required
def staff_attendance_view(request):
    att_date_str = request.GET.get('date', str(date.today()))
    att_date = datetime.strptime(att_date_str, '%Y-%m-%d').date()
    staff_members = Staff.objects.filter(is_active=True)

    if request.method == 'POST':
        with transaction.atomic():
            for sm in staff_members:
                status_val = request.POST.get(f"status_{sm.pk}", 'Present')
                remarks_val = request.POST.get(f"remarks_{sm.pk}", '')
                StaffAttendance.objects.update_or_create(
                    staff=sm, date=att_date,
                    defaults={'status': status_val, 'remarks': remarks_val}
                )
        messages.success(request, f"Staff attendance logged for {att_date_str}.")
        return redirect(f"{request.path}?date={att_date_str}")

    existing = {a.staff_id: a for a in StaffAttendance.objects.filter(date=att_date)}
    return render(request, 'core/staff_attendance.html', {
        'staff_members': staff_members,
        'existing': existing,
        'selected_date': att_date_str,
    })


@login_required
def leave_list(request):
    leaves = LeaveApplication.objects.select_related('student', 'staff').all()
    return render(request, 'core/leave_list.html', {'leaves': leaves})


@login_required
def leave_apply(request):
    form = LeaveApplicationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Leave application submitted successfully.")
        return redirect('leave_list')
    return render(request, 'core/leave_form.html', {'form': form, 'title': 'Submit Leave Application'})


@login_required
def leave_status_update(request, pk, status):
    leave = get_object_or_404(LeaveApplication, pk=pk)
    if status in ['Approved', 'Rejected', 'Pending']:
        leave.status = status
        leave.save()
        messages.success(request, f"Leave application marked as {status}.")
    return redirect('leave_list')


@login_required
def sms_log_view(request):
    logs = SMSAlertLog.objects.select_related('student').all()[:100]
    return render(request, 'core/sms_logs.html', {'logs': logs})


# ═══════════════════════════════════════════════════════════════════════════════
#  9. LIBRARY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
def book_list(request):
    q = request.GET.get('q', '')
    books = Book.objects.all()
    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q))
    return render(request, 'core/book_list.html', {'books': books, 'search': q})


@login_required
def book_add(request):
    form = BookForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Book added to library inventory.")
        return redirect('book_list')
    return render(request, 'core/book_form.html', {'form': form, 'title': 'Add New Book'})


@login_required
def book_issue_list(request):
    issues = BookIssue.objects.select_related('book', 'student', 'staff').order_by('-issue_date')
    return render(request, 'core/book_issue_list.html', {'issues': issues})


@login_required
def book_issue_add(request):
    form = BookIssueForm(request.POST or None)
    if form.is_valid():
        with transaction.atomic():
            issue = form.save(commit=False)
            if issue.book.available_copies > 0:
                issue.book.available_copies -= 1
                issue.book.save()
                issue.save()
                messages.success(request, f"Book '{issue.book.title}' issued successfully.")
                return redirect('book_issue_list')
            else:
                messages.error(request, "Selected book is currently out of stock.")
    return render(request, 'core/book_issue_form.html', {'form': form, 'title': 'Issue Book'})


@login_required
def book_return_action(request, pk):
    issue = get_object_or_404(BookIssue.objects.select_related('book'), pk=pk)
    if issue.status == 'Issued':
        with transaction.atomic():
            issue.status = 'Returned'
            issue.return_date = date.today()
            issue.fine_amount = issue.calculate_fine()
            issue.book.available_copies += 1
            issue.book.save()
            issue.save()
            messages.success(request, f"Book marked as returned (Fine: PKR {issue.fine_amount}).")
    return redirect('book_issue_list')


# ═══════════════════════════════════════════════════════════════════════════════
#  10. INVENTORY & ASSET MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
def asset_list(request):
    assets = Asset.objects.all()
    stocks = StockItem.objects.all()
    return render(request, 'core/asset_list.html', {'assets': assets, 'stocks': stocks})


@login_required
def asset_add(request):
    form = AssetForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Asset registered.")
        return redirect('asset_list')
    return render(request, 'core/asset_form.html', {'form': form, 'title': 'Register Asset'})


@login_required
def stock_add(request):
    form = StockItemForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Stock item added.")
        return redirect('asset_list')
    return render(request, 'core/stock_form.html', {'form': form, 'title': 'Add Stock Item'})


# ═══════════════════════════════════════════════════════════════════════════════
#  11. CERTIFICATES & OFFICIAL DOCUMENTS
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
def certificate_list(request):
    certificates = Certificate.objects.select_related('student').all()
    return render(request, 'core/certificate_list.html', {'certificates': certificates})


@login_required
def certificate_add(request):
    initial = {'certificate_no': f"CERT-EDU-{date.today().year}-{Certificate.objects.count() + 101:04d}"}
    form = CertificateForm(request.POST or None, initial=initial)
    if form.is_valid():
        cert = form.save()
        messages.success(request, f"Certificate #{cert.certificate_no} generated!")
        return redirect('certificate_pdf', pk=cert.pk)
    return render(request, 'core/certificate_form.html', {'form': form, 'title': 'Generate Official Certificate'})


@login_required
def certificate_pdf(request, pk):
    cert = get_object_or_404(Certificate.objects.select_related('student'), pk=pk)
    settings = SchoolSetting.get_settings()
    pdf_buffer = generate_certificate_pdf(cert, settings)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Certificate_{cert.certificate_no}_{cert.student.roll_no}.pdf"'
    return response


# ═══════════════════════════════════════════════════════════════════════════════
#  12. HOMEWORK, DIGITAL NOTICES & TIMETABLE
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
def homework_list(request):
    cls = request.GET.get('student_class', '')
    homework_items = Homework.objects.select_related('subject', 'teacher').all()
    if cls:
        homework_items = homework_items.filter(student_class=cls)
    return render(request, 'core/homework_list.html', {'homework_items': homework_items, 'classes': CLASS_CHOICES, 'selected_class': cls})


@login_required
def homework_add(request):
    form = HomeworkForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Homework assigned successfully.")
        return redirect('homework_list')
    return render(request, 'core/homework_form.html', {'form': form, 'title': 'Assign Daily Homework'})


@login_required
def notice_list(request):
    notices = Notice.objects.all()
    return render(request, 'core/notice_list.html', {'notices': notices})


@login_required
def notice_add(request):
    form = NoticeForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Notice published on digital board.")
        return redirect('notice_list')
    return render(request, 'core/notice_form.html', {'form': form, 'title': 'Publish School Notice'})


@login_required
def timetable_list(request):
    cls = request.GET.get('student_class', '10')
    sec = request.GET.get('section', 'A')
    slots = Timetable.objects.filter(student_class=cls, section=sec).select_related('subject', 'teacher')

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    matrix = {d: {} for d in days}
    for s in slots:
        matrix[s.day][s.period_number] = s

    subjects = Subject.objects.filter(Q(student_class=cls) | Q(student_class='')).select_related('teacher').order_by('name')
    if not subjects.exists():
        subjects = Subject.objects.select_related('teacher').all().order_by('name')
    teachers = Staff.objects.filter(department='Academics', is_active=True).order_by('name')
    if not teachers.exists():
        teachers = Staff.objects.filter(is_active=True).order_by('name')

    default_timings = {
        1: ("08:00", "08:45"),
        2: ("08:45", "09:30"),
        3: ("09:30", "10:15"),
        4: ("10:15", "11:00"),
        5: ("11:30", "12:15"),
        6: ("12:15", "13:00"),
        7: ("13:00", "13:40"),
        8: ("13:40", "14:20"),
    }

    return render(request, 'core/timetable_list.html', {
        'matrix': matrix,
        'days': days,
        'periods': range(1, 9),
        'selected_class': cls,
        'selected_section': sec,
        'classes': CLASS_CHOICES,
        'sections': SECTION_CHOICES,
        'class_subjects': subjects,
        'staff_list': teachers,
        'default_timings': default_timings,
        'default_timings_json': json.dumps(default_timings),
    })


@login_required
def timetable_add(request):
    form = TimetableForm(request.POST or None)
    if form.is_valid():
        slot = form.save()
        messages.success(request, f"Period {slot.period_number} for {slot.subject.name} added successfully.")
        return redirect(f"/timetable/?student_class={slot.student_class}&section={slot.section}")
    return render(request, 'core/timetable_form.html', {'form': form, 'title': 'Add Timetable Slot'})


@login_required
def timetable_edit(request, pk):
    slot = get_object_or_404(Timetable.objects.select_related('subject', 'teacher'), pk=pk)
    form = TimetableForm(request.POST or None, instance=slot)
    if form.is_valid():
        form.save()
        messages.success(request, f"Timetable slot for {slot.subject.name} updated successfully.")
        return redirect(f"/timetable/?student_class={slot.student_class}&section={slot.section}")
    return render(request, 'core/timetable_form.html', {'form': form, 'title': 'Edit Timetable Slot', 'slot': slot})


@login_required
def timetable_delete(request, pk):
    slot = get_object_or_404(Timetable, pk=pk)
    cls = slot.student_class
    sec = slot.section
    name = slot.subject.name
    slot.delete()
    messages.success(request, f"Period slot for '{name}' removed from timetable.")
    return redirect(f"/timetable/?student_class={cls}&section={sec}")


@login_required
def timetable_shift_ajax(request):
    """
    Handles interactive shifting/moving of lectures wrapped in transaction.atomic().
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

    try:
        data = request.POST
        if not data and request.body:
            data = json.loads(request.body.decode('utf-8'))

        slot_id = data.get('slot_id')
        action = data.get('action')

        default_timings = {
            1: ("08:00", "08:45"),
            2: ("08:45", "09:30"),
            3: ("09:30", "10:15"),
            4: ("10:15", "11:00"),
            5: ("11:30", "12:15"),
            6: ("12:15", "13:00"),
            7: ("13:00", "13:40"),
            8: ("13:40", "14:20"),
        }

        with transaction.atomic():
            if action == 'shift_period':
                slot = get_object_or_404(Timetable, pk=slot_id)
                direction = int(data.get('direction', 1))
                new_period = slot.period_number + direction
                if new_period < 1 or new_period > 8:
                    return JsonResponse({'success': False, 'error': f'Period must be between 1 and 8 (Current: {slot.period_number})'})

                existing = Timetable.objects.filter(
                    student_class=slot.student_class, section=slot.section, day=slot.day, period_number=new_period
                ).first()

                s_str, e_str = default_timings.get(new_period, ("08:00", "08:45"))
                st = datetime.strptime(s_str, "%H:%M").time()
                et = datetime.strptime(e_str, "%H:%M").time()

                if existing:
                    old_period = slot.period_number
                    old_s_str, old_e_str = default_timings.get(old_period, ("08:00", "08:45"))
                    old_st = datetime.strptime(old_s_str, "%H:%M").time()
                    old_et = datetime.strptime(old_e_str, "%H:%M").time()

                    existing.period_number = 99
                    existing.save()

                    slot.period_number = new_period
                    slot.start_time = st
                    slot.end_time = et
                    slot.save()

                    existing.period_number = old_period
                    existing.start_time = old_st
                    existing.end_time = old_et
                    existing.save()

                    return JsonResponse({
                        'success': True,
                        'message': f"Swapped: {slot.subject.name} ⇄ {existing.subject.name} (Period {new_period})"
                    })
                else:
                    slot.period_number = new_period
                    slot.start_time = st
                    slot.end_time = et
                    slot.save()
                    return JsonResponse({
                        'success': True,
                        'message': f"{slot.subject.name} shifted to Period {new_period} ({s_str} - {e_str})"
                    })

            elif action == 'quick_update':
                slot = get_object_or_404(Timetable, pk=slot_id)
                new_day = data.get('day', slot.day)
                new_period = int(data.get('period_number', slot.period_number))
                subject_id = data.get('subject_id')
                teacher_id = data.get('teacher_id')
                room_no = data.get('room_number', slot.room_number)
                start_t_str = data.get('start_time')
                end_t_str = data.get('end_time')

                if subject_id:
                    slot.subject = get_object_or_404(Subject, pk=subject_id)
                if teacher_id:
                    slot.teacher = Staff.objects.filter(pk=teacher_id).first()
                elif teacher_id == '':
                    slot.teacher = None

                if start_t_str:
                    slot.start_time = datetime.strptime(start_t_str[:5], "%H:%M").time()
                if end_t_str:
                    slot.end_time = datetime.strptime(end_t_str[:5], "%H:%M").time()

                if new_day != slot.day or new_period != slot.period_number:
                    clash = Timetable.objects.filter(
                        student_class=slot.student_class, section=slot.section, day=new_day, period_number=new_period
                    ).exclude(pk=slot.pk).first()
                    if clash:
                        clash.period_number = 99
                        clash.save()

                        old_p = slot.period_number
                        slot.day = new_day
                        slot.period_number = new_period
                        slot.room_number = room_no
                        slot.save()

                        clash.day = new_day
                        clash.period_number = old_p
                        clash.save()
                    else:
                        slot.day = new_day
                        slot.period_number = new_period

                slot.room_number = room_no
                slot.save()
                return JsonResponse({'success': True, 'message': f"Lecture '{slot.subject.name}' updated successfully."})

            elif action == 'create_slot':
                cls = data.get('student_class', '10')
                sec = data.get('section', 'A')
                day = data.get('day', 'Monday')
                period_num = int(data.get('period_number', 1))
                subject_id = data.get('subject_id')
                teacher_id = data.get('teacher_id')
                room_no = data.get('room_number', f'Room {cls}')
                start_t_str = data.get('start_time')
                end_t_str = data.get('end_time')

                if not subject_id:
                    return JsonResponse({'success': False, 'error': 'Please select a subject.'})

                subject = get_object_or_404(Subject, pk=subject_id)
                teacher = Staff.objects.filter(pk=teacher_id).first() if teacher_id else subject.teacher

                if not start_t_str or not end_t_str:
                    s_def, e_def = default_timings.get(period_num, ("08:00", "08:45"))
                    st = datetime.strptime(s_def, "%H:%M").time()
                    et = datetime.strptime(e_def, "%H:%M").time()
                else:
                    st = datetime.strptime(start_t_str[:5], "%H:%M").time()
                    et = datetime.strptime(end_t_str[:5], "%H:%M").time()

                existing = Timetable.objects.filter(
                    student_class=cls, section=sec, day=day, period_number=period_num
                ).first()
                if existing:
                    existing.subject = subject
                    existing.teacher = teacher
                    existing.start_time = st
                    existing.end_time = et
                    existing.room_number = room_no
                    existing.save()
                    return JsonResponse({'success': True, 'message': f"Period {period_num} updated with {subject.name}."})
                else:
                    Timetable.objects.create(
                        student_class=cls,
                        section=sec,
                        day=day,
                        period_number=period_num,
                        start_time=st,
                        end_time=et,
                        subject=subject,
                        teacher=teacher,
                        room_number=room_no
                    )
                    return JsonResponse({'success': True, 'message': f"Period {period_num} scheduled for {subject.name}."})

        return JsonResponse({'success': False, 'error': 'Unknown action specified'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def timetable_auto_generate_all(request):
    cls = request.GET.get('student_class', '')
    from .models import auto_generate_timetable_for_subject
    qs = Subject.objects.select_related('teacher').all()
    if cls:
        qs = qs.filter(student_class=cls)
    total_added = 0
    with transaction.atomic():
        for s in qs:
            created = auto_generate_timetable_for_subject(s)
            total_added += len(created)

    messages.success(request, f"Auto-scheduled {total_added} lecture periods for subjects.")
    target_url = f"/timetable/?student_class={cls}" if cls else "/timetable/"
    return redirect(target_url)


# ═══════════════════════════════════════════════════════════════════════════════
#  13. SUBJECTS & CURRICULUM
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
def subject_list(request):
    subjects = Subject.objects.select_related('teacher').all()
    return render(request, 'core/subject_list.html', {'subjects': subjects})


@login_required
def subject_add(request):
    form = SubjectForm(request.POST or None)
    if form.is_valid():
        subj = form.save()
        messages.success(request, f"Subject '{subj.name}' added and automatically scheduled in timetable!")
        return redirect('subject_list')
    return render(request, 'core/subject_form.html', {'form': form, 'title': 'Add Subject', 'action': 'Add'})


@login_required
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(request.POST or None, instance=subject)
    if form.is_valid():
        form.save()
        messages.success(request, "Subject updated.")
        return redirect('subject_list')
    return render(request, 'core/subject_form.html', {'form': form, 'title': 'Edit Subject', 'action': 'Update'})


@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, "Subject deleted.")
        return redirect('subject_list')
    return render(request, 'core/confirm_delete.html', {'object': subject, 'type': 'Subject', 'cancel_url': 'subject_list'})


# ═══════════════════════════════════════════════════════════════════════════════
#  14. SCHOOL SETTINGS & BRANDING
# ═══════════════════════════════════════════════════════════════════════════════
@login_required
def school_settings_view(request):
    settings_obj = SchoolSetting.get_settings()
    form = SchoolSettingForm(request.POST or None, request.FILES or None, instance=settings_obj)
    if form.is_valid():
        form.save()
        messages.success(request, "School profile and system branding settings updated.")
        return redirect('school_settings_view')
    return render(request, 'core/school_settings.html', {'form': form, 'settings': settings_obj})


@login_required
def notifications(request):
    notifs = Notification.objects.all()
    return render(request, 'core/notifications.html', {'notifications': notifs})


@login_required
def mark_notifications_read(request):
    Notification.objects.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications')
