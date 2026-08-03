import imaplib, email, re, time
from datetime import datetime, timezone

def get_linksmate_code_dynamic(gmail_user, gmail_app_pass, target_hotmail, max_retries=10, delay=5, not_before_utc=None):
    IMAP_SERVER = "imap.gmail.com"
    for attempt in range(max_retries):
        print(f"[*] [{datetime.now().strftime('%H:%M:%S')}] Kiểm tra lần {attempt+1}/{max_retries}...")
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(gmail_user, gmail_app_pass)
            mail.select("inbox")
            status, messages = mail.search(None, '(SUBJECT "LinksMate")')
            if status != 'OK' or not messages[0]:
                mail.logout(); time.sleep(delay); continue
            mail_ids = messages[0].split()[::-1][:5]
            now_utc = datetime.now(timezone.utc)
            for mail_id in mail_ids:
                status, data = mail.fetch(mail_id, '(RFC822)')
                if status != 'OK': continue
                msg = email.message_from_bytes(data[0][1])
                date_header = msg.get("Date")
                is_valid_time = False
                if date_header:
                    try:
                        mail_date = email.utils.parsedate_to_datetime(date_header)
                        mail_utc = mail_date.astimezone(timezone.utc)
                        is_recent = (now_utc - mail_utc).total_seconds() <= 120
                        is_after_login = not_before_utc is None or mail_utc >= not_before_utc
                        if is_recent and is_after_login:
                            is_valid_time = True
                    except Exception:
                        pass
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore'); break
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                if target_hotmail.lower() in body.lower() and is_valid_time:
                    match = re.search(r'(?:認証コード)\s*:\s*(\d{4,6})', body)
                    if not match:
                        match = re.search(r':\s*(\d{4,6})', body)
                    if match:
                        otp = match.group(1)
                        print(f"[==>] CODE: {otp}")
                        mail.store(mail_id, '+FLAGS', '\\Seen')
                        mail.logout()
                        return otp
            mail.logout()
        except Exception as e:
            print(f"[!] Lỗi: {e}")
        time.sleep(delay)
    print(f"[-] Hết thời gian, không lấy được code cho {target_hotmail}")
    return None
