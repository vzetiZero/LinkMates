"""
Tạo tài khoản LinksMate
Nhận biến môi trường từ GUI:
  ACC_MAIL, ACC_PASSMAIL, ACC_PASSACC, ACC_HO, ACC_TEN, ACC_HO1, ACC_TEN1
  ACC_HOPHIENAM, ACC_TENPHIENAM, ACC_MABUUDIEN, ACC_DIACHI, ACC_SDT
  GMAIL_MAIN, GMAIL_APP_PASSWORD, PREFECTURE, CITY, ADDRESS, ACC_PASSWORD, PROXY
"""
import os, sys, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test import get_linksmate_code_dynamic

GMAIL_MAIN        = os.environ.get("GMAIL_MAIN", "")
GMAIL_APP_PASSWORD= os.environ.get("GMAIL_APP_PASSWORD", "")
PREFECTURE        = os.environ.get("PREFECTURE", "東京都")
CITY              = os.environ.get("CITY", "千代田区丸の内")
ADDRESS           = os.environ.get("ADDRESS", "1-1")
ACC_PASSWORD      = os.environ.get("ACC_PASSWORD", "Pass@12345")
PROXY             = os.environ.get("PROXY", "")

mail_addr   = os.environ.get("ACC_MAIL", "")
passmail    = os.environ.get("ACC_PASSMAIL", "")
ho          = os.environ.get("ACC_HO", "ｙａｍａｔｅ")
ten         = os.environ.get("ACC_TEN", "ｙａｍａｔｅ")
ho1         = os.environ.get("ACC_HO1", "フリガナ")
ten1        = os.environ.get("ACC_TEN1", "フリガナ")
hophienam   = os.environ.get("ACC_HOPHIENAM", "YAMATE")
tenphienam  = os.environ.get("ACC_TENPHIENAM", "YAMATE")
mabuudien   = os.environ.get("ACC_MABUUDIEN", "5008286")
diachi      = os.environ.get("ACC_DIACHI", ADDRESS)
sdt         = os.environ.get("ACC_SDT", "09012345673")
passacc     = os.environ.get("ACC_PASSACC", "") or ACC_PASSWORD

proxies = {}
if PROXY:
    parts = PROXY.split(":")
    if len(parts) == 2:
        proxies = {"http": f"http://{PROXY}", "https": f"http://{PROXY}"}
    elif len(parts) == 4:
        proxies = {"http": f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}",
                   "https": f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"}

HEADERS = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'vi,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://linksmate.jp',
    'referer': 'https://linksmate.jp/p',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

session = requests.Session()
if proxies:
    session.proxies.update(proxies)

# Bước 1: lấy csrf
cc = session.get("https://linksmate.jp/preorder/").text
csrf_name  = cc.split('name="csrf_name" value="')[1].split('"')[0]
csrf_value = cc.split('name="csrf_value" value="')[1].split('"')[0]
print(f"[1] csrf ok: {csrf_name}")

# Bước 2: accept personal info
session.post('https://linksmate.jp/preorder/userinfo/', headers=HEADERS, data={
    'csrf_name': csrf_name, 'csrf_value': csrf_value,
    'accept_dealing_with_personal_information': '1',
})
print("[2] accept ok")

# Bước 3: gửi code mail
r = session.post('https://linksmate.jp/api/mail/send_verification_code/', headers=HEADERS, data={
    'mail_local_part': mail_addr, 'csrf_name': csrf_name, 'csrf_value': csrf_value,
}).json()
print(f"[3] send mail: {r}")

# Bước 4: lấy code từ gmail
codemail = get_linksmate_code_dynamic(GMAIL_MAIN, GMAIL_APP_PASSWORD, mail_addr)
if not codemail:
    print("FAIL: không lấy được code mail"); sys.exit(1)
print(f"[4] code: {codemail}")

# Bước 5: xác minh thông tin
data={
    'csrf_name': csrf_name, 'csrf_value': csrf_value,
    'familyname': ho, 'firstname': ten,
    'familyname_kana': hophienam, 'firstname_kana': tenphienam,
    'familyname_romaji': ho1, 'firstname_romaji': ten1,
    'birthday_year': '1993', 'birthday_month': '10', 'birthday_day': '27',
    'sex': '1',
    'postal_code': mabuudien,
    'prefecture': PREFECTURE, 'city': CITY, 'address': diachi,
    'address2': '',
    'contactphone': sdt,
    'mail_local_part': mail_addr,
    'mail_verification_code': codemail,
    'password': passacc, 'password_confirm': passacc,
    'receive_mails': '1',
}
cc = session.post('https://linksmate.jp/preorder/confirm/', headers=HEADERS, data=data)
print("[5] confirm ok")
with open("2.html", "w", encoding="utf-8") as f:
                f.write(cc.text)
with open("data.html", "w", encoding="utf-8") as f:
    f.write(str(data)) # Ép thẳng dict thành chuỗi chữ
# Bước 6: hoàn tất đăng ký
r = session.post('https://linksmate.jp/preorder/complete/', headers=HEADERS, data={
    'csrf_name': csrf_name, 'csrf_value': csrf_value,
    'accept_terms_of_service': '1',
    'accept_dealing_with_personal_information': '1',
    'accept_lp_payment': '1',
    'accept_game_connect': '1',
    'confirm_input_correct': '1',
}).text
with open("1.html", "w", encoding="utf-8") as f:
                f.write(r)

if 'complete' in r.lower() or 'ありがとう' in r or '完了' in r:
    print("DONE: Tạo tài khoản thành công")
else:
    print("DONE: Đã gửi đăng ký")

