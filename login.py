"""
Hàm login LinksMate dùng chung.
Trả về (session, csrf_name, csrf_value) hoặc raise Exception nếu thất bại.
"""
import os, sys, re, requests
from datetime import datetime, timezone, timedelta
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

def parse_account_info(html):
    """Parse các thông tin account phổ biến từ HTML mypage/form nếu có."""
    soup = BeautifulSoup(html, "html.parser")
    info = {}

    def clean_text(value):
        return re.sub(r"\s+", " ", str(value or "").replace("\u3000", " ")).strip()

    def set_if_value(key, value):
        value = clean_text(value)
        if value:
            info[key] = value

    def split_name(value, first_key="ho", second_key="ten"):
        value = clean_text(value)
        if not value:
            return
        parts = value.split()
        if len(parts) >= 2:
            set_if_value(first_key, parts[0])
            set_if_value(second_key, " ".join(parts[1:]))
        elif first_key not in info:
            set_if_value(first_key, value)

    def map_label_value(label, value):
        label = clean_text(label)
        value = clean_text(value)
        if not label or not value:
            return
        upper_label = label.upper()
        if (any(k in label for k in ("氏名", "お名前", "名前", "契約者名"))
                or "TÊN NGƯỜI ĐỨNG TÊN HỢP ĐỒNG" in upper_label) \
                and not any(k in label for k in ("カナ", "フリガナ", "ローマ")):
            split_name(value, "ho", "ten")
        elif any(k in label for k in ("フリガナ", "カナ")) or "CÁCH PHÁT ÂM" in upper_label:
            split_name(value, "hophienam", "tenphienam")
        elif (any(k in label for k in ("ローマ", "英字")) or "ROMAJI" in upper_label
              or "LA MÃ" in upper_label or "LATIN" in upper_label):
            split_name(value, "ho1", "ten1")
        elif any(k in label for k in ("郵便", "〒")) or "MÃ BƯU ĐIỆN" in upper_label:
            set_if_value("mabuudien", value)
        elif "住所" in label or "ĐỊA CHỈ" in upper_label:
            set_if_value("diachi", value)
            zip_match = re.search(r"\b\d{7}\b", value)
            if zip_match:
                set_if_value("mabuudien", zip_match.group(0))
        elif "EID" in upper_label:
            set_if_value("eid", value)
        elif (any(k in label for k in ("電話番号", "携帯電話", "連絡先電話", "SIMカード電話番号"))
              or "SỐ ĐIỆN THOẠI" in upper_label):
            set_if_value("sdt", value)

    input_map = {
        "familyname": "ho",
        "firstname": "ten",
        "familyname_romaji": "ho1",
        "firstname_romaji": "ten1",
        "familyname_kana": "hophienam",
        "firstname_kana": "tenphienam",
        "postal_code": "mabuudien",
        "eid": "eid",
    }

    for input_name, key in input_map.items():
        tag = soup.find(["input", "select", "textarea"], {"name": input_name})
        if tag:
            value = tag.get("value", "") if tag.name != "textarea" else tag.get_text(strip=True)
            set_if_value(key, value)

    # Các trang hồ sơ có thể dùng family_name/first_name hoặc name lồng nhau
    # thay vì đúng các tên field ở form đăng ký. Chuẩn hóa để đọc được cả hai.
    input_aliases = {
        "familyname": "ho",
        "firstname": "ten",
        "familynamekana": "hophienam",
        "firstnamekana": "tenphienam",
        "familynameromaji": "ho1",
        "firstnameromaji": "ten1",
        "postalcode": "mabuudien",
        "postcode": "mabuudien",
    }
    for tag in soup.find_all(["input", "select", "textarea"]):
        raw_name = " ".join(str(tag.get(attr, "")) for attr in ("name", "id", "data-name"))
        normalized_name = re.sub(r"[^a-z0-9]", "", raw_name.lower())
        if not normalized_name:
            continue
        key = next((mapped_key for alias, mapped_key in input_aliases.items()
                    if normalized_name.endswith(alias)), None)
        if not key:
            continue
        value = tag.get("value", "") if tag.name != "textarea" else tag.get_text(strip=True)
        if value and key not in info:
            set_if_value(key, value)

    address_parts = []
    for input_name in ("prefecture", "city", "address", "address2"):
        tag = soup.find(["input", "select", "textarea"], {"name": input_name})
        if not tag:
            continue
        value = tag.get("value", "") if tag.name != "textarea" else tag.get_text(strip=True)
        value = clean_text(value)
        if value:
            address_parts.append(value)
    if address_parts:
        info["diachi"] = " ".join(address_parts)

    for dt in soup.find_all("dt"):
        dd = dt.find_next_sibling("dd")
        if dd:
            map_label_value(dt.get_text(" ", strip=True), dd.get_text(" ", strip=True))

    for th in soup.find_all("th"):
        td = th.find_next_sibling("td")
        if td:
            map_label_value(th.get_text(" ", strip=True), td.get_text(" ", strip=True))

    for td in soup.select("td[data-label]"):
        map_label_value(td.get("data-label", ""), td.get_text(" ", strip=True))

    # Trang registrationinfo hiển thị label/value bằng thẻ <p> lồng nhau,
    # nên không thể đọc bằng cặp dt/dd hoặc th/td thông thường.
    for row in soup.select(
        ".mypage-registrationinfo__group-row, "
        ".mypage-registrationinfo__group-row-other"
    ):
        label_el = row.select_one(".mypage-registrationinfo__group-row-name")
        value_el = row.select_one(".mypage-registrationinfo__group-row-value")
        if label_el and value_el:
            map_label_value(
                label_el.get_text(" ", strip=True),
                value_el.get_text(" ", strip=True)
            )

    for label in soup.find_all(["label", "span", "div"], string=True):
        label_text = clean_text(label.get_text(" ", strip=True))
        if not label_text or len(label_text) > 40:
            continue
        parent = label.parent
        if not parent:
            continue
        value_text = clean_text(parent.get_text(" ", strip=True).replace(label_text, "", 1))
        map_label_value(label_text, value_text)

    lp_el = soup.select_one("#available_lp .mypage-lp__available-value")
    if lp_el:
        # Số dư LinksPoint khác với mã LP 6 chữ số được tạo khi charge.
        set_if_value("lp_balance", lp_el.get_text(strip=True))

    return info

