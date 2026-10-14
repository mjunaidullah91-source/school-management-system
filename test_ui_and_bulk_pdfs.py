import urllib.request, urllib.parse, http.cookiejar, re, sys

base = 'http://127.0.0.1:8000'
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("="*75)
print("  COMPREHENSIVE UI/UX, LAYOUT & BULK PDF AUDIT SUITE")
print("="*75)

# 1. Login as Admin
login_html = opener.open(f'{base}/login/').read().decode('utf-8')
csrf = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_html).group(1)
login_resp = opener.open(urllib.request.Request(
    f'{base}/login/',
    data=urllib.parse.urlencode({'csrfmiddlewaretoken': csrf, 'username': 'admin', 'password': 'admin'}).encode('utf-8'),
    headers={'Referer': f'{base}/login/'}
))
print(f"[1] Authentication: {'SUCCESS' if 'dashboard' in login_resp.url else 'FAILED'}")

# 2. Test Bulk PDF Endpoints
pdf_endpoints = [
    (f'{base}/results/bulk-class-pdf/', 'Bulk Result Cards (HD PDF)'),
    (f'{base}/results/bulk-class-pdf/?student_class=10&exam_type=Final&year=2026', 'Bulk Result Cards (Class 10 Filtered)'),
    (f'{base}/students/export/id-cards/', 'Bulk Student ID Cards (HD PDF)'),
    (f'{base}/students/export/id-cards/?student_class=10', 'Bulk Student ID Cards (Class 10 Filtered)'),
    (f'{base}/staff/export/id-cards/', 'Bulk Staff ID Cards (HD PDF)'),
    (f'{base}/fees/bulk-class-pdf/', 'Bulk Class Fee Challans (PDF)'),
]

print("\n[2] Bulk PDF Generation & ReportLab Verification:")
for url, label in pdf_endpoints:
    try:
        resp = opener.open(url)
        content_type = resp.headers.get('Content-Type', '')
        disp = resp.headers.get('Content-Disposition', '')
        data = resp.read()
        is_pdf = data.startswith(b'%PDF')
        print(f"    - {label}:")
        print(f"      * HTTP Status: {resp.status}")
        print(f"      * Content-Type: {content_type}")
        print(f"      * Filename Header: {disp}")
        print(f"      * PDF Valid Header (%PDF): {'YES' if is_pdf else 'NO'} ({len(data)} bytes) - PASS")
        assert is_pdf and len(data) > 1000, f"Expected valid PDF binary for {label}"
    except Exception as e:
        print(f"    - {label}: ERROR ({e})")
        sys.exit(1)

# 3. Test UI Pages for Prominent Bulk Action Buttons
ui_pages = [
    (f'{base}/results/', 'Results Ledger', ['Bulk Result Cards (HD PDF)', '/results/bulk-class-pdf/']),
    (f'{base}/students/', 'Students Directory', ['Bulk Student ID Cards (HD PDF)', '/students/export/id-cards/']),
    (f'{base}/staff/', 'Staff Directory', ['Bulk Staff ID Cards (HD PDF)', '/staff/export/id-cards/']),
    (f'{base}/search/?q=A', 'Search Results Page', ['Bulk ID Cards (HD PDF)', 'Bulk Result Cards (HD PDF)']),
    (f'{base}/dashboard/', 'Admin Command Center', ['topbar-left', 'topbar-search-form', 'dashboard-header', 'welcome-box']),
    (f'{base}/portal/accountant/', 'Accountant Portal', ['topbar-left', 'Finance & Accounts Workspace']),
    (f'{base}/portal/teacher/', 'Teacher Portal', ['topbar-left', 'portal-welcome']),
    (f'{base}/portal/student/', 'Student Portal', ['topbar-left', 'portal-welcome']),
]

print("\n[3] UI Layout, Flexbox Wrapper & Action Button Verification:")
for url, label, expected_tokens in ui_pages:
    try:
        resp = opener.open(url)
        html = resp.read().decode('utf-8', errors='ignore')
        missing = [tok for tok in expected_tokens if tok not in html]
        if missing:
            print(f"    - {label}: MISSING TOKENS {missing} - FAIL")
            sys.exit(1)
        else:
            print(f"    - {label}: All required layout elements & buttons present ({len(html)} bytes) - PASS")
    except Exception as e:
        print(f"    - {label}: ERROR ({e})")
        sys.exit(1)

# 4. Verify Static CSS for Topbar & Dashboard Wrappers
css_resp = opener.open(f'{base}/static/css/style.css')
css_text = css_resp.read().decode('utf-8')
css_checks = [
    '.topbar-left',
    '.topbar-search-form',
    '.topbar-title',
    '.dashboard-header',
    '.welcome-box',
    '.quick-actions-bar',
    '.portal-welcome',
    '@media (max-width: 1280px)',
    '@media (max-width: 992px)',
    '@media (max-width: 768px)',
    '@media (max-width: 576px)',
]
print("\n[4] CSS Layout & Responsive Breakpoint Verification:")
for cls in css_checks:
    if cls in css_text:
        print(f"    - CSS Rule '{cls}': FOUND - PASS")
    else:
        print(f"    - CSS Rule '{cls}': MISSING - FAIL")
        sys.exit(1)

print("\n" + "="*75)
print("  ALL UI/UX, LAYOUT & BULK PDF AUDIT TESTS COMPLETED SUCCESSFULLY (100% PASS)!")
print("="*75)
