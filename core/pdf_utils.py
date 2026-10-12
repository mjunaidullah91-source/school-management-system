"""
Enterprise PDF Utilities for Ittihad Model School Management System.
Uses ReportLab to generate:
- 3-Copy Bank Challan / Fee Vouchers (with school monogram)
- Student Result Cards (Single & Bulk Class PDF with school monogram)
- Exam Admit Cards with Barcodes, QR & Monogram
- Student & Staff ID Cards (Multi-card A4 layout with school monogram)
- School Leaving (TC), Character & Bonafide Certificates (with school crest)
- Staff Monthly Salary Slips (with school branding)

Optimized with:
- Dynamic School Monogram / Logo flowables
- Unicode TrueType font registration (Arial/Segoe/DejaVu) to support Urdu & regional names
- High-resolution vector elements and in-memory BytesIO buffers
"""
import io
import os
import html
from datetime import date
from decimal import Decimal
from django.conf import settings as django_settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, portrait, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, KeepTogether, PageBreak, HRFlowable
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.barcode import qr, code128
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ─── UNICODE TRUETYPE FONT REGISTRATION ──────────────────────────────────────
FONT_REGULAR = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'
FONT_ITALIC = 'Helvetica-Oblique'

def _register_system_fonts():
    global FONT_REGULAR, FONT_BOLD, FONT_ITALIC
    
    font_candidates = [
        # Windows system fonts
        (r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\ariali.ttf', 'EduArial'),
        (r'C:\Windows\Fonts\segoeui.ttf', r'C:\Windows\Fonts\segoeuib.ttf', r'C:\Windows\Fonts\segoeuii.ttf', 'EduSegoe'),
        (r'C:\Windows\Fonts\tahoma.ttf', r'C:\Windows\Fonts\tahomabd.ttf', r'C:\Windows\Fonts\tahoma.ttf', 'EduTahoma'),
        # Linux standard TrueType fonts
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf', 'EduDejaVu'),
        ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf', 'EduLiberation'),
    ]

    for reg_path, bold_path, italic_path, family_name in font_candidates:
        if os.path.exists(reg_path):
            try:
                pdfmetrics.registerFont(TTFont(family_name, reg_path))
                FONT_REGULAR = family_name
                
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont(f"{family_name}-Bold", bold_path))
                    FONT_BOLD = f"{family_name}-Bold"
                else:
                    FONT_BOLD = family_name
                    
                if os.path.exists(italic_path):
                    pdfmetrics.registerFont(TTFont(f"{family_name}-Italic", italic_path))
                    FONT_ITALIC = f"{family_name}-Italic"
                else:
                    FONT_ITALIC = family_name
                break
            except Exception:
                continue

_register_system_fonts()


def clean_pdf_text(val):
    """Sanitize string values for ReportLab XML/HTML Paragraph rendering."""
    if val is None:
        return ""
    s = str(val)
    return html.escape(s)


def get_school_logo_flowable(school_setting, width=32, height=32):
    """
    Returns a ReportLab Image flowable for the school monogram.
    Tries school_setting.logo first, with fallback to static/images/logo.png.
    """
    logo_path = None
    if school_setting and school_setting.logo:
        try:
            if hasattr(school_setting.logo, 'path') and os.path.exists(school_setting.logo.path):
                logo_path = school_setting.logo.path
        except Exception:
            pass
    
    if not logo_path or not os.path.exists(logo_path):
        fallbacks = [
            os.path.join(django_settings.BASE_DIR, 'media', 'school_branding', 'logo.png'),
            os.path.join(django_settings.BASE_DIR, 'static', 'images', 'logo.png'),
        ]
        for fb in fallbacks:
            if os.path.exists(fb):
                logo_path = fb
                break
                
    if logo_path and os.path.exists(logo_path):
        try:
            return RLImage(logo_path, width=width, height=height)
        except Exception:
            return None
    return None


# ─── BRANDING PALETTE ────────────────────────────────────────────────────────
PRIMARY_COLOR   = colors.HexColor('#1E3A5F')
SECONDARY_COLOR = colors.HexColor('#2563EB')
ACCENT_COLOR    = colors.HexColor('#0D9488')
DARK_TEXT       = colors.HexColor('#1E293B')
LIGHT_BG        = colors.HexColor('#F8FAFC')
BORDER_COLOR    = colors.HexColor('#CBD5E1')
SUCCESS_COLOR   = colors.HexColor('#16A34A')
DANGER_COLOR    = colors.HexColor('#DC2626')


def create_qr_drawing(text, size=45):
    """Generates a ReportLab Drawing with a clean QR code."""
    d = Drawing(size, size)
    qr_widget = qr.QrCodeWidget(str(text))
    qr_widget.barWidth = size
    qr_widget.barHeight = size
    qr_widget.qrVersion = 1
    d.add(qr_widget)
    return d


