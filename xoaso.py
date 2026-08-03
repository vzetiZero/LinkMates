"""Xóa số SIM sau khi login"""
import os, sys, re
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from login import do_login

GMAIL_MAIN         = os.environ.get("GMAIL_MAIN", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
PROXY              = os.environ.get("PROXY", "")
mail_addr          = os.environ.get("ACC_MAIL", "")
passacc            = os.environ.get("ACC_PASSACC", "") or os.environ.get("ACC_PASSWORD", "")

session, csrf_name, csrf_value = do_login(mail_addr, passacc, GMAIL_MAIN, GMAIL_APP_PASSWORD, PROXY)

# Bước 1: lấy link xóa
getso = session.get("https://linksmate.jp/mypage/simcardadd/")
soup  = BeautifulSoup(getso.text, 'html.parser')
first_delete_link = soup.find('a', class_='simcardadd__delete-link')
if not first_delete_link:
    print("FAIL: Không tìm thấy link xóa số"); sys.exit(1)
link = first_delete_link.get('href')
print(f"[xoa-1] link: {link}")

# Bước 2: truy cập link xóa
session.get(f"https://linksmate.jp{link}")
print("[xoa-2] truy cập link ok")

# Bước 3: before
session.get("https://linksmate.jp/mypage/simcardadd/delete/before/")
print("[xoa-3] before ok")

# Bước 4: lấy ym và confirm xóa
getym = session.get("https://linksmate.jp/mypage/simcardadd/delete/confirm/").text
results = re.findall(r'"ym":\s*(\d{6})', getym)
if not results:
    print("FAIL: Không tìm thấy ym"); sys.exit(1)
ym = int(results[0])
print(f"[xoa-4] ym: {ym}")

r = session.post('https://linksmate.jp/mypage/simcardadd/delete/confirm/', data={
    "csrf_name": csrf_name, "csrf_value": csrf_value,
    "ym": ym, "lp_ok": "1",
    "agreeNoCancel": "1",
    "agreeCallChargeBillingTwoMonthsLater": "1",
    "agreeReturnSimCard": "1",
    "agreePaymentMethodLp": "1",
    "agreeCheck": "1",
})
print(f"DONE: Xóa số {r.url}")
