import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date
from core.models import Student, Staff, Fee, Result, Exam, Certificate, Payroll, SchoolSetting, Subject
from core.pdf_utils import (
    generate_result_card_pdf,
    generate_bulk_result_cards_pdf,
    generate_admit_card_pdf,
    generate_id_cards_pdf,
    generate_certificate_pdf,
    generate_fee_voucher_pdf,
    generate_salary_slip_pdf,
)

def run_tests():
    print("=" * 70)
    print("1. AUDITING REPORTLAB PDF GENERATION & TYPOGRAPHY SPACING")
    print("=" * 70)

    settings = SchoolSetting.get_settings()
    student = Student.objects.first()
    teacher = Staff.objects.filter(is_active=True).first()
    fee = Fee.objects.first()
    exam = Exam.objects.first()
    results = list(Result.objects.filter(student=student)) if student else []
    cert = Certificate.objects.first()
    
    if not cert and student:
        cert = Certificate.objects.create(
            student=student,
            certificate_type='Leaving_TC',
            certificate_no='TC-TEST-2026',
            issue_date=date.today(),
            session='2025-2026',
            reason_for_leaving='Family relocation',
            conduct_remarks='Exemplary moral conduct and diligence'
        )

    # 1. Result Card Single
    buf_rc = generate_result_card_pdf(
        student=student,
        exam_name=exam.title if exam else "Midterm 2026",
        academic_year="2025-2026",
        results=results,
        school_setting=settings,
        position_text="1st",
        attendance_pct=96.5
    )
    data_rc = buf_rc.getvalue()
    assert data_rc.startswith(b'%PDF'), "Result Card PDF does not start with %PDF"
    print(f"[PASS] Single Result Card PDF generated successfully ({len(data_rc):,} bytes)")

    # 2. Bulk Result Cards
    students_data = [(student, results, "1st", 96.5)]
    buf_bulk_rc = generate_bulk_result_cards_pdf(
        students_result_data=students_data,
        exam_name=exam.title if exam else "Annual 2026",
        academic_year="2025-2026",
        school_setting=settings
    )
    data_bulk_rc = buf_bulk_rc.getvalue()
    assert data_bulk_rc.startswith(b'%PDF'), "Bulk Result Cards PDF does not start with %PDF"
    print(f"[PASS] Bulk Result Cards PDF generated successfully ({len(data_bulk_rc):,} bytes)")

    # 3. Certificates
    buf_cert = generate_certificate_pdf(cert, settings)
    data_cert = buf_cert.getvalue()
    assert data_cert.startswith(b'%PDF'), "Certificate PDF does not start with %PDF"
    print(f"[PASS] Certificate PDF generated successfully ({len(data_cert):,} bytes)")

    # 4. Fee Voucher
    if fee:
        buf_fee = generate_fee_voucher_pdf([fee], settings)
        data_fee = buf_fee.getvalue()
        assert data_fee.startswith(b'%PDF'), "Fee Voucher PDF does not start with %PDF"
        print(f"[PASS] Fee Voucher (3-copy Challan) PDF generated successfully ({len(data_fee):,} bytes)")

    # 5. ID Cards (Student & Staff)
    buf_id = generate_id_cards_pdf([student], card_type='student', school_setting=settings)
    data_id = buf_id.getvalue()
    assert data_id.startswith(b'%PDF'), "Student ID Card PDF does not start with %PDF"
    print(f"[PASS] Student ID Card PDF generated successfully ({len(data_id):,} bytes)")

    buf_staff_id = generate_id_cards_pdf([teacher], card_type='staff', school_setting=settings)
    data_staff_id = buf_staff_id.getvalue()
    assert data_staff_id.startswith(b'%PDF'), "Staff ID Card PDF does not start with %PDF"
    print(f"[PASS] Staff ID Card PDF generated successfully ({len(data_staff_id):,} bytes)")

    # 6. Salary Slip
    payroll, _ = Payroll.objects.get_or_create(
        staff=teacher,
        month='October',
        year=2026,
        defaults={
            'basic_salary': teacher.basic_salary,
            'allowance': Decimal('2500.00'),
            'bonus': Decimal('1000.00'),
            'deductions': Decimal('500.00'),
            'advance_deduction': Decimal('0.00'),
            'net_salary': teacher.basic_salary + Decimal('3000.00'),
            'status': 'Paid',
            'payment_date': date.today(),
            'payment_mode': 'Bank Transfer'
        }
    )
    buf_pay = generate_salary_slip_pdf(payroll, settings)
    data_pay = buf_pay.getvalue()
    assert data_pay.startswith(b'%PDF'), "Salary Slip PDF does not start with %PDF"
    print(f"[PASS] Salary Slip PDF generated successfully ({len(data_pay):,} bytes)")

    print("\n" + "=" * 70)
    print("2. VERIFYING TEACHER SALARY MANAGEMENT ENDPOINTS & ACCESS CONTROL")
    print("=" * 70)

    client = Client()
    admin_user = User.objects.filter(is_superuser=True).first()
    assert admin_user is not None, "Admin user must exist"

    # Login as admin
    client.force_login(admin_user)

    # 1. Access Teacher Salary Desk
    res = client.get('/salaries/teachers/')
    assert res.status_code == 200, f"Expected 200 for teacher_salary_list, got {res.status_code}"
    assert b"Teacher &amp; Faculty Salaries Desk" in res.content or b"Teacher & Faculty Salaries" in res.content
    assert b"Total Assigned Budget" in res.content
    assert b"Total Disbursed (Paid)" in res.content
    assert b"Pending Dues &amp; Balances" in res.content or b"Pending Dues & Balances" in res.content
    print("[PASS] Admin access to /salaries/teachers/ returned 200 with complete financial breakdown")

    # 2. Test status filters
    for st in ['All', 'Paid', 'Partial', 'Unpaid', 'Generated', 'Hold']:
        res_st = client.get(f'/salaries/teachers/?status={st}')
        assert res_st.status_code == 200, f"Filter status={st} failed with {res_st.status_code}"
    print("[PASS] All filter variants (All, Paid, Partial, Unpaid, Generated, Hold) returned 200")

    # 3. Test Teacher Salary Disbursement POST
    disburse_data = {
        'month': 'November',
        'year': '2026',
        'basic_salary': str(teacher.basic_salary),
        'allowance': '4500.00',
        'bonus': '1500.00',
        'deductions': '750.00',
        'advance_deduction': '0.00',
        'payment_mode': 'Habib Bank Transfer',
        'payment_date': str(date.today()),
        'status': 'Paid',
        'remarks': 'Full November Clearance'
    }
    res_disburse = client.post(f'/salaries/teachers/{teacher.pk}/disburse/', disburse_data)
    assert res_disburse.status_code == 302, f"Disburse POST failed, got {res_disburse.status_code}"
    
    # Verify database record
    p_nov = Payroll.objects.get(staff=teacher, month='November', year=2026)
    expected_net = teacher.basic_salary + Decimal('4500.00') + Decimal('1500.00') - Decimal('750.00')
    assert p_nov.status == 'Paid', f"Expected status Paid, got {p_nov.status}"
    assert p_nov.net_salary == expected_net, f"Expected {expected_net}, got {p_nov.net_salary}"
    print(f"[PASS] Salary disbursement recorded successfully: Net PKR {p_nov.net_salary:,.2f} (Status: {p_nov.status})")

    # 4. Test Salary Slip PDF view via HTTP
    res_slip = client.get(f'/salaries/payroll/{p_nov.pk}/slip/')
    assert res_slip.status_code == 200, f"Salary slip PDF returned {res_slip.status_code}"
    assert res_slip['Content-Type'] == 'application/pdf'
    assert res_slip.content.startswith(b'%PDF')
    print(f"[PASS] Salary Slip PDF endpoint returned valid PDF ({len(res_slip.content):,} bytes)")

    # 5. Test Status Update to Partial
    res_partial = client.get(f'/salaries/teachers/{p_nov.pk}/status/Partial/')
    assert res_partial.status_code == 302
    p_nov.refresh_from_db()
    assert p_nov.status == 'Partial', f"Expected Partial, got {p_nov.status}"
    print("[PASS] Status update to 'Partial' succeeded")

    # 6. Test Status Update to Hold
    res_hold = client.get(f'/salaries/teachers/{p_nov.pk}/status/Hold/')
    assert res_hold.status_code == 302
    p_nov.refresh_from_db()
    assert p_nov.status == 'Hold', f"Expected Hold, got {p_nov.status}"
    print("[PASS] Status update to 'Hold' succeeded")

    # 7. Test Revert to Unpaid (clears record)
    res_unpaid = client.get(f'/salaries/teachers/{p_nov.pk}/status/Unpaid/')
    assert res_unpaid.status_code == 302
    assert not Payroll.objects.filter(staff=teacher, month='November', year=2026).exists()
    print("[PASS] Status update to 'Unpaid' correctly removed record and reverted to pending state")

    # 8. Test Direct 1-Click Quick-Pay
    res_quick = client.get(f'/salaries/teachers/{teacher.pk}/quick-pay/?month=November&year=2026')
    assert res_quick.status_code == 302
    p_quick = Payroll.objects.get(staff=teacher, month='November', year=2026)
    assert p_quick.status == 'Paid'
    assert p_quick.net_salary == teacher.basic_salary
    print(f"[PASS] Direct 1-Click Quick-Pay succeeded: Net PKR {p_quick.net_salary:,.2f} marked as Paid")

    # 9. Test Accountant User Dual Access
    accountant_user = User.objects.filter(username__icontains='accountant').first()
    if not accountant_user:
        accountant_user = User.objects.create_user(username='test_accountant', password='Password@123', is_staff=True)
    
    client.force_login(accountant_user)
    res_acc = client.get('/salaries/teachers/')
    assert res_acc.status_code == 200, f"Accountant access to teacher_salary_list returned {res_acc.status_code}"
    res_acc_slip = client.get(f'/salaries/payroll/{payroll.pk}/slip/')
    assert res_acc_slip.status_code == 200, f"Accountant access to payroll_slip_pdf returned {res_acc_slip.status_code}"
    print("[PASS] Accountant role verified with full access to /salaries/teachers/ and salary slips")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY! ZERO ERRORS FOUND.")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()