# ═══════════════════════════════════════════════════════════════════════════════
#  1. FEE VOUCHER / 3-PART BANK CHALLAN GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════
def generate_fee_voucher_pdf(fees, school_setting):
    """
    Generates a 3-part bank challan voucher (Bank Copy, School Copy, Student Copy)
    on A4 landscape with the Ittihad Model School monogram on each copy.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('ChallanTitle', parent=styles['Normal'], fontSize=8.5, fontName=FONT_BOLD, textColor=PRIMARY_COLOR, alignment=1)
    sub_style = ParagraphStyle('ChallanSub', parent=styles['Normal'], fontSize=6, fontName=FONT_REGULAR, textColor=DARK_TEXT, alignment=1)
    body_bold = ParagraphStyle('ChallanBold', parent=styles['Normal'], fontSize=7, fontName=FONT_BOLD)
    body_norm = ParagraphStyle('ChallanNorm', parent=styles['Normal'], fontSize=7, fontName=FONT_REGULAR)
    right_bold = ParagraphStyle('ChallanRightBold', parent=styles['Normal'], fontSize=7, fontName=FONT_BOLD, alignment=2)
    right_norm = ParagraphStyle('ChallanRightNorm', parent=styles['Normal'], fontSize=7, fontName=FONT_REGULAR, alignment=2)
    center_bold = ParagraphStyle('ChallanCenterBold', parent=styles['Normal'], fontSize=7, fontName=FONT_BOLD, alignment=1)

    story = []
    copy_types = ['BANK COPY', 'SCHOOL COPY', 'STUDENT COPY']

    if not isinstance(fees, (list, tuple)) and hasattr(fees, 'pk'):
        fees = [fees]

    for fee_idx, fee in enumerate(fees):
        student = fee.student
        column_tables = []

        for copy_name in copy_types:
            copy_elements = []

            # 1. Header with Logo & School Name
            logo_img = get_school_logo_flowable(school_setting, width=22*mm, height=22*mm)
            header_text_block = [
                Paragraph(clean_pdf_text(school_setting.school_name.upper()), title_style),
                Paragraph(clean_pdf_text(school_setting.tagline), sub_style),
                Paragraph(f"<b>{copy_name}</b> | Fee Challan", ParagraphStyle('Badge', parent=sub_style, fontName=FONT_BOLD, textColor=SECONDARY_COLOR))
            ]
            
            if logo_img:
                head_table = Table([[logo_img, header_text_block]], colWidths=[24 * mm, 60 * mm])
                head_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (0,0), 'CENTER'),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ]))
                copy_elements.append(head_table)
            else:
                for p in header_text_block:
                    copy_elements.append(p)
                    
            copy_elements.append(Spacer(1, 1.5 * mm))

            # 2. Bank Account Details Box
            bank_info = [
                [Paragraph(f"<b>Bank:</b> {clean_pdf_text(school_setting.bank_name)}", body_norm), Paragraph(f"<b>Branch:</b> {clean_pdf_text(school_setting.bank_branch)}", body_norm)],
                [Paragraph(f"<b>A/C Title:</b> {clean_pdf_text(school_setting.bank_account_title)}", body_norm), Paragraph(f"<b>A/C No:</b> {clean_pdf_text(school_setting.bank_account_no)}", body_norm)],
                [Paragraph(f"<b>IBAN:</b> {clean_pdf_text(school_setting.iban)}", body_norm), Paragraph(f"<b>Voucher:</b> {clean_pdf_text(fee.voucher_no)}", body_bold)],
            ]
            t_bank = Table(bank_info, colWidths=[42 * mm, 42 * mm])
            t_bank.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
                ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ]))
            copy_elements.append(t_bank)
            copy_elements.append(Spacer(1, 1.5 * mm))

            # 3. Student Info Table
            std_info = [
                [Paragraph("<b>Roll No:</b>", body_norm), Paragraph(clean_pdf_text(student.roll_no), body_bold), Paragraph("<b>Issue Date:</b>", body_norm), Paragraph(str(fee.issue_date), body_norm)],
                [Paragraph("<b>Student:</b>", body_norm), Paragraph(clean_pdf_text(student.name[:20]), body_bold), Paragraph("<b>Due Date:</b>", body_norm), Paragraph(str(fee.due_date or '—'), body_bold)],
                [Paragraph("<b>Class:</b>", body_norm), Paragraph(f"Class {student.student_class}-{student.section}", body_norm), Paragraph("<b>Month/Year:</b>", body_norm), Paragraph(f"{fee.month} {fee.year}", body_norm)],
                [Paragraph("<b>Father:</b>", body_norm), Paragraph(clean_pdf_text(student.father_name[:20]), body_norm), Paragraph("<b>Status:</b>", body_norm), Paragraph(f"<b>{fee.status}</b>", body_bold)],
            ]
            t_std = Table(std_info, colWidths=[16 * mm, 28 * mm, 18 * mm, 22 * mm])
            t_std.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ]))
            copy_elements.append(t_std)
            copy_elements.append(Spacer(1, 2 * mm))

            # 4. Fee Breakdown Line Items
            fee_items = [
                [Paragraph("<b>Fee Particulars</b>", body_bold), Paragraph("<b>Amount (PKR)</b>", right_bold)],
                [Paragraph("Tuition Fee", body_norm), Paragraph(f"{fee.tuition_fee or fee.amount:,.2f}", right_norm)],
            ]
            if fee.admission_fee > 0:
                fee_items.append([Paragraph("Admission Fee", body_norm), Paragraph(f"{fee.admission_fee:,.2f}", right_norm)])
            if fee.exam_fee > 0:
                fee_items.append([Paragraph("Examination Fee", body_norm), Paragraph(f"{fee.exam_fee:,.2f}", right_norm)])
            if fee.other_fee > 0:
                fee_items.append([Paragraph("Other / Lab / Library Charges", body_norm), Paragraph(f"{fee.other_fee:,.2f}", right_norm)])
            if fee.late_fee_fine > 0:
                fee_items.append([Paragraph("Late Fee Fine", body_norm), Paragraph(f"{fee.late_fee_fine:,.2f}", right_norm)])
            if fee.concession > 0:
                fee_items.append([Paragraph("Less: Scholarship / Concession", body_norm), Paragraph(f"- {fee.concession:,.2f}", right_norm)])

            fee_items.append([Paragraph("<b>TOTAL PAYABLE (Within Due Date)</b>", body_bold), Paragraph(f"<b>PKR {fee.amount:,.2f}</b>", right_bold)])
            fee_items.append([Paragraph("Amount Paid", body_norm), Paragraph(f"PKR {fee.paid_amount:,.2f}", right_norm)])
            fee_items.append([Paragraph("<b>REMAINING BALANCE</b>", body_bold), Paragraph(f"<b>PKR {fee.balance():,.2f}</b>", right_bold)])

            t_fee = Table(fee_items, colWidths=[54 * mm, 30 * mm])
            t_fee.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#CBD5E1')),
                ('BACKGROUND', (0,-3), (-1,-3), colors.HexColor('#EBF4FF')),
                ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FEF2F2') if fee.balance() > 0 else colors.HexColor('#F0FDF4')),
                ('TOPPADDING', (0,0), (-1,-1), 1.2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
            ]))
            copy_elements.append(t_fee)
            copy_elements.append(Spacer(1, 2 * mm))

            # 5. Instructions & Signatures
            qr_draw = create_qr_drawing(f"VOUCHER:{fee.voucher_no}|STD:{student.roll_no}|AMT:{fee.amount}|DUE:{fee.due_date}", size=36)
            bottom_row = [
                [
                    qr_draw,
                    Paragraph("* Pay before due date to avoid fine.<br/>* Non-refundable &amp; non-transferable.<br/>* Deposit at any designated branch.", sub_style),
                    Paragraph("___________________<br/><b>Cashier / Officer</b>", center_bold)
                ]
            ]
            t_bottom = Table(bottom_row, colWidths=[15 * mm, 45 * mm, 24 * mm])
            t_bottom.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ]))
            copy_elements.append(t_bottom)

            t_col = Table([[el] for el in copy_elements], colWidths=[86 * mm])
            t_col.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 0.8, PRIMARY_COLOR),
                ('LEFTPADDING', (0,0), (-1,-1), 2),
                ('RIGHTPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            column_tables.append(t_col)

        row_table = Table([[column_tables[0], column_tables[1], column_tables[2]]], colWidths=[89 * mm, 89 * mm, 89 * mm])
        row_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 1),
            ('RIGHTPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(row_table)

        if fee_idx < len(fees) - 1:
            story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer


# ═══════════════════════════════════════════════════════════════════════════════
#  2. ADVANCED RESULT CARD / REPORT CARD GENERATOR (SINGLE & BULK)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_result_card_pdf(student, exam_name, academic_year, results, school_setting, position_text="—", attendance_pct=100.0):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    styles = getSampleStyleSheet()
    story = _build_single_result_card_story(student, exam_name, academic_year, results, school_setting, position_text, attendance_pct, styles)

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_bulk_result_cards_pdf(students_result_data, exam_name, academic_year, school_setting):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    styles = getSampleStyleSheet()
    story = []

    for idx, (student, results, pos_text, att_pct) in enumerate(students_result_data):
        card_story = _build_single_result_card_story(student, exam_name, academic_year, results, school_setting, pos_text, att_pct, styles)
        story.extend(card_story)
        if idx < len(students_result_data) - 1:
            story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer


def _build_single_result_card_story(student, exam_name, academic_year, results, school_setting, position_text, attendance_pct, styles):
    story = []

    header_style = ParagraphStyle('SchoolHead', parent=styles['Normal'], fontSize=16, fontName=FONT_BOLD, textColor=PRIMARY_COLOR, alignment=1)
    tag_style = ParagraphStyle('SchoolTag', parent=styles['Normal'], fontSize=8.5, fontName=FONT_REGULAR, textColor=DARK_TEXT, alignment=1)
    card_title = ParagraphStyle('CardTitle', parent=styles['Normal'], fontSize=11, fontName=FONT_BOLD, textColor=SECONDARY_COLOR, alignment=1)
    body_bold = ParagraphStyle('RCBold', parent=styles['Normal'], fontSize=8.5, fontName=FONT_BOLD)
    body_norm = ParagraphStyle('RCNorm', parent=styles['Normal'], fontSize=8.5, fontName=FONT_REGULAR)
    center_norm = ParagraphStyle('RCCenter', parent=styles['Normal'], fontSize=8.5, fontName=FONT_REGULAR, alignment=1)
    center_bold = ParagraphStyle('RCCenterBold', parent=styles['Normal'], fontSize=8.5, fontName=FONT_BOLD, alignment=1)

    # 1. School Header with Monogram
    logo_img = get_school_logo_flowable(school_setting, width=38*mm, height=38*mm)
    head_text = [
        Paragraph(clean_pdf_text(school_setting.school_name.upper()), header_style),
        Paragraph(f"{clean_pdf_text(school_setting.tagline)} | Reg No: {clean_pdf_text(school_setting.registration_no)}", tag_style),
        Paragraph(f"{clean_pdf_text(school_setting.address)} | Ph: {clean_pdf_text(school_setting.contact_phone)}", tag_style),
        Spacer(1, 2 * mm),
        Paragraph(f"OFFICIAL ACADEMIC PROGRESS REPORT — {clean_pdf_text(exam_name.upper())} ({academic_year})", card_title)
    ]
    
    if logo_img:
        head_table = Table([[logo_img, head_text]], colWidths=[40 * mm, 146 * mm])
        head_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(head_table)
    else:
        for item in head_text:
            story.append(item)

    story.append(Spacer(1, 4 * mm))

    # 2. Student Demographic Table
    std_data = [
        [Paragraph("<b>Student Name:</b>", body_norm), Paragraph(clean_pdf_text(student.name), body_bold), Paragraph("<b>Roll Number:</b>", body_norm), Paragraph(clean_pdf_text(student.roll_no), body_bold)],
        [Paragraph("<b>Father's Name:</b>", body_norm), Paragraph(clean_pdf_text(student.father_name), body_norm), Paragraph("<b>Admission No:</b>", body_norm), Paragraph(clean_pdf_text(student.admission_no or '—'), body_norm)],
        [Paragraph("<b>Class &amp; Section:</b>", body_norm), Paragraph(f"Class {student.student_class} - Section {student.section}", body_bold), Paragraph("<b>Date of Birth:</b>", body_norm), Paragraph(str(student.dob or '—'), body_norm)],
        [Paragraph("<b>Attendance:</b>", body_norm), Paragraph(f"<b>{attendance_pct}%</b>", body_bold), Paragraph("<b>Class Position:</b>", body_norm), Paragraph(f"<b>{clean_pdf_text(position_text)}</b>", body_bold)],
    ]
    t_std = Table(std_data, colWidths=[35 * mm, 58 * mm, 35 * mm, 58 * mm])
    t_std.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY_COLOR),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_std)
    story.append(Spacer(1, 5 * mm))

    # 3. Marks & Academic Performance Table
    table_data = [
        [
            Paragraph("<b>#</b>", center_bold),
            Paragraph("<b>Subject</b>", body_bold),
            Paragraph("<b>Max Marks</b>", center_bold),
            Paragraph("<b>Passing</b>", center_bold),
            Paragraph("<b>Obtained</b>", center_bold),
            Paragraph("<b>%</b>", center_bold),
            Paragraph("<b>Grade</b>", center_bold),
            Paragraph("<b>GPA</b>", center_bold),
            Paragraph("<b>Teacher Remarks</b>", body_bold),
        ]
    ]

    total_max = 0
    total_obtained = 0
    total_gpa_points = Decimal('0.00')
    count_subjects = len(results)

    for i, r in enumerate(results, 1):
        pct = r.percentage()
        total_max += r.max_marks
        total_obtained += float(r.marks_obtained)
        total_gpa_points += r.gpa

        status_color = DANGER_COLOR if r.grade == 'F' else DARK_TEXT

        table_data.append([
            Paragraph(str(i), center_norm),
            Paragraph(clean_pdf_text(r.subject.name), body_norm),
            Paragraph(str(r.max_marks), center_norm),
            Paragraph(str(r.subject.passing_marks), center_norm),
            Paragraph(f"<b>{r.marks_obtained}</b>", ParagraphStyle('Obt', parent=center_bold, textColor=status_color)),
            Paragraph(f"{pct}%", center_norm),
            Paragraph(f"<b>{r.grade}</b>", ParagraphStyle('Grd', parent=center_bold, textColor=status_color)),
            Paragraph(f"{r.gpa:.2f}", center_norm),
            Paragraph(clean_pdf_text(r.teacher_remarks or 'Good effort'), body_norm),
        ])

    overall_pct = round((total_obtained / total_max) * 100, 2) if total_max else 0
    cgpa = round(total_gpa_points / Decimal(count_subjects), 2) if count_subjects else Decimal('0.00')

    if overall_pct >= 90:   overall_grade = 'A+'
    elif overall_pct >= 80: overall_grade = 'A'
    elif overall_pct >= 70: overall_grade = 'B'
    elif overall_pct >= 60: overall_grade = 'C'
    elif overall_pct >= 50: overall_grade = 'D'
    else:                   overall_grade = 'F'

    table_data.append([
        Paragraph("", center_bold),
        Paragraph("<b>GRAND TOTAL</b>", body_bold),
        Paragraph(f"<b>{total_max}</b>", center_bold),
        Paragraph("—", center_norm),
        Paragraph(f"<b>{total_obtained:,.1f}</b>", center_bold),
        Paragraph(f"<b>{overall_pct}%</b>", center_bold),
        Paragraph(f"<b>{overall_grade}</b>", ParagraphStyle('TotGrd', parent=center_bold, textColor=PRIMARY_COLOR, fontSize=10)),
        Paragraph(f"<b>{cgpa:.2f}</b>", center_bold),
        Paragraph(f"<b>Result: {'PASSED' if overall_grade != 'F' else 'FAILED'}</b>", body_bold),
    ])

    t_results = Table(table_data, colWidths=[8 * mm, 45 * mm, 18 * mm, 16 * mm, 18 * mm, 16 * mm, 15 * mm, 15 * mm, 35 * mm])
    t_results.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EBF4FF')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    story.append(t_results)
    story.append(Spacer(1, 5 * mm))

    # 4. Grading Scale Matrix & Summary Panel
    scale_data = [
        [
            Paragraph("<b>Grading Scale Reference:</b><br/>90-100% : A+ (4.00) — Outstanding<br/>80-89% : A (3.70) — Excellent<br/>70-79% : B (3.00) — Very Good<br/>60-69% : C (2.00) — Good<br/>50-59% : D (1.00) — Satisfactory<br/>&lt; 50% : F (0.00) — Fail", ParagraphStyle('Scale', parent=styles['Normal'], fontSize=7, leading=9, fontName=FONT_REGULAR)),
            create_qr_drawing(f"RESULT:{student.roll_no}|EXAM:{exam_name}|YEAR:{academic_year}|PCT:{overall_pct}%|GRD:{overall_grade}", size=52),
            Paragraph(f"<b>ACADEMIC SUMMARY:</b><br/><b>Percentage:</b> {overall_pct}%<br/><b>Cumulative GPA:</b> {cgpa:.2f}<br/><b>Final Grade:</b> {overall_grade}<br/><b>Class Position:</b> {clean_pdf_text(position_text)}<br/><b>Status:</b> {'PROMOTED' if overall_grade != 'F' else 'DETENTION'}", ParagraphStyle('Summ', parent=styles['Normal'], fontSize=8, leading=11, textColor=PRIMARY_COLOR, fontName=FONT_REGULAR))
        ]
    ]
    t_scale = Table(scale_data, colWidths=[65 * mm, 40 * mm, 81 * mm])
    t_scale.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_scale)
    story.append(Spacer(1, 8 * mm))

    # 5. Signatures Block
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Class Teacher Signature</b>", center_bold),
            Paragraph("____________________________<br/><b>Controller of Examinations</b>", center_bold),
            Paragraph(f"____________________________<br/><b>Principal ({clean_pdf_text(school_setting.principal_name)})</b>", center_bold),
        ]
    ]
    t_sig = Table(sig_data, colWidths=[62 * mm, 62 * mm, 62 * mm])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_sig)

    return story


# ═══════════════════════════════════════════════════════════════════════════════
#  3. EXAM ADMIT CARD GENERATOR WITH BARCODE / QR & MONOGRAM
# ═══════════════════════════════════════════════════════════════════════════════
def generate_admit_card_pdf(student, exam, schedules, school_setting):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=12 * mm, bottomMargin=12 * mm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('AdmitTitle', parent=styles['Normal'], fontSize=15, fontName=FONT_BOLD, textColor=PRIMARY_COLOR, alignment=1)
    tag_style = ParagraphStyle('AdmitTag', parent=styles['Normal'], fontSize=8.5, fontName=FONT_REGULAR, alignment=1)
    bold_style = ParagraphStyle('AdmitBold', parent=styles['Normal'], fontSize=8.5, fontName=FONT_BOLD)
    norm_style = ParagraphStyle('AdmitNorm', parent=styles['Normal'], fontSize=8.5, fontName=FONT_REGULAR)
    center_bold = ParagraphStyle('AdmitCBold', parent=styles['Normal'], fontSize=8.5, fontName=FONT_BOLD, alignment=1)

    story = []

    logo_img = get_school_logo_flowable(school_setting, width=32*mm, height=32*mm)
    head_text = [
        Paragraph(clean_pdf_text(school_setting.school_name.upper()), title_style),
        Paragraph(f"{clean_pdf_text(school_setting.address)} | Ph: {clean_pdf_text(school_setting.contact_phone)}", tag_style),
        Spacer(1, 2 * mm),
        Paragraph(f"EXAMINATION ADMIT CARD / ROLL NUMBER SLIP — {clean_pdf_text(exam.title.upper())} ({exam.academic_year})", ParagraphStyle('Badg', parent=tag_style, fontSize=11, fontName=FONT_BOLD, textColor=SECONDARY_COLOR))
    ]
    
    if logo_img:
        head_table = Table([[logo_img, head_text]], colWidths=[35 * mm, 145 * mm])
        head_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
        ]))
        story.append(head_table)
    else:
        for p in head_text:
            story.append(p)
            
    story.append(Spacer(1, 4 * mm))

    qr_draw = create_qr_drawing(f"ADMIT:{student.roll_no}|EXAM:{exam.title}|CLASS:{student.student_class}-{student.section}", size=55)
    std_info = [
        [
            Paragraph("<b>Roll No:</b>", norm_style), Paragraph(clean_pdf_text(student.roll_no), bold_style),
            Paragraph("<b>Student Name:</b>", norm_style), Paragraph(clean_pdf_text(student.name), bold_style),
            qr_draw
        ],
        [
            Paragraph("<b>Class:</b>", norm_style), Paragraph(f"Class {student.student_class} ({student.section})", bold_style),
            Paragraph("<b>Father's Name:</b>", norm_style), Paragraph(clean_pdf_text(student.father_name), norm_style),
            ""
        ],
        [
            Paragraph("<b>Exam Center:</b>", norm_style), Paragraph("Main Campus Hall A", norm_style),
            Paragraph("<b>Emergency Ph:</b>", norm_style), Paragraph(clean_pdf_text(student.emergency_contact or student.contact or '—'), norm_style),
            ""
        ],
    ]
    t_std = Table(std_info, colWidths=[24 * mm, 38 * mm, 26 * mm, 50 * mm, 32 * mm])
    t_std.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY_COLOR),
        ('SPAN', (4,0), (4,2)),
        ('ALIGN', (4,0), (4,2), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_std)
    story.append(Spacer(1, 5 * mm))

    table_data = [
        [
            Paragraph("<b>Date</b>", center_bold),
            Paragraph("<b>Day</b>", center_bold),
            Paragraph("<b>Time</b>", center_bold),
            Paragraph("<b>Subject</b>", bold_style),
            Paragraph("<b>Room / Hall</b>", center_bold),
            Paragraph("<b>Invigilator Sign</b>", center_bold),
        ]
    ]

    for sch in schedules:
        table_data.append([
            Paragraph(str(sch.exam_date), norm_style),
            Paragraph(sch.exam_date.strftime('%A'), norm_style),
            Paragraph(f"{sch.start_time.strftime('%I:%M %p')} - {sch.end_time.strftime('%I:%M %p')}", norm_style),
            Paragraph(clean_pdf_text(sch.subject.name), bold_style),
            Paragraph(clean_pdf_text(sch.room_no), center_bold),
            Paragraph("________________", center_bold),
        ])

    t_sch = Table(table_data, colWidths=[24 * mm, 24 * mm, 36 * mm, 44 * mm, 22 * mm, 30 * mm])
    t_sch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    story.append(t_sch)
    story.append(Spacer(1, 5 * mm))

    instructions = f"<b>IMPORTANT CANDIDATE INSTRUCTIONS:</b><br/>1. Possession of this Admit Card and Student ID Card is mandatory during all exam sessions.<br/>2. Candidates must be seated 15 minutes before the exam commences.<br/>3. Mobile phones, programmable calculators, and unauthorized materials are strictly prohibited.<br/>4. {clean_pdf_text(exam.instructions)}"
    t_inst = Table([[Paragraph(instructions, ParagraphStyle('Inst', parent=styles['Normal'], fontSize=7.5, leading=10, fontName=FONT_REGULAR))]], colWidths=[180 * mm])
    t_inst.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF3C7')),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#D97706')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_inst)
    story.append(Spacer(1, 10 * mm))

    sig_data = [
        [
            Paragraph("____________________________<br/><b>Student's Signature</b>", center_bold),
            Paragraph("____________________________<br/><b>Controller of Examinations</b>", center_bold),
            Paragraph(f"____________________________<br/><b>Principal Seal &amp; Signature</b>", center_bold),
        ]
    ]
    t_sig = Table(sig_data, colWidths=[60 * mm, 60 * mm, 60 * mm])
    story.append(t_sig)

    doc.build(story)
    buffer.seek(0)
    return buffer


# ═══════════════════════════════════════════════════════════════════════════════
#  4. STUDENT & STAFF ID CARD GENERATOR (MULTI-CARD PRINT LAYOUT WITH LOGO)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_id_cards_pdf(items, card_type='student', school_setting=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=8 * mm, rightMargin=8 * mm, topMargin=8 * mm, bottomMargin=8 * mm)
    styles = getSampleStyleSheet()

    card_header = ParagraphStyle('IDHead', parent=styles['Normal'], fontSize=7, fontName=FONT_BOLD, textColor=colors.white, alignment=1)
    card_sub = ParagraphStyle('IDSub', parent=styles['Normal'], fontSize=5, fontName=FONT_REGULAR, textColor=colors.HexColor('#E2E8F0'), alignment=1)
    card_name = ParagraphStyle('IDName', parent=styles['Normal'], fontSize=8.5, fontName=FONT_BOLD, textColor=PRIMARY_COLOR, alignment=1)
    body_bold = ParagraphStyle('IDBold', parent=styles['Normal'], fontSize=6.5, fontName=FONT_BOLD)
    body_norm = ParagraphStyle('IDNorm', parent=styles['Normal'], fontSize=6.5, fontName=FONT_REGULAR)

    story = []
    card_boxes = []

    for item in items:
        qr_text = f"ID:{item.roll_no if card_type == 'student' else item.emp_id}|NAME:{item.name}|TYPE:{card_type.upper()}"
        qr_draw = create_qr_drawing(qr_text, size=32)
        logo_tiny = get_school_logo_flowable(school_setting, width=14*mm, height=14*mm)

        head_text = [
            Paragraph(clean_pdf_text(school_setting.school_name.upper()), card_header),
            Paragraph("STUDENT IDENTITY CARD" if card_type == 'student' else "STAFF IDENTITY CARD", card_sub)
        ]
        
        if logo_tiny:
            head_table = Table([[logo_tiny, head_text]], colWidths=[15 * mm, 73 * mm])
            head_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), PRIMARY_COLOR if card_type == 'student' else colors.HexColor('#0F766E')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ]))
        else:
            head_table = Table([[p] for p in head_text], colWidths=[88 * mm])
            head_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), PRIMARY_COLOR if card_type == 'student' else colors.HexColor('#0F766E')),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ]))

        if card_type == 'student':
            details = [
                [Paragraph("<b>Roll No:</b>", body_norm), Paragraph(clean_pdf_text(item.roll_no), body_bold), qr_draw],
                [Paragraph("<b>Class:</b>", body_norm), Paragraph(f"{item.student_class} ({item.section})", body_bold), ""],
                [Paragraph("<b>Father:</b>", body_norm), Paragraph(clean_pdf_text(item.father_name[:16]), body_norm), ""],
                [Paragraph("<b>Blood Grp:</b>", body_norm), Paragraph(clean_pdf_text(item.blood_group), body_bold), ""],
                [Paragraph("<b>Emergency:</b>", body_norm), Paragraph(clean_pdf_text(item.emergency_contact or item.contact or '—'), body_norm), ""],
            ]
            t_det = Table(details, colWidths=[18 * mm, 40 * mm, 26 * mm])
        else:
            details = [
                [Paragraph("<b>Emp ID:</b>", body_norm), Paragraph(clean_pdf_text(item.emp_id), body_bold), qr_draw],
                [Paragraph("<b>Designation:</b>", body_norm), Paragraph(clean_pdf_text(item.designation[:16]), body_bold), ""],
                [Paragraph("<b>Dept:</b>", body_norm), Paragraph(clean_pdf_text(item.department), body_norm), ""],
                [Paragraph("<b>Blood Grp:</b>", body_norm), Paragraph(clean_pdf_text(item.blood_group), body_bold), ""],
                [Paragraph("<b>Contact:</b>", body_norm), Paragraph(clean_pdf_text(item.contact), body_norm), ""],
            ]
            t_det = Table(details, colWidths=[18 * mm, 40 * mm, 26 * mm])

        t_det.setStyle(TableStyle([
            ('SPAN', (2,0), (2,4)),
            ('ALIGN', (2,0), (2,4), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 0.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0.5),
        ]))

        single_card = Table([
            [head_table],
            [Paragraph(clean_pdf_text(item.name.upper()), card_name)],
            [t_det],
            [Paragraph(f"Valid: 2025–2026 | Principal Sign: ________________", ParagraphStyle('Sign', parent=styles['Normal'], fontSize=5, alignment=1, textColor=colors.HexColor('#64748B'), fontName=FONT_REGULAR))]
        ], colWidths=[90 * mm])
        single_card.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]))
        card_boxes.append(single_card)

    for i in range(0, len(card_boxes), 2):
        row_items = [card_boxes[i]]
        if i + 1 < len(card_boxes):
            row_items.append(card_boxes[i+1])
        else:
            row_items.append(Paragraph("", styles['Normal']))

        grid_table = Table([row_items], colWidths=[95 * mm, 95 * mm])
        grid_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4 * mm),
        ]))
        story.append(grid_table)

        if (i + 2) % 8 == 0 and (i + 2) < len(card_boxes):
            story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer


# ═══════════════════════════════════════════════════════════════════════════════
#  5. CERTIFICATE GENERATOR (LEAVING / TC, CHARACTER, BONAFIDE)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_certificate_pdf(certificate, school_setting):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm
    )
    styles = getSampleStyleSheet()

    school_title = ParagraphStyle('CertSchool', parent=styles['Normal'], fontSize=16, fontName=FONT_BOLD, textColor=PRIMARY_COLOR, alignment=1)
    sub_title = ParagraphStyle('CertSub', parent=styles['Normal'], fontSize=8.5, fontName=FONT_REGULAR, textColor=DARK_TEXT, alignment=1)
    cert_title = ParagraphStyle('CertTitle', parent=styles['Normal'], fontSize=13, fontName=FONT_BOLD, textColor=SECONDARY_COLOR, alignment=1)
    body_style = ParagraphStyle('CertBody', parent=styles['Normal'], fontSize=9.5, fontName=FONT_REGULAR, leading=14.5, alignment=4)
    center_bold = ParagraphStyle('CertCBold', parent=styles['Normal'], fontSize=9, fontName=FONT_BOLD, alignment=1)

    student = certificate.student
    story = []

    content = []
    logo_crest = get_school_logo_flowable(school_setting, width=28*mm, height=28*mm)
    
    head_text = [
        Paragraph(clean_pdf_text(school_setting.school_name.upper()), school_title),
        Paragraph(f"{clean_pdf_text(school_setting.tagline)} | Reg No: {clean_pdf_text(school_setting.registration_no)}", sub_title),
        Paragraph(f"{clean_pdf_text(school_setting.address)} | Contact: {clean_pdf_text(school_setting.contact_phone)}", sub_title),
    ]
    
    if logo_crest:
        t_head = Table([[logo_crest, head_text]], colWidths=[32 * mm, 228 * mm])
        t_head.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
        ]))
        content.append(t_head)
    else:
        for p in head_text:
            content.append(p)

    content.append(Spacer(1, 2 * mm))
    content.append(HRFlowable(width="95%", thickness=1, color=PRIMARY_COLOR, spaceAfter=2*mm))
    content.append(Paragraph(clean_pdf_text(certificate.get_certificate_type_display().upper()), cert_title))
    content.append(Paragraph(f"<b>Certificate No:</b> {clean_pdf_text(certificate.certificate_no)} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Issue Date:</b> {certificate.issue_date}", sub_title))
    content.append(Spacer(1, 3 * mm))

    std_name_clean = clean_pdf_text(student.name)
    father_clean = clean_pdf_text(student.father_name)
    roll_clean = clean_pdf_text(student.roll_no)
    conduct_clean = clean_pdf_text(certificate.conduct_remarks)
    reason_clean = clean_pdf_text(certificate.reason_for_leaving)

    if certificate.certificate_type == 'Leaving_TC':
        body_text = f"""
        This is to certify that <b>{std_name_clean}</b>, Son / Daughter of <b>{father_clean}</b>, 
        bearing Roll No. <b>{roll_clean}</b> (Admission No: <b>{clean_pdf_text(student.admission_no or '—')}</b>), 
        was a bonafide regular student of this institution in <b>Class {student.student_class} (Section {student.section})</b> 
        during the academic session <b>{clean_pdf_text(certificate.session)}</b>.<br/><br/>
        His / Her date of birth according to the school admission register is <b>{student.dob or 'N/A'}</b>. 
        All school dues, fee assessments, and library liabilities have been fully cleared up to the date of departure. 
        The student is leaving the school due to <b>{reason_clean}</b>. 
        During his / her stay at the institution, his / her conduct and moral character were found to be <b>{conduct_clean}</b>.<br/><br/>
        We wish him / her every success in all future educational endeavors.
        """
    elif certificate.certificate_type == 'Character':
        body_text = f"""
        This is to certify that <b>{std_name_clean}</b>, Son / Daughter of <b>{father_clean}</b>, 
        bearing Roll No. <b>{roll_clean}</b>, is / was a student of <b>Class {student.student_class}-{student.section}</b> 
        at <b>{clean_pdf_text(school_setting.school_name)}</b>.<br/><br/>
        To the best of our knowledge and official institutional records, he / she bears exemplary moral character, 
        maintains sincere discipline, and has not participated in any subversive or antisocial activities. 
        His / Her conduct with teachers, staff, and peers has been consistently <b>{conduct_clean}</b>.<br/><br/>
        This certificate is granted upon request for official / academic purposes.
        """
    else:  # Bonafide / Merit
        body_text = f"""
        This is to certify that <b>{std_name_clean}</b>, Son / Daughter of <b>{father_clean}</b>, 
        bearing Roll No. <b>{roll_clean}</b>, is currently a bonafide, active student of 
        <b>Class {student.student_class} (Section {student.section})</b> at <b>{clean_pdf_text(school_setting.school_name)}</b> 
        for the ongoing academic term <b>{clean_pdf_text(certificate.session)}</b>.<br/><br/>
        He / She was admitted on <b>{student.admission_date}</b> and is currently pursuing his / her studies with diligence.<br/><br/>
        Remarks: <b>{conduct_clean}</b>
        """

    content.append(Paragraph(body_text, body_style))
    content.append(Spacer(1, 4 * mm))

    qr_draw = create_qr_drawing(f"CERT:{certificate.certificate_no}|STD:{student.roll_no}|TYPE:{certificate.certificate_type}", size=38)
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Prepared &amp; Verified By</b>", center_bold),
            qr_draw,
            Paragraph(f"____________________________<br/><b>Principal ({clean_pdf_text(school_setting.principal_name)})</b>", center_bold),
        ]
    ]
    t_sig = Table(sig_data, colWidths=[85 * mm, 90 * mm, 85 * mm])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
    ]))
    content.append(t_sig)

    frame = Table([[Table([[c] for c in content], colWidths=[265 * mm])]], colWidths=[270 * mm])
    frame.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, PRIMARY_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FCFDFE')),
        ('TOPPADDING', (0,0), (-1,-1), 2 * mm),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2 * mm),
        ('LEFTPADDING', (0,0), (-1,-1), 3 * mm),
        ('RIGHTPADDING', (0,0), (-1,-1), 3 * mm),
    ]))
    story.append(frame)

    doc.build(story)
    buffer.seek(0)
    return buffer


# ═══════════════════════════════════════════════════════════════════════════════
#  6. STAFF SALARY SLIP GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════
def generate_salary_slip_pdf(payroll, school_setting):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=portrait(A4), leftMargin=15 * mm, rightMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm)
    styles = getSampleStyleSheet()

    staff = payroll.staff
    story = []

    title_style = ParagraphStyle('PayTitle', parent=styles['Normal'], fontSize=15, fontName=FONT_BOLD, textColor=PRIMARY_COLOR, alignment=1)
    tag_style = ParagraphStyle('PayTag', parent=styles['Normal'], fontSize=9, fontName=FONT_REGULAR, alignment=1)
    bold_style = ParagraphStyle('PayBold', parent=styles['Normal'], fontSize=9, fontName=FONT_BOLD)
    norm_style = ParagraphStyle('PayNorm', parent=styles['Normal'], fontSize=9, fontName=FONT_REGULAR)
    right_bold = ParagraphStyle('PayRBold', parent=styles['Normal'], fontSize=9, fontName=FONT_BOLD, alignment=2)
    right_norm = ParagraphStyle('PayRNorm', parent=styles['Normal'], fontSize=9, fontName=FONT_REGULAR, alignment=2)
    center_bold = ParagraphStyle('PayCBold', parent=styles['Normal'], fontSize=9, fontName=FONT_BOLD, alignment=1)

    logo_img = get_school_logo_flowable(school_setting, width=32*mm, height=32*mm)
    head_text = [
        Paragraph(clean_pdf_text(school_setting.school_name.upper()), title_style),
        Paragraph(f"{clean_pdf_text(school_setting.address)} | Ph: {clean_pdf_text(school_setting.contact_phone)}", tag_style),
        Spacer(1, 2 * mm),
        Paragraph(f"MONTHLY SALARY SLIP — {clean_pdf_text(payroll.month.upper())} {payroll.year}", ParagraphStyle('Badge', parent=tag_style, fontSize=11, fontName=FONT_BOLD, textColor=SECONDARY_COLOR))
    ]
    
    if logo_img:
        head_table = Table([[logo_img, head_text]], colWidths=[35 * mm, 145 * mm])
        head_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
        ]))
        story.append(head_table)
    else:
        for p in head_text:
            story.append(p)
            
    story.append(Spacer(1, 4 * mm))

    staff_info = [
        [Paragraph("<b>Employee ID:</b>", norm_style), Paragraph(clean_pdf_text(staff.emp_id), bold_style), Paragraph("<b>Payment Date:</b>", norm_style), Paragraph(str(payroll.payment_date or '—'), norm_style)],
        [Paragraph("<b>Name:</b>", norm_style), Paragraph(clean_pdf_text(staff.name), bold_style), Paragraph("<b>Department:</b>", norm_style), Paragraph(clean_pdf_text(staff.department), norm_style)],
        [Paragraph("<b>Designation:</b>", norm_style), Paragraph(clean_pdf_text(staff.designation), norm_style), Paragraph("<b>Payment Mode:</b>", norm_style), Paragraph(clean_pdf_text(payroll.payment_mode), norm_style)],
        [Paragraph("<b>CNIC / NID:</b>", norm_style), Paragraph(clean_pdf_text(staff.cnic_or_nid or '—'), norm_style), Paragraph("<b>Status:</b>", norm_style), Paragraph(f"<b>{payroll.status}</b>", bold_style)],
    ]
    t_staff = Table(staff_info, colWidths=[35 * mm, 55 * mm, 35 * mm, 55 * mm])
    t_staff.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY_COLOR),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_staff)
    story.append(Spacer(1, 6 * mm))

    earnings = [
        [Paragraph("<b>Earnings</b>", bold_style), Paragraph("<b>Amount (PKR)</b>", right_bold)],
        [Paragraph("Basic Salary", norm_style), Paragraph(f"{payroll.basic_salary:,.2f}", right_norm)],
        [Paragraph("Allowances", norm_style), Paragraph(f"{payroll.allowance:,.2f}", right_norm)],
        [Paragraph("Bonus / Special Pay", norm_style), Paragraph(f"{payroll.bonus:,.2f}", right_norm)],
        [Paragraph("<b>Total Gross Earnings</b>", bold_style), Paragraph(f"<b>{(payroll.basic_salary + payroll.allowance + payroll.bonus):,.2f}</b>", right_bold)],
    ]
    t_earn = Table(earnings, colWidths=[55 * mm, 35 * mm])
    t_earn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F0FDF4')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))

    deductions = [
        [Paragraph("<b>Deductions</b>", bold_style), Paragraph("<b>Amount (PKR)</b>", right_bold)],
        [Paragraph("General Deductions / Tax", norm_style), Paragraph(f"{payroll.deductions:,.2f}", right_norm)],
        [Paragraph("Advance Salary Recovery", norm_style), Paragraph(f"{payroll.advance_deduction:,.2f}", right_norm)],
        [Paragraph("—", norm_style), Paragraph("0.00", right_norm)],
        [Paragraph("<b>Total Deductions</b>", bold_style), Paragraph(f"<b>{(payroll.deductions + payroll.advance_deduction):,.2f}</b>", right_bold)],
    ]
    t_ded = Table(deductions, colWidths=[55 * mm, 35 * mm])
    t_ded.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DC2626')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FEF2F2')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))

    t_side = Table([[t_earn, t_ded]], colWidths=[90 * mm, 90 * mm])
    t_side.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_side)
    story.append(Spacer(1, 5 * mm))

    net_box = [
        [Paragraph("<b>NET SALARY PAYABLE:</b>", ParagraphStyle('NP', parent=bold_style, fontSize=12, textColor=PRIMARY_COLOR)),
         Paragraph(f"<b>PKR {payroll.net_salary:,.2f}</b>", ParagraphStyle('NPAmt', parent=right_bold, fontSize=13, textColor=SUCCESS_COLOR))]
    ]
    t_net = Table(net_box, colWidths=[90 * mm, 90 * mm])
    t_net.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF4FF')),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_net)
    story.append(Spacer(1, 15 * mm))

    sig_data = [
        [
            Paragraph("____________________________<br/><b>Employee Signature</b>", center_bold),
            Paragraph("____________________________<br/><b>Accountant / HR Manager</b>", center_bold),
            Paragraph(f"____________________________<br/><b>Principal Seal &amp; Signature</b>", center_bold),
        ]
    ]
    t_sig = Table(sig_data, colWidths=[60 * mm, 60 * mm, 60 * mm])
    story.append(t_sig)

    doc.build(story)
    buffer.seek(0)
    return buffer
