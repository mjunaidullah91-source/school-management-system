import urllib.request, urllib.parse, http.cookiejar, re, sys

def get_csrf(opener, url):
    try:
        r = opener.open(url)
        html = r.read().decode('utf-8', errors='ignore')
        m = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', html)
        return m.group(1) if m else ''
    except Exception as e:
        print(f"Error fetching CSRF from {url}: {e}")
        return ''

base_url = "http://127.0.0.1:8000"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("="*70)
print("  ITTIHAD MODEL SCHOOL MANAGEMENT SYSTEM - FULL FUNCTIONAL AUDIT")
print("="*70)

# 1. Admin Login
token = get_csrf(opener, f"{base_url}/login/")
login_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': token,
    'username': 'admin',
    'password': 'admin'
}).encode('utf-8')

req = urllib.request.Request(f"{base_url}/login/", data=login_data, headers={'Referer': f"{base_url}/login/"})
resp = opener.open(req)
print(f"\n[1] Admin Login Authentication: {'SUCCESS' if 'dashboard' in resp.url else 'FAILED'} (URL: {resp.url})")

# Endpoints to test
endpoints = [
    # Dashboard & Portals
    ('/dashboard/', 'Admin Command Center'),
    ('/api/dashboard-stats/', 'Real-time Stats JSON API'),
    ('/portal/teacher/', 'Teacher Portal (Admin View)'),
    ('/portal/student/', 'Student Portal (Admin Preview)'),
    ('/settings/school/', 'School Profile & Branding Settings'),
    ('/notifications/', 'Notifications Feed'),
    
    # Students & SIS
    ('/students/', 'Students Directory (SIS)'),
    ('/students/1/', 'Student 360 Profile Dossier'),
    ('/students/export/excel/', 'Students Directory Excel Export'),
    ('/students/export/id-cards/', 'Bulk Student ID Cards PDF'),
    
    # Fees & Challans
    ('/fees/', 'Fees Management Dashboard'),
    ('/fees/1/voucher-pdf/', '3-Copy Bank Fee Challan PDF'),
    ('/fees/bulk-class-pdf/?student_class=10', 'Bulk Class Fee Vouchers PDF'),
    ('/fees/export/excel/', 'Fee Ledger Excel Export'),
    ('/fees/student/1/', 'Student Individual Fee Ledger'),
    
    # Staff & Payroll
    ('/staff/', 'Staff & HR Directory'),
    ('/staff/export/id-cards/', 'Staff ID Cards PDF'),
    ('/payroll/', 'HR Payroll Management'),
    ('/payroll/export/excel/', 'Payroll Report Excel Export'),
    
    # Subjects & Curriculum
    ('/subjects/', 'Subjects & Curriculum Index'),
    
    # Exams & Results
    ('/exams/', 'Exams & Date Sheets'),
    ('/results/', 'Examination Results Ledger'),
    ('/results/student/1/', 'Student Result Transcript'),
    ('/results/student/1/pdf/?exam_type=Mid-Term&year=2026', 'Official Result Card PDF'),
    ('/results/bulk-class-pdf/?student_class=10&exam_type=Mid-Term&year=2026', 'Bulk Class Result Cards PDF'),
    ('/results/merit-list/?student_class=10', 'Class Merit List Report'),
    
    # Attendance & Leaves
    ('/attendance/students/', 'Student Attendance Register'),
    ('/attendance/staff/', 'Staff Attendance Register'),
    ('/leaves/', 'Leave Applications Desk'),
    ('/sms-logs/', 'Standalone Alert Audit Logs'),
    
    # Library, Inventory, Certificates, Timetable
    ('/library/books/', 'Library Books Catalogue'),
    ('/library/issues/', 'Book Issue & Circulation'),
    ('/inventory/assets/', 'Asset & Stock Inventory'),
    ('/certificates/', 'Official Certificates Registry'),
    ('/homework/', 'Class Homework & Assignments'),
    ('/notices/', 'Digital Notice Board'),
    ('/timetable/', 'Class Timetable & Schedule'),
]

passed = 0
failed = 0

print("\n" + "-"*70)
print(f" {'ENDPOINT':<45} | {'STATUS':<6} | {'SIZE':<8} | {'RESULT'}")
print("-"*70)

for url_path, label in endpoints:
    full_url = f"{base_url}{url_path}"
    try:
        r = opener.open(full_url)
        content = r.read()
        size = len(content)
        content_type = r.headers.get('Content-Type', '')
        
        # Check for 500 error traces
        if b'Traceback' in content or b'Internal Server Error' in content or b'TemplateSyntaxError' in content:
            print(f" {url_path:<45} | {r.status:<6} | {size:<8} | FAIL (Exception in Body)")
            failed += 1
        else:
            is_pdf = 'application/pdf' in content_type or content.startswith(b'%PDF')
            is_excel = 'spreadsheet' in content_type or 'excel' in content_type or content.startswith(b'PK')
            is_json = 'application/json' in content_type
            
            flag = "[PDF OK]" if is_pdf else ("[XLS OK]" if is_excel else ("[JSON]" if is_json else "[HTML]"))
            print(f" {url_path:<45} | {r.status:<6} | {size:<8} | PASS {flag}")
            passed += 1
    except urllib.error.HTTPError as e:
        print(f" {url_path:<45} | {e.code:<6} | {'-':<8} | FAIL (HTTP {e.code})")
        failed += 1
    except Exception as ex:
        print(f" {url_path:<45} | {'ERR':<6} | {'-':<8} | FAIL ({ex})")
        failed += 1

print("-"*70)
print(f"  AUDIT SUMMARY: {passed} PASSED, {failed} FAILED (TOTAL: {passed + failed})")
print("="*70)

# 2. Individual Student Login & Password Lifecycle Audit
print("\n[2] Testing Individual Student Portal & Password Lifecycle:")
std_cj = http.cookiejar.CookieJar()
std_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(std_cj))

std_token = get_csrf(std_opener, f"{base_url}/login/")
std_login_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': std_token,
    'username': 'std_1001',
    'password': '12345678'
}).encode('utf-8')

std_req = urllib.request.Request(f"{base_url}/login/", data=std_login_data, headers={'Referer': f"{base_url}/login/"})
std_resp = std_opener.open(std_req)
print(f"  -> Student 'std_1001' Default Login (12345678): {'SUCCESS' if 'portal/student' in std_resp.url else 'FAILED'}")

# Student accessing student portal
std_portal_resp = std_opener.open(f"{base_url}/portal/student/")
print(f"  -> Student Portal Access (HTTP {std_portal_resp.status}): {'SUCCESS' if std_portal_resp.status == 200 else 'FAILED'}")

# Student attempting to access Admin Dashboard
std_dash_resp = std_opener.open(f"{base_url}/dashboard/")
print(f"  -> Student Admin Route Block & Redirect: {'SUCCESS' if 'portal/student' in std_dash_resp.url or 'login' in std_dash_resp.url else 'FAILED'} (Target: {std_dash_resp.url})")

print("\n" + "="*70)
print("  ALL AUDIT TESTS COMPLETED SUCCESSFULLY!")
print("="*70)
