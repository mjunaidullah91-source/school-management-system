"""
Enterprise URL Routes for EduManage School Management System.
"""
from django.urls import path
from . import views

urlpatterns = [
    # ── Authentication & Portals ─────────────────────────
    path('',                             views.login_view,               name='home'),
    path('login/',                       views.login_view,               name='login'),
    path('logout/',                      views.logout_view,              name='logout'),
    path('dashboard/',                   views.dashboard,                name='dashboard'),
    path('portal/teacher/',              views.teacher_portal,           name='teacher_portal'),
    path('portal/student/',              views.student_portal,           name='student_portal'),
    path('portal/student/change-password/', views.student_change_password, name='student_change_password'),

    # ── Students (SIS) ───────────────────────────────────
    path('students/',                    views.student_list,             name='student_list'),
    path('students/add/',                views.student_add,              name='student_add'),
    path('students/<int:pk>/',           views.student_detail,           name='student_detail'),
    path('students/<int:pk>/edit/',      views.student_edit,             name='student_edit'),
    path('students/<int:pk>/reset-password/', views.student_reset_password, name='student_reset_password'),
    path('students/<int:pk>/delete/',    views.student_delete,           name='student_delete'),
    path('students/export/excel/',       views.export_students_excel,    name='export_students_excel'),
    path('students/export/id-cards/',    views.student_id_cards_pdf,     name='student_id_cards_pdf'),

    # ── Staff, HR & Payroll ──────────────────────────────
    path('staff/',                       views.staff_list,               name='staff_list'),
    path('staff/add/',                   views.staff_add,                name='staff_add'),
    path('staff/<int:pk>/edit/',         views.staff_edit,               name='staff_edit'),
    path('staff/<int:pk>/delete/',       views.staff_delete,             name='staff_delete'),
    path('staff/export/id-cards/',       views.staff_id_cards_pdf,       name='staff_id_cards_pdf'),
    path('payroll/',                     views.payroll_list,             name='payroll_list'),
    path('payroll/generate/',            views.payroll_generate,         name='payroll_generate'),
    path('payroll/<int:pk>/slip/',       views.payroll_slip_pdf,         name='payroll_slip_pdf'),
    path('payroll/export/excel/',        views.export_payroll_excel,     name='export_payroll_excel'),

    # ── Advanced Fees & Challans ─────────────────────────
    path('fees/',                        views.fee_list,                 name='fee_list'),
    path('fees/add/',                    views.fee_add,                  name='fee_add'),
    path('fees/bulk-generate/',          views.bulk_voucher_generate,    name='bulk_voucher_generate'),
    path('fees/<int:pk>/edit/',          views.fee_edit,                 name='fee_edit'),
    path('fees/<int:pk>/delete/',        views.fee_delete,               name='fee_delete'),
    path('fees/<int:pk>/voucher-pdf/',   views.fee_voucher_pdf,          name='fee_voucher_pdf'),
    path('fees/bulk-class-pdf/',         views.bulk_class_vouchers_pdf,  name='bulk_class_vouchers_pdf'),
    path('fees/<int:pk>/sms-reminder/',  views.fee_reminder_sms,         name='fee_reminder_sms'),
    path('fees/student/<int:student_id>/', views.student_fee_detail,     name='student_fee_detail'),
    path('fees/export/excel/',           views.export_fees_excel,        name='export_fees_excel'),

    # ── Subjects & Curriculum ────────────────────────────
    path('subjects/',                    views.subject_list,             name='subject_list'),
    path('subjects/add/',                views.subject_add,              name='subject_add'),
    path('subjects/<int:pk>/edit/',      views.subject_edit,             name='subject_edit'),
    path('subjects/<int:pk>/delete/',    views.subject_delete,           name='subject_delete'),

    # ── Exams, Admit Cards & Results ─────────────────────
    path('exams/',                       views.exam_list,                name='exam_list'),
    path('exams/add/',                   views.exam_add,                 name='exam_add'),
    path('exams/<int:pk>/edit/',         views.exam_edit,                name='exam_edit'),
    path('exams/<int:exam_id>/schedules/', views.exam_schedule_list,     name='exam_schedule_list'),
    path('exams/<int:exam_id>/schedules/add/', views.exam_schedule_add,  name='exam_schedule_add'),
    path('exams/<int:exam_id>/admit-card/<int:student_id>/', views.exam_admit_card_pdf, name='exam_admit_card_pdf'),
    
    path('results/',                     views.result_list,              name='result_list'),
    path('results/add/',                 views.result_add,               name='result_add'),
    path('results/<int:pk>/edit/',       views.result_edit,              name='result_edit'),
    path('results/<int:pk>/delete/',     views.result_delete,            name='result_delete'),
    path('results/student/<int:student_id>/', views.student_result_detail, name='student_result_detail'),
    path('results/student/<int:student_id>/pdf/', views.result_pdf,      name='result_pdf'),
    path('results/bulk-class-pdf/',      views.bulk_result_cards_pdf,    name='bulk_result_cards_pdf'),
    path('results/merit-list/',          views.merit_list_view,          name='merit_list_view'),

    # ── Attendance & Leaves ──────────────────────────────
    path('attendance/students/',         views.student_attendance_view,  name='student_attendance'),
    path('attendance/staff/',            views.staff_attendance_view,    name='staff_attendance'),
    path('leaves/',                      views.leave_list,               name='leave_list'),
    path('leaves/apply/',                views.leave_apply,              name='leave_apply'),
    path('leaves/<int:pk>/<str:status>/', views.leave_status_update,     name='leave_status_update'),
    path('sms-logs/',                    views.sms_log_view,             name='sms_logs'),

    # ── Library Management ───────────────────────────────
    path('library/books/',               views.book_list,                name='book_list'),
    path('library/books/add/',           views.book_add,                 name='book_add'),
    path('library/issues/',              views.book_issue_list,          name='book_issue_list'),
    path('library/issues/add/',          views.book_issue_add,           name='book_issue_add'),
    path('library/issues/<int:pk>/return/', views.book_return_action,    name='book_return_action'),

    # ── Inventory & Assets ───────────────────────────────
    path('inventory/assets/',            views.asset_list,               name='asset_list'),
    path('inventory/assets/add/',        views.asset_add,                name='asset_add'),
    path('inventory/stock/add/',         views.stock_add,                name='stock_add'),

    # ── Certificates ─────────────────────────────────────
    path('certificates/',                views.certificate_list,         name='certificate_list'),
    path('certificates/add/',            views.certificate_add,          name='certificate_add'),
    path('certificates/<int:pk>/pdf/',   views.certificate_pdf,          name='certificate_pdf'),

    # ── Homework & Digital Notices ───────────────────────
    path('homework/',                    views.homework_list,            name='homework_list'),
    path('homework/add/',                views.homework_add,             name='homework_add'),
    path('notices/',                     views.notice_list,              name='notice_list'),
    path('notices/add/',                 views.notice_add,               name='notice_add'),

    # ── Timetable ────────────────────────────────────────
    path('timetable/',                   views.timetable_list,           name='timetable_list'),
    path('timetable/add/',               views.timetable_add,            name='timetable_add'),
    path('timetable/<int:pk>/edit/',     views.timetable_edit,           name='timetable_edit'),
    path('timetable/<int:pk>/delete/',   views.timetable_delete,         name='timetable_delete'),
    path('timetable/shift-ajax/',        views.timetable_shift_ajax,      name='timetable_shift_ajax'),
    path('timetable/auto-generate/',     views.timetable_auto_generate_all, name='timetable_auto_generate_all'),

    # ── Settings & Notifications ─────────────────────────
    path('settings/school/',             views.school_settings_view,     name='school_settings_view'),
    path('notifications/',               views.notifications,            name='notifications'),
    path('notifications/mark-read/',     views.mark_notifications_read,  name='mark_notifications_read'),

    # ── API ──────────────────────────────────────────────
    path('api/dashboard-stats/',         views.dashboard_stats_api,      name='dashboard_stats_api'),
]
