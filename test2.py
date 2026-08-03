"""Nhiệm vụ 2: Cập nhật EID sau khi login"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from login import do_login, _parse

GMAIL_MAIN         = os.environ.get("GMAIL_MAIN", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
PROXY              = os.environ.get("PROXY", "")
mail_addr          = os.environ.get("ACC_MAIL", "")
passacc            = os.environ.get("ACC_PASSACC", "") or os.environ.get("ACC_PASSWORD", "")
EID                = os.environ.get("ACC_EID", "89049032005008882600042119686315")

session, csrf_name, csrf_value = do_login(mail_addr, passacc, GMAIL_MAIN, GMAIL_APP_PASSWORD, PROXY)
cc1 = session.get("https://linksmate.jp/api/mypage/notice/").text
checked_date = cc1.split('name="checked_date" value="')[1].split('"')[0]
order_id = cc1.split('name="order_id" value="')[1].split('"')[0]
print(checked_date,order_id)
data = {
    'csrf_name': csrf_name,
    'csrf_value': csrf_value,
    'checked_date': checked_date,
    'order_id': order_id,
}

response = session.post('https://linksmate.jp/mypage/order/first_payment/', data=data)
print(response.text)
print(response.url)
# Bước 1: lấy simSequenceId
cc2 = session.get("https://linksmate.jp/mypage/eid/").text
simSequenceId = _parse(cc2, '/mypage/eid/update/?simSequenceId=', '"', "simSequenceId")
print(f"[2-1] simSequenceId: {simSequenceId}")

# Bước 2: update EID
r = session.post('https://linksmate.jp/mypage/eid/update/', data={
    'eid': EID, 'eid_confirm': EID, 'sim_sequence_id': simSequenceId,
})
print(f"[2-2] update: {r.url}")

# Bước 3: confirm EID
r = session.post('https://linksmate.jp/mypage/eid/confirm/', data={
    'new_eid': EID, 'sim_sequence_id': simSequenceId,
})
print(f"DONE: EID confirm {r.url}")
