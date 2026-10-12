"""
Enterprise Excel Export Utilities for Ittihad Model School Management System.
Uses openpyxl to generate styled Excel spreadsheets for:
- Student Directory
- Fee Ledger & Financial Collections
- Staff Payroll Register
- Student & Staff Attendance Matrix
- Academic Merit & Position List
"""
import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from .models import SchoolSetting


HEADER_FILL = PatternFill("solid", fgColor="1E3A5F")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
TITLE_FONT  = Font(bold=True, color="1E3A5F", size=14)
SUB_FONT    = Font(italic=True, color="475569", size=10)
TOTAL_FILL  = PatternFill("solid", fgColor="E2E8F0")
TOTAL_FONT  = Font(bold=True, color="0F172A", size=11)

THIN_BORDER = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)


def export_students_excel_sheet(students):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Student Directory"

    setting = SchoolSetting.get_settings()
    school_name = setting.school_name.upper() if setting else "ITTIHAD MODEL SCHOOL"

    # Title Banner
    ws.merge_cells("A1:K1")
    ws["A1"] = f"{school_name} - STUDENT DIRECTORY"
    ws["A1"].font = TITLE_FONT
    ws["A1"].alignment = Alignment(horizontal="center")

    headers = [
        "Roll No", "Admission No", "Student Name", "Father Name", "Gender",
        "Class", "Section", "Contact", "Emergency Contact", "Monthly Fee", "Status"
    ]

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = THIN_BORDER
        ws.column_dimensions[get_column_letter(col)].width = 18

    for row_idx, s in enumerate(students, 4):
        row_data = [
            s.roll_no, s.admission_no, s.name, s.father_name, s.gender,
            f"Class {s.student_class}", s.section, s.contact,
            s.emergency_contact, float(s.monthly_fee), "Active" if s.is_active else "Inactive"
        ]
        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border = THIN_BORDER
            if col_idx in [1, 2, 5, 6, 7, 11]:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx == 10:
                cell.alignment = Alignment(horizontal="right")
                cell.number_format = "#,##0.00"

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def export_fees_excel_sheet(fees):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Fee Collection Ledger"

    setting = SchoolSetting.get_settings()
    school_name = setting.school_name.upper() if setting else "ITTIHAD MODEL SCHOOL"

    ws.merge_cells("A1:L1")
    ws["A1"] = f"{school_name} - FEE COLLECTION REPORT"
    ws["A1"].font = TITLE_FONT
    ws["A1"].alignment = Alignment(horizontal="center")

    headers = [
        "Voucher No", "Student Name", "Roll No", "Class", "Fee Type", "Month/Year",
        "Gross (PKR)", "Concession", "Payable", "Paid Amount", "Balance", "Status"
    ]

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = THIN_BORDER
        ws.column_dimensions[get_column_letter(col)].width = 16

    total_payable = 0
    total_paid = 0
    total_balance = 0

    for row_idx, f in enumerate(fees, 4):
        payable = float(f.amount)
        paid = float(f.paid_amount)
        bal = float(f.balance())

        total_payable += payable
        total_paid += paid
        total_balance += bal

        row_data = [
            f.voucher_no or f"VCH-{f.pk}", f.student.name, f.student.roll_no,
            f"Class {f.student.student_class}-{f.student.section}", f.fee_type,
            f"{f.month} {f.year}", float(f.amount + f.concession), float(f.concession),
            payable, paid, bal, f.status
        ]
        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border = THIN_BORDER
            if col_idx in [1, 3, 4, 6, 12]:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx in [7, 8, 9, 10, 11]:
                cell.alignment = Alignment(horizontal="right")
                cell.number_format = "#,##0.00"

    summary_row = len(fees) + 4
    ws.cell(row=summary_row, column=1, value="TOTAL SUMMARY").font = TOTAL_FONT
    ws.merge_cells(start_row=summary_row, start_column=1, end_row=summary_row, end_column=8)
    
    ws.cell(row=summary_row, column=9, value=total_payable).font = TOTAL_FONT
    ws.cell(row=summary_row, column=10, value=total_paid).font = TOTAL_FONT
    ws.cell(row=summary_row, column=11, value=total_balance).font = TOTAL_FONT
    
    for c in range(1, 13):
        cell = ws.cell(row=summary_row, column=c)
        cell.fill = TOTAL_FILL
        cell.border = THIN_BORDER
        if c in [9, 10, 11]:
            cell.alignment = Alignment(horizontal="right")
            cell.number_format = "#,##0.00"

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def export_payroll_excel_sheet(payrolls):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Staff Payroll Register"

    setting = SchoolSetting.get_settings()
    school_name = setting.school_name.upper() if setting else "ITTIHAD MODEL SCHOOL"

    ws.merge_cells("A1:K1")
    ws["A1"] = f"{school_name} - STAFF PAYROLL SHEET"
    ws["A1"].font = TITLE_FONT
    ws["A1"].alignment = Alignment(horizontal="center")

    headers = [
        "Emp ID", "Staff Name", "Department", "Designation", "Month/Year",
        "Basic Salary", "Allowances", "Bonus", "Deductions", "Net Salary", "Status"
    ]

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center")
        cell.border = THIN_BORDER
        ws.column_dimensions[get_column_letter(col)].width = 16

    for row_idx, p in enumerate(payrolls, 4):
        row_data = [
            p.staff.emp_id, p.staff.name, p.staff.department, p.staff.designation,
            f"{p.month} {p.year}", float(p.basic_salary), float(p.allowance),
            float(p.bonus), float(p.deductions + p.advance_deduction),
            float(p.net_salary), p.status
        ]
        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border = THIN_BORDER
            if col_idx in [1, 3, 4, 5, 11]:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx in [6, 7, 8, 9, 10]:
                cell.alignment = Alignment(horizontal="right")
                cell.number_format = "#,##0.00"

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def export_merit_list_excel_sheet(merit_data, exam_type, student_class):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Class {student_class} Merit List"

    setting = SchoolSetting.get_settings()
    school_name = setting.school_name.upper() if setting else "ITTIHAD MODEL SCHOOL"

    ws.merge_cells("A1:H1")
    ws["A1"] = f"{school_name} - CLASS {student_class} MERIT RANKINGS ({exam_type.upper()})"
    ws["A1"].font = TITLE_FONT
    ws["A1"].alignment = Alignment(horizontal="center")

    headers = [
        "Position / Rank", "Roll No", "Student Name", "Total Marks",
        "Marks Obtained", "Percentage (%)", "Cumulative GPA", "Grade"
    ]

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center")
        cell.border = THIN_BORDER
        ws.column_dimensions[get_column_letter(col)].width = 18

    for row_idx, m in enumerate(merit_data, 4):
        row_data = [
            m['position_text'], m['student'].roll_no, m['student'].name,
            m['total_max'], m['total_obtained'], m['percentage'],
            float(m['cgpa']), m['grade']
        ]
        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border = THIN_BORDER
            if col_idx in [1, 2, 4, 5, 7, 8]:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx == 6:
                cell.alignment = Alignment(horizontal="right")
                cell.number_format = "0.00%"

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
