import urllib.request, urllib.parse, http.cookiejar, re

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Get CSRF token
r = opener.open('http://localhost:8000/login/')
html = r.read().decode()
m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
if not m:
    m = re.search(r"name='csrfmiddlewaretoken' value='([^']+)'", html)
if not m:
    m = re.search(r'csrfmiddlewaretoken["\'][^>]*value=["\']([^"\']+)', html)

token = m.group(1) if m else ''
print('CSRF:', bool(token))

# Login
data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': token,
    'username': 'admin',
    'password': 'admin'
}).encode()
req = urllib.request.Request(
    'http://localhost:8000/login/',
    data=data,
    headers={'Referer': 'http://localhost:8000/login/'}
)
try:
    r = opener.open(req)
    print('Login OK -> URL:', r.url)
except urllib.error.HTTPError as e:
    print('Login HTTP Error:', e.code)

# Dashboard
try:
    r = opener.open('http://localhost:8000/dashboard/')
    content = r.read().decode()
    print('Dashboard: HTTP', r.status, '| Size:', len(content), 'bytes')
    if 'Traceback' in content or 'TemplateSyntaxError' in content or 'Exception' in content:
        print('\n=== ERROR IN DASHBOARD ===')
        print(content[:3000])
    else:
        print('Dashboard loaded successfully!')
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print('Dashboard ERROR:', e.code)
    print(body[:3000])
