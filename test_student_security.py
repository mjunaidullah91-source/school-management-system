import urllib.request, urllib.parse, http.cookiejar, re

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# 1. Access Login Page
r = opener.open('http://127.0.0.1:8000/login/')
html = r.read().decode('utf-8')
m = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', html)
token = m.group(1) if m else ''

# 2. Login as Individual Student std_ims-001
post_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': token,
    'username': 'std_ims-001',
    'password': 'ims_ims-001'
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/login/',
    data=post_data,
    headers={'Referer': 'http://127.0.0.1:8000/login/'}
)

resp = opener.open(req)
print(f"Student Login Target URL: {resp.url}")

# 3. View Student Portal
portal_resp = opener.open('http://127.0.0.1:8000/portal/student/')
portal_content = portal_resp.read().decode('utf-8')
print(f"Portal Status: {portal_resp.status} | Content Length: {len(portal_content)}")

# 4. Check if student name is present in their portal
if "std_ims-001" in portal_content or "Muhammad Ali" in portal_content or "Roll No: IMS-001" in portal_content:
    print("SUCCESS: Student's personal records loaded in Portal!")

# 5. Verify security: Student trying to open Admin Dashboard
dash_resp = opener.open('http://127.0.0.1:8000/dashboard/')
print(f"Accessing /dashboard/ redirected to: {dash_resp.url}")
if "portal/student" in dash_resp.url:
    print("SUCCESS: Student was blocked from Admin Dashboard and redirected to Student Portal!")
