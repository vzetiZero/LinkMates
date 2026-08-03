"""Nhiệm vụ 3: Thêm SIM card + cập nhật EID sau khi login"""
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

# Bước 1: order SIM
r = session.post('https://linksmate.jp/mypage/simcardadd/add/order/', data={
    "csrf_name": csrf_name, "csrf_value": csrf_value,
    "payment_method_type": "2",
    "sim[0][sim_type]": "1", "sim[0][mnp]": "0",
    "sim[0][mnp_in_code]": "", "sim[0][mnp_number_key]": "",
    "installment": "0",
    "sim[0][select-terminal-os]": "iOS",
    "sim[0][select-terminal-maker]": "Apple",
    "sim[0][select-terminal-name]": "10.5インチiPad Pro ドコモ版 [A1709]",
    "sim[0][sim_for_terminal]": "", "sim[0][sim_size]": "3",
    "sim[0][add_line_of_5g]": "1", "sim[0][other_uses_sim_card]": "0",
    "sim[0][sim_user_familyname]": "", "sim[0][sim_user_firstname]": "",
    "sim[0][sim_user_familyname_kana]": "", "sim[0][sim_user_firstname_kana]": "",
    "delivery_day": "0", "delivery_time": "", "ym": "202605", "lp_ok": "1",
})
print(f"[3-1] order: {r.url}")

# Bước 2: confirm order
r = session.post('https://linksmate.jp/mypage/simcardadd/add/confirm/', data={
    "csrf_name": csrf_name, "csrf_value": csrf_value,
    "accept_important_concern": "1", "accept_terms_of_service": "1",
    "agreeDriversLicenseProvide": "1", "accept_line_of_5g_concern": "1",
    "accept_mate_phone_concern": "1", "agreeNoCancel": "1",
    "agreePayment": "1", "agreeExitFee": "1", "agreeConfirmedTerminal": "1",
    "confirm_validated_5g_terminal": "1", "confirm_validated_esim": "1",
    "confirm_esim_terminal": "1", "confirm_eid_input": "1",
    "agreePaymentMethodLp": "1", "agreeCheck": "1",
})
print(f"[3-2] confirm order: {r.url}")

# Bước 3: first payment
cc1 = session.get("https://linksmate.jp/api/mypage/notice/").text
checked_date = _parse(cc1, 'name="checked_date" value="', '"', "checked_date")
order_id     = _parse(cc1, 'name="order_id" value="',     '"', "order_id")
r = session.post('https://linksmate.jp/mypage/order/first_payment/', data={
    'csrf_name': csrf_name, 'csrf_value': csrf_value,
    'checked_date': checked_date, 'order_id': order_id,
})
print(f"[3-3] payment: {r.url}")

# Bước 4: update EID
cc2 = session.get("https://linksmate.jp/mypage/eid/").text
simSequenceId = _parse(cc2, '/mypage/eid/update/?simSequenceId=', '"', "simSequenceId")
r = session.post('https://linksmate.jp/mypage/eid/update/', data={
    'eid': EID, 'eid_confirm': EID, 'sim_sequence_id': simSequenceId,
})
print(f"[3-4] eid update: {r.url}")

# Bước 5: confirm EID
r = session.post('https://linksmate.jp/mypage/eid/confirm/', data={
    'new_eid': EID, 'sim_sequence_id': simSequenceId,
})
print(f"DONE: EID confirm {r.url}")
