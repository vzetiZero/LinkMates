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

# Bước 1: order selectplan
r = session.post('https://linksmate.jp/order/selectplan/', data={
    "csrf_name": csrf_name, 
    "csrf_value": csrf_value,
    "accept_dealing_with_personal_information": "1",
    "coupon-option": "0", 
})
print(f"[1-1] order: {r.url}")

# Bước 2: order userinfo
r= session.post('https://linksmate.jp/order/userinfo/', data={
    "csrf_name": csrf_name, 
    "csrf_value": csrf_value,
    "payment_method_type": "2",
    "sim[0][sim_type]": "1",
    "plan": "104857600",
    "sim[0][mnp]": "0",
    "sim[0][mnp_in_code]": "",
    "sim[0][mnp_number_key]": "",
    "terminal": "0",
    "installment": "0",
    "sim[0][sim_size]": "3",
    "sim[0][select-terminal-os]": "iOS",
    "sim[0][select-terminal-maker]": "Apple",
    "sim[0][select-terminal-name]": "11インチiPad Pro (第3世代) SIMフリー版 [A2459]",
    "sim[0][sim_for_terminal]": "",
    "sim[0][add_line_of_5g]": "1",
    "prefecture_cd": "20",
    "use_logined_user": "1",
    "accept_dealing_with_personal_information": "1",
    "coupon-option": "0",
    "fixed_minimum_lp": "{\"connect_group_master\":[{\"id\":-1,\"group_name\":\"新規グループ\",\"monthly_payment_target_ym_after_next\":202607,\"connect_monthly_billing\":{\"billing_detail\":[{\"item_name\":\"100MBプラン (音声通話あり・SMSあり)\",\"order\":-1,\"tax_rate\":\"10.0\",\"sum_price\":470,\"user_memo\":null,\"item_name_with_user_memo\":\"100MBプラン (音声通話あり・SMSあり)\"},{\"item_id\":2008,\"item_name\":\"ユニバーサルサービス料等\",\"order\":10,\"tax_rate\":\"10.0\",\"sum_price\":3,\"user_memo\":null,\"item_name_with_user_memo\":\"ユニバーサルサービス料等\",\"display_unit_price\":null,\"sim_sequence_id\":\"-2\"},{\"item_id\":2015,\"item_name\":\"5G回線オプション\",\"order\":35,\"tax_rate\":\"10.0\",\"sum_price\":0,\"user_memo\":null,\"item_name_with_user_memo\":\"5G回線オプション\",\"display_unit_price\":null,\"sim_sequence_id\":\"-2\"}],\"amount_without_tax\":473,\"tax\":47,\"amount\":520,\"payment_ym\":202606,\"without_order\":{\"billing_detail\":[],\"amount_without_tax\":0,\"tax\":0,\"amount\":0,\"payment_ym\":202606,\"without_order\":null}},\"connect_once_billing\":{\"billing_detail\":[],\"amount_without_tax\":0,\"tax\":0,\"amount\":0,\"payment_ym\":0,\"without_order\":null},\"ym_to_additional_call_billing\":{}}],\"ym\":202605,\"total_lp_amount\":0,\"call_charge_lps\":{\"ym\":{},\"all\":[],\"amount\":0},\"available_lp_amount\":0,\"minimum_lp_amount\":0,\"is_first_order\":true,\"order_group_id\":-1,\"connect_once_billing\":{\"billing_detail\":[{\"item_name\":\"100MBプラン (音声通話あり・SMSあり)\",\"order\":-1,\"tax_rate\":\"10.0\",\"sum_price\":344,\"user_memo\":null,\"item_name_with_user_memo\":\"100MBプラン (音声通話あり・SMSあり)\"},{\"item_id\":2008,\"item_name\":\"ユニバーサルサービス料等\",\"order\":10,\"tax_rate\":\"10.0\",\"sum_price\":3,\"user_memo\":null,\"item_name_with_user_memo\":\"ユニバーサルサービス料等\",\"display_unit_price\":null,\"sim_sequence_id\":\"-2\"},{\"item_id\":9001,\"item_name\":\"新規契約事務手数料\",\"order\":28,\"tax_rate\":\"10.0\",\"sum_price\":0,\"user_memo\":null,\"item_name_with_user_memo\":\"新規契約事務手数料\",\"display_unit_price\":null},{\"item_id\":2015,\"item_name\":\"5G回線オプション\",\"order\":35,\"tax_rate\":\"10.0\",\"sum_price\":0,\"user_memo\":null,\"item_name_with_user_memo\":\"5G回線オプション\",\"display_unit_price\":null,\"sim_sequence_id\":\"-2\"},{\"item_id\":9013,\"item_name\":\"eSIM新規発行手数料\",\"order\":35,\"tax_rate\":\"10.0\",\"sum_price\":500,\"user_memo\":null,\"item_name_with_user_memo\":\"eSIM新規発行手数料\",\"display_unit_price\":null}],\"amount_without_tax\":847,\"tax\":84,\"amount\":931,\"payment_ym\":0,\"without_order\":null}}"
})
print(f"[1-2] order: {r.url}")

# Bước 3: order confirm
r = session.post('https://linksmate.jp/order/confirm/', data={
    "csrf_name": csrf_name, 
    "csrf_value": csrf_value,
    "sim_user[0][other_uses_sim_card]": "0",
    "sim_user[0][sim_user_familyname]": "",
    "sim_user[0][sim_user_firstname]": "",
    "sim_user[0][sim_user_familyname_kana]": "",
    "sim_user[0][sim_user_firstname_kana]": "",
    "delivery_day": "",
    "delivery_time": ""
})
print(f"[1-3] order: {r.url}")

# Bước 4: order complete
r = session.post('https://linksmate.jp/order/complete/', data={
    "csrf_name": csrf_name, 
    "csrf_value": csrf_value,
    "accept_important_concern": "1",
    "accept_terms_of_service": "1",
    "accept_drivers_license_provide": "1",
    "accept_mate_phone_concern": "1",
    "accept_line_of_5g_concern": "1",
    "accept_electronic_delivery": "1",
    "accept_no_cancel": "1",
    "accept_new_order": "1",
    "accept_payment_by_the_day": "1",
    "ready_for_identity_verification_documents": "1",
    "agree_ekyc": "1",
    "confirm_validated_terminal": "1",
    "confirm_validated_5g_terminal": "1",
    "confirm_validated_esim": "1",
    "confirm_esim_terminal": "1",
    "confirm_eid_input": "1",
    "accept_game_connect": "1",
    "accept_use_restriction": "1",
    "lp_notes": "1",
    "confirm_input_correct": "1"
})
print(f"[1-4] order: {r.url}")

print("✅ DONE: Hoàn thành Bước 1")