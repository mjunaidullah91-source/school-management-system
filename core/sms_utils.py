"""
Internal Alert & Communication Logger for Ittihad Model School.
Completely standalone and offline without external gateway dependencies.
"""
from datetime import date
from .models import SMSAlertLog, SchoolSetting


def dispatch_absence_alert(student, attendance_date=None):
    """
    Internal audit logger for student absence. Runs completely offline.
    """
    settings = SchoolSetting.get_settings()
    d_str = str(attendance_date or date.today())
    recipient = student.emergency_contact or student.contact or '0300-0000000'

    msg = (
        f"Parent Notification: {student.name} (Roll No: {student.roll_no}, "
        f"Class {student.student_class}-{student.section}) was marked Absent on {d_str}."
    )

    log = SMSAlertLog.objects.create(
        student=student,
        recipient=recipient,
        alert_type="Absence Notice",
        message=msg,
        status="Recorded (Internal)"
    )
    return log


def dispatch_fee_reminder(fee):
    """
    Internal audit logger for fee reminder. Runs completely offline.
    """
    student = fee.student
    recipient = student.emergency_contact or student.contact or '0300-0000000'
    settings = SchoolSetting.get_settings()

    msg = (
        f"Fee Notice: Voucher #{fee.voucher_no} for {student.name} ({fee.month} {fee.year}) "
        f"Balance: PKR {fee.balance():,.2f}. Due Date: {fee.due_date}."
    )

    log = SMSAlertLog.objects.create(
        student=student,
        recipient=recipient,
        alert_type="Fee Reminder",
        message=msg,
        status="Recorded (Internal)"
    )
    return log