def change_group(session, group_id, csrf_name, csrf_value, return_page=False):
    group_id = str(group_id).strip()
    if not group_id:
        return (csrf_name, csrf_value, None) if return_page else (csrf_name, csrf_value)

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
    next_csrf_name, next_csrf_value = parse_csrf(cc.text)
    if return_page:
        return next_csrf_name, next_csrf_value, cc
    return next_csrf_name, next_csrf_value

def do_login(mail_addr, passacc, gmail_main, gmail_app_pass, proxy="", group_id=None, return_page=False):
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

    cc = None
    last_error = None
    for login_attempt in range(2):
        login_started = datetime.now(timezone.utc) - timedelta(seconds=5)
        r = session.post('https://linksmate.jp/api/mypage/login', data={
            'data[mail]': mail_addr,
            'data[password]': passacc,
        })
        resp_text = r.text[:300]
        print(f"[login] response: {resp_text}")
        if '"status":false' in r.text or 'error' in r.text.lower() and 'csrf' not in r.text:
            print(f"[login] cảnh báo: có thể sai mật khẩu")

        code = get_linksmate_code_dynamic(gmail_main, gmail_app_pass, mail_addr, not_before_utc=login_started)
        if not code:
            raise Exception("FAIL: Không lấy được code xác thực mail")
        print(f"[login] verify code: {code}")

        r2 = session.post('https://linksmate.jp/email_verification/', data={'verify_code': code})
        print(f"[login] verify url: {r2.url}")

        cc = session.get("https://linksmate.jp/mypage/")
        print(f"[login] mypage url: {cc.url}")
        try:
            csrf_name, csrf_value = parse_csrf(cc.text)
            break
        except Exception as e:
            last_error = e
            if "login" in cc.url and login_attempt == 0:
                print("[login] verify chưa vào được mypage, thử lấy OTP mới lần 2")
                continue
            raise
    else:
        raise last_error or Exception("FAIL: Login không vào được mypage")

    groups = parse_groups(cc.text)
    print(f"[login] groups found: {format_groups(groups) if groups else 'none'}")

    group_id = str(group_id if group_id is not None else os.environ.get("ACC_GROUP_ID", "")).strip()
    if group_id:
        group_ids = [g["id"] for g in groups]
        if group_ids and group_id not in group_ids:
            raise Exception(f"FAIL: Không tìm thấy group_id {group_id} trong tài khoản này")
        csrf_name, csrf_value = change_group(session, group_id, csrf_name, csrf_value)

    if return_page:
        return session, csrf_name, csrf_value, cc
    return session, csrf_name, csrf_value
