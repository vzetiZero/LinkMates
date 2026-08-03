"""
Hàm login LinksMate dùng chung.
Trả về (session, csrf_name, csrf_value) hoặc raise Exception nếu thất bại.
"""
import os, sys, re, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test import get_linksmate_code_dynamic
from bs4 import BeautifulSoup

HEADERS_BASE = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'vi,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://linksmate.jp',
    'referer': 'https://linksmate.jp/mypage/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

def _parse(html, before, after='"', label=""):
    """Tách chuỗi an toàn, raise Exception rõ ràng nếu không tìm thấy."""
    if before not in html:
        raise Exception(f"FAIL: Không tìm thấy '{label or before}' trong HTML (có thể chưa login hoặc bị redirect)")
    return html.split(before)[1].split(after)[0]

def parse_csrf(html):
    return (
        _parse(html, 'name="csrf_name" value="',  '"', "csrf_name"),
        _parse(html, 'name="csrf_value" value="', '"', "csrf_value"),
    )

def parse_group_ids(html):
    """Lấy danh sách group_id có trên mypage/group_change form."""
    return [g["id"] for g in parse_groups(html)]

def parse_groups(html):
    """Lấy danh sách group theo đúng thứ tự hiển thị trên mypage."""
    soup = BeautifulSoup(html, "html.parser")
    groups = []

    def add_group(value, label=""):
        value = str(value or "").strip()
        if not value.isdigit() or any(g["id"] == value for g in groups):
            return
        label = " ".join(str(label or "").split())
        label = re.sub(r"\s+", " ", label).strip()
        groups.append({
            "order": len(groups) + 1,
            "id": value,
            "label": label,
        })

    for tag in soup.select('[name="group_id"]'):
        value = tag.get("value")
        label = ""
        if tag.parent:
            label = tag.parent.get_text(" ", strip=True)
        add_group(value, label)

    for form in soup.find_all("form"):
        action = form.get("action", "")
        if "group_change" not in action:
            continue
        for tag in form.select("[value]"):
            value = tag.get("value", "")
            label = tag.parent.get_text(" ", strip=True) if tag.parent else ""
            add_group(value, label)

    if not groups and "group_change" in html:
        for value in re.findall(r'value=["\'](\d+)["\']', html):
            add_group(value)

    return groups

def format_groups(groups):
    return " | ".join(f'{g["order"]}:{g["id"]}' for g in groups)

def change_group(session, group_id, csrf_name, csrf_value):
    group_id = str(group_id).strip()
    if not group_id:
        return csrf_name, csrf_value

    r = session.post("https://linksmate.jp/mypage/group_change/", data={
        "csrf_name": csrf_name,
        "csrf_value": csrf_value,
        "group_id": group_id,
    }, headers={
        "referer": "https://linksmate.jp/mypage/",
        "x-requested-with": "XMLHttpRequest",
    })
    print(f"[login] group_change {group_id}: {r.status_code} {r.url}")
    if r.status_code >= 400:
        raise Exception(f"FAIL: Đổi group {group_id} lỗi HTTP {r.status_code}")

    cc = session.get("https://linksmate.jp/mypage/")
    print(f"[login] mypage after group_change: {cc.url}")
    return parse_csrf(cc.text)

def do_login(mail_addr, passacc, gmail_main, gmail_app_pass, proxy="", group_id=None):
    if not mail_addr:
        raise Exception("FAIL: Chưa nhập email tài khoản")
    if not passacc:
        raise Exception("FAIL: Chưa nhập mật khẩu tài khoản")

    proxies = {}
    if proxy:
        parts = proxy.split(":")
        if len(parts) == 2:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        elif len(parts) == 4:
            proxies = {
                "http":  f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}",
                "https": f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
            }

    session = requests.Session()
    session.headers.update(HEADERS_BASE)
    if proxies:
        session.proxies.update(proxies)

    # Login
    r = session.post('https://linksmate.jp/api/mypage/login', data={
        'data[mail]': mail_addr,
        'data[password]': passacc,
    })
    resp_text = r.text[:300]
    print(f"[login] response: {resp_text}")
    if '"status":false' in r.text or 'error' in r.text.lower() and 'csrf' not in r.text:
        print(f"[login] cảnh báo: có thể sai mật khẩu")

    # Lấy verify code từ gmail
    code = get_linksmate_code_dynamic(gmail_main, gmail_app_pass, mail_addr)
    if not code:
        raise Exception("FAIL: Không lấy được code xác thực mail")
    print(f"[login] verify code: {code}")

    # Xác thực email
    r2 = session.post('https://linksmate.jp/email_verification/', data={'verify_code': code})
    print(f"[login] verify url: {r2.url}")

    # Lấy csrf từ mypage. Mặc định LinksMate trả về group đầu tiên.
    cc = session.get("https://linksmate.jp/mypage/")
    print(f"[login] mypage url: {cc.url}")

    csrf_name, csrf_value = parse_csrf(cc.text)

    groups = parse_groups(cc.text)
    print(f"[login] groups found: {format_groups(groups) if groups else 'none'}")

    group_id = str(group_id if group_id is not None else os.environ.get("ACC_GROUP_ID", "")).strip()
    if group_id:
        group_ids = [g["id"] for g in groups]
        if group_ids and group_id not in group_ids:
            raise Exception(f"FAIL: Không tìm thấy group_id {group_id} trong tài khoản này")
        csrf_name, csrf_value = change_group(session, group_id, csrf_name, csrf_value)

    return session, csrf_name, csrf_value
