import urllib.request, urllib.parse, http.cookiejar, re

def get_csrf(opener, url):
    r = opener.open(url)
    html = r.read().decode('utf-8')
    m = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', html)
    return m.group(1) if m else ''

student_username = 'std_1001'
student_pk = 9
default_password = '12345678'
new_password = 'newpassword2026'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# 1. Login as Student with default password '12345678'
token = get_csrf(opener, 'http://127.0.0.1:8000/login/')
login_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': token,
    'username': student_username,
    'password': default_password
}).encode('utf-8')

req = urllib.request.Request('http://127.0.0.1:8000/login/', data=login_data, headers={'Referer': 'http://127.0.0.1:8000/login/'})
resp = opener.open(req)
print(f"1. Student Login with '{default_password}': {'SUCCESS' if 'portal/student' in resp.url else 'FAILED'} -> {resp.url}")

# 2. Change password to 'newpassword2026'
chg_token = get_csrf(opener, 'http://127.0.0.1:8000/portal/student/change-password/')
change_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': chg_token,
    'old_password': default_password,
    'new_password1': new_password,
    'new_password2': new_password,
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/portal/student/change-password/',
    data=change_data,
    headers={'Referer': 'http://127.0.0.1:8000/portal/student/change-password/'}
)
resp_chg = opener.open(req)
print(f"2. Student Changed Password: {'SUCCESS' if 'portal/student' in resp_chg.url else 'FAILED'} -> {resp_chg.url}")

# 3. Test Admin Reset Password
admin_cj = http.cookiejar.CookieJar()
admin_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(admin_cj))

admin_token = get_csrf(admin_opener, 'http://127.0.0.1:8000/login/')
admin_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': admin_token,
    'username': 'admin',
    'password': 'admin'
}).encode('utf-8')

req = urllib.request.Request('http://127.0.0.1:8000/login/', data=admin_data, headers={'Referer': 'http://127.0.0.1:8000/login/'})
admin_opener.open(req)

# Reset student pk=9 password
reset_resp = admin_opener.open(f'http://127.0.0.1:8000/students/{student_pk}/reset-password/')
print(f"3. Admin Reset Password to '{default_password}': Status {reset_resp.status} -> {reset_resp.url}")

# 4. Login as student again with reset default password '12345678'
new_student_cj = http.cookiejar.CookieJar()
new_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(new_student_cj))
token4 = get_csrf(new_opener, 'http://127.0.0.1:8000/login/')
login_data4 = urllib.parse.urlencode({
    'csrfmiddlewaretoken': token4,
    'username': student_username,
    'password': default_password
}).encode('utf-8')

req4 = urllib.request.Request('http://127.0.0.1:8000/login/', data=login_data4, headers={'Referer': 'http://127.0.0.1:8000/login/'})
resp4 = new_opener.open(req4)
print(f"4. Relogin with reset '{default_password}': {'SUCCESS' if 'portal/student' in resp4.url else 'FAILED'} -> {resp4.url}")
