import sys, os, json, csv, subprocess, threading, unicodedata, zipfile
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog,
    QMenu, QAction, QMessageBox, QDialog, QFormLayout,
    QDialogButtonBox, QAbstractItemView, QFrame, QSplitter,
    QGroupBox, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QMimeData
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QCursor, QDrag, QKeySequence

# ── paths ──────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE, "settings.json")
ACCOUNTS_FILE = os.path.join(BASE, "accounts.json")

# ── default settings ───────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "GMAIL_MAIN": "congnguyen20042021@gmail.com",
    "GMAIL_APP_PASSWORD": "ocvgudskzzgplnqw",
    "prefecture": "東京都",
    "city": "千代田区丸の内",
    "address": "1-1",
    "password": "Pass@12345",
    "proxies": "",
    "theme": "dark"
}

# ── stylesheet ─────────────────────────────────────────────────────────────────
QSS = """
QMainWindow, QDialog {
    background: #0f1117;
}
QWidget {
    background: #0f1117;
    color: #e2e8f0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #2d3748;
    border-radius: 8px;
    background: #161b27;
}
QTabBar::tab {
    background: #1a2035;
    color: #94a3b8;
    padding: 10px 28px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 3px;
    font-weight: 600;
    font-size: 13px;
}
QTabBar::tab:selected {
    background: #2563eb;
    color: #ffffff;
}
QTabBar::tab:hover:!selected {
    background: #1e3a5f;
    color: #e2e8f0;
}
QGroupBox {
    border: 1px solid #2d3748;
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 10px 10px 10px;
    font-weight: 600;
    color: #94a3b8;
    font-size: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #60a5fa;
}
QLineEdit, QTextEdit {
    background: #1e2535;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 7px 10px;
    color: #e2e8f0;
    selection-background-color: #2563eb;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #2563eb;
}
QLabel {
    color: #94a3b8;
    font-size: 12px;
}
QPushButton {
    background: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover {
    background: #3b82f6;
}
QPushButton:pressed {
    background: #1d4ed8;
}
QPushButton#btnDanger {
    background: #dc2626;
}
QPushButton#btnDanger:hover {
    background: #ef4444;
}
QPushButton#btnSuccess {
    background: #16a34a;
}
QPushButton#btnSuccess:hover {
    background: #22c55e;
}
QPushButton#btnWarning {
    background: #d97706;
}
QPushButton#btnWarning:hover {
    background: #f59e0b;
}
QTableWidget {
    background: #161b27;
    border: 1px solid #2d3748;
    border-radius: 8px;
    gridline-color: #1e2535;
    selection-background-color: #1e3a5f;
    alternate-background-color: #1a2035;
}
QTableWidget::item {
    padding: 6px 10px;
    border: none;
}
QTableWidget::item:selected {
    background: #1e3a5f;
    color: #60a5fa;
}
QHeaderView::section {
    background: #1a2035;
    color: #60a5fa;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #2d3748;
    font-weight: 700;
    font-size: 12px;
}
QScrollBar:vertical {
    background: #1a2035;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #2d3748;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #4a5568;
}
QScrollBar:horizontal {
    background: #1a2035;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #2d3748;
    border-radius: 4px;
}
QMenu {
    background: #1e2535;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 6px 0;
}
QMenu::item {
    padding: 8px 24px 8px 16px;
    color: #e2e8f0;
    border-radius: 4px;
    margin: 1px 4px;
}
QMenu::item:selected {
    background: #2563eb;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background: #2d3748;
    margin: 4px 10px;
}
QDialogButtonBox QPushButton {
    min-width: 80px;
}
QLineEdit#cellText {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 4px 6px;
    color: #e2e8f0;
    selection-background-color: #2563eb;
}
"""

LIGHT_QSS = """
QMainWindow, QDialog {
    background: #f8fafc;
}
QWidget {
    background: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: #ffffff;
}
QTabBar::tab {
    background: #e2e8f0;
    color: #475569;
    padding: 10px 28px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 3px;
    font-weight: 600;
    font-size: 13px;
}
QTabBar::tab:selected {
    background: #2563eb;
    color: #ffffff;
}
QTabBar::tab:hover:!selected {
    background: #dbeafe;
    color: #1e40af;
}
QGroupBox {
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 10px 10px 10px;
    font-weight: 600;
    color: #475569;
    font-size: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #2563eb;
}
QLineEdit, QTextEdit {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 10px;
    color: #0f172a;
    selection-background-color: #bfdbfe;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #2563eb;
}
QLabel {
    color: #475569;
    font-size: 12px;
}
QPushButton {
    background: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover {
    background: #3b82f6;
}
QPushButton:pressed {
    background: #1d4ed8;
}
QPushButton#btnDanger {
    background: #dc2626;
}
QPushButton#btnDanger:hover {
    background: #ef4444;
}
QPushButton#btnSuccess {
    background: #16a34a;
}
QPushButton#btnSuccess:hover {
    background: #22c55e;
}
QPushButton#btnWarning {
    background: #d97706;
}
QPushButton#btnWarning:hover {
    background: #f59e0b;
}
QTableWidget {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    gridline-color: #e2e8f0;
    selection-background-color: #dbeafe;
    alternate-background-color: #f1f5f9;
}
QTableWidget::item {
    padding: 6px 10px;
    border: none;
}
QTableWidget::item:selected {
    background: #dbeafe;
    color: #1d4ed8;
}
QHeaderView::section {
    background: #e2e8f0;
    color: #1d4ed8;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #cbd5e1;
    font-weight: 700;
    font-size: 12px;
}
QScrollBar:vertical {
    background: #e2e8f0;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #94a3b8;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #64748b;
}
QScrollBar:horizontal {
    background: #e2e8f0;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #94a3b8;
    border-radius: 4px;
}
QMenu {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 6px 0;
}
QMenu::item {
    padding: 8px 24px 8px 16px;
    color: #0f172a;
    border-radius: 4px;
    margin: 1px 4px;
}
QMenu::item:selected {
    background: #2563eb;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background: #e2e8f0;
    margin: 4px 10px;
}
QDialogButtonBox QPushButton {
    min-width: 80px;
}
QLineEdit#cellText {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 4px 6px;
    color: #0f172a;
    selection-background-color: #bfdbfe;
}
"""

# ── columns ────────────────────────────────────────────────────────────────────
COLS = ["Chọn","Trạng thái","Email","Pass Mail","Pass Acc","Group ID","Groups","Họ","Tên",
        "Họ 1","Tên 1","Họ phiên âm","Tên phiên âm",
        "Mã bưu điện","Địa chỉ","EID","Mã số LP","Số điện thoại"]
ACC_KEYS = ["status","mail","passmail","passacc","group_id","groups","ho","ten",
            "ho1","ten1","hophienam","tenphienam",
            "mabuudien","diachi","eid","lp_code","sdt"]

# ── helpers ────────────────────────────────────────────────────────────────────
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                d = json.load(f)
            s = dict(DEFAULT_SETTINGS)
            s.update(d)
            return s
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)

def save_settings(s):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_accounts(accs):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(accs, f, ensure_ascii=False, indent=2)

def empty_acc():
    return {k: "" for k in ACC_KEYS}

def fullwidth_to_ascii_upper(text: str) -> str:
    """Chuyển fullwidth (ｃＨＩＣｏＮｇ) hoặc có dấu tiếng Việt → ASCII HOA không dấu."""
    if not text:
        return text
    # Fullwidth A-Z: U+FF21–U+FF3A, a-z: U+FF41–U+FF5A
    result = []
    for ch in text:
        cp = ord(ch)
        if 0xFF21 <= cp <= 0xFF3A:        # fullwidth A-Z
            result.append(chr(cp - 0xFF21 + ord('A')))
        elif 0xFF41 <= cp <= 0xFF5A:      # fullwidth a-z
            result.append(chr(cp - 0xFF41 + ord('A')))
        else:
            result.append(ch.upper())
    ascii_str = ''.join(result)
    # Bỏ dấu tiếng Việt / diacritics
    normalized = unicodedata.normalize('NFD', ascii_str)
    return ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')

def normalize_romaji_fields(acc: dict) -> dict:
    """Áp dụng fullwidth→ASCII HOA cho ho1 và ten1."""
    for key in ('ho1', 'ten1'):
        if acc.get(key):
            acc[key] = fullwidth_to_ascii_upper(acc[key])
    return acc

def current_qss():
    app = QApplication.instance()
    if app and app.styleSheet():
        return app.styleSheet()
    return QSS

# ── worker thread ──────────────────────────────────────────────────────────────
class Worker(QThread):
    status_update = pyqtSignal(int, str)   # row, status text
    groups_update = pyqtSignal(int, str)   # row, groups text
    info_update   = pyqtSignal(int, dict)  # row, parsed account info
    log_update    = pyqtSignal(int, str, str)  # row, script, log line
    finished      = pyqtSignal(int, str)   # row, result

    def __init__(self, script, row, acc, settings, proxy):
        super().__init__()
        self.script   = script
        self.row      = row
        self.acc      = acc
        self.settings = settings
        self.proxy    = proxy

    def run(self):
        self.status_update.emit(self.row, "⏳ Đang chạy...")
        self.log_update.emit(self.row, self.script, "START")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        env.update({
            "GMAIL_MAIN":          self.settings.get("GMAIL_MAIN",""),
            "GMAIL_APP_PASSWORD":  self.settings.get("GMAIL_APP_PASSWORD",""),
            "PREFECTURE":          self.settings.get("prefecture",""),
            "CITY":                self.settings.get("city",""),
            "ADDRESS":             self.settings.get("address",""),
            "ACC_PASSWORD":        self.settings.get("password",""),
            "PROXY":               self.proxy,
            "ACC_MAIL":            self.acc.get("mail",""),
            "ACC_PASSMAIL":        self.acc.get("passmail",""),
            "ACC_PASSACC":         self.acc.get("passacc",""),
            "ACC_GROUP_ID":        self.acc.get("group_id",""),
            "ACC_HO":              self.acc.get("ho",""),
            "ACC_TEN":             self.acc.get("ten",""),
            "ACC_HO1":             self.acc.get("ho1",""),
            "ACC_TEN1":            self.acc.get("ten1",""),
            "ACC_HOPHIENAM":       self.acc.get("hophienam",""),
            "ACC_TENPHIENAM":      self.acc.get("tenphienam",""),
            "ACC_MABUUDIEN":       self.acc.get("mabuudien",""),
            "ACC_DIACHI":          self.acc.get("diachi",""),
            "ACC_SDT":             self.acc.get("sdt",""),
            "ACC_EID":             self.acc.get("eid",""),
        })
        script_path = os.path.join(BASE, self.script)
        try:
            result = subprocess.run(
                [sys.executable, "-X", "utf8", script_path],
                capture_output=True, encoding="utf-8", errors="replace",
                env=env, timeout=300
            )
            # Chỉ lấy dòng cuối có nội dung, ưu tiên DONE/FAIL
            lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
            for line in lines:
                self.log_update.emit(self.row, self.script, line)
                if line.startswith("[login] groups found:"):
                    groups_text = line.split(":", 1)[1].strip()
                    if groups_text and groups_text != "none":
                        self.groups_update.emit(self.row, groups_text)
            if result.returncode != 0:
                err_lines = [l.strip() for l in result.stderr.splitlines() if l.strip()]
                for line in err_lines:
                    self.log_update.emit(self.row, self.script, f"STDERR: {line}")
                last = err_lines[-1] if err_lines else (lines[-1] if lines else "Lỗi không xác định")
                self.log_update.emit(self.row, self.script, f"EXIT {result.returncode}")
                self.finished.emit(self.row, f"❌ {last[:80]}")
                return
            # Tìm dòng DONE hoặc FAIL trước, nếu không có thì lấy dòng cuối
            summary = next((l for l in reversed(lines) if l.startswith(("DONE","FAIL","✅","❌"))), None)
            if not summary:
                summary = lines[-1] if lines else "Done"
            self.log_update.emit(self.row, self.script, "DONE")
            self.finished.emit(self.row, f"✅ {summary[:80]}")
        except subprocess.TimeoutExpired:
            self.log_update.emit(self.row, self.script, "TIMEOUT")
            self.finished.emit(self.row, "⏰ Timeout")
        except Exception as e:
            self.log_update.emit(self.row, self.script, f"EXCEPTION: {e}")
            self.finished.emit(self.row, f"❌ {str(e)[:60]}")

# ── Check group worker ─────────────────────────────────────────────────────────
class CheckGroupWorker(QThread):
    status_update = pyqtSignal(int, str)
    groups_update = pyqtSignal(int, str)
    info_update   = pyqtSignal(int, dict)
    log_update    = pyqtSignal(int, str, str)
    finished      = pyqtSignal(int, str)

    def __init__(self, row: int, acc: dict, settings: dict, proxy: str):
        super().__init__()
        self.row      = row
        self.acc      = acc
        self.settings = settings
        self.proxy    = proxy

    def run(self):
        script = "CheckNhom"
        self.status_update.emit(self.row, "⏳ Check nhóm...")
        self.log_update.emit(self.row, script, "START")
        try:
            import sys as _sys, io, contextlib
            _sys.path.insert(0, BASE)
            from bs4 import BeautifulSoup
            from login import do_login, parse_groups, format_groups, parse_account_info

            mail    = self.acc.get("mail", "")
            passacc = self.acc.get("passacc", "")
            gmail   = self.settings.get("GMAIL_MAIN", "")
            apppass = self.settings.get("GMAIL_APP_PASSWORD", "")

            login_log = io.StringIO()
            try:
                with contextlib.redirect_stdout(login_log):
                    session, _, _ = do_login(mail, passacc, gmail, apppass, self.proxy, "")
            finally:
                for line in login_log.getvalue().splitlines():
                    line = line.strip()
                    if line:
                        self.log_update.emit(self.row, script, line)

            r = session.get("https://linksmate.jp/mypage/")
            groups = parse_groups(r.text)
            groups_text = format_groups(groups)
            if not groups_text:
                raise Exception("Không tìm thấy nhóm trên mypage")

            info = {}
            info.update(parse_account_info(r.text))

            for url in (
                "https://linksmate.jp/mypage/userinfo/",
                "https://linksmate.jp/mypage/userinfo/edit/",
                "https://linksmate.jp/mypage/customer/",
                "https://linksmate.jp/mypage/customerinfo/",
                "https://linksmate.jp/mypage/contract/",
                "https://linksmate.jp/mypage/member/",
                "https://linksmate.jp/mypage/account/",
                "https://linksmate.jp/mypage/eid/",
            ):
                try:
                    rr = session.get(url)
                    self.log_update.emit(self.row, script, f"GET {url} -> {rr.status_code} {rr.url}")
                    if rr.status_code < 400:
                        info.update(parse_account_info(rr.text))
                except Exception as e:
                    self.log_update.emit(self.row, script, f"WARN {url}: {e}")

            try:
                rr = session.get("https://linksmate.jp/mypage/simcardadd/")
                self.log_update.emit(self.row, script, f"GET simcardadd -> {rr.status_code}")
                if rr.status_code < 400:
                    soup = BeautifulSoup(rr.text, "html.parser")
                    phones = []
                    for td in soup.select("td[data-label='SIMカード電話番号']"):
                        div = td.select_one(".simcardadd__div-data")
                        if div:
                            phone = div.get_text(strip=True)
                            if phone and phone not in phones:
                                phones.append(phone)
                    if phones:
                        info["sdt"] = "\n".join(phones)
            except Exception as e:
                self.log_update.emit(self.row, script, f"WARN simcardadd: {e}")

            self.log_update.emit(self.row, script, f"GROUPS: {groups_text}")
            self.groups_update.emit(self.row, groups_text)
            if info:
                self.info_update.emit(self.row, info)
                self.log_update.emit(self.row, script, f"INFO: {', '.join(sorted(info.keys()))}")
            profile_keys = sorted(k for k in info.keys() if k != "lp_code")
            if profile_keys:
                self.finished.emit(self.row, f"✅ Check nhóm/info: {', '.join(profile_keys)[:55]}")
            else:
                self.log_update.emit(self.row, script, "INFO_PROFILE: chưa thấy field họ tên/địa chỉ/eid/sđt trong HTML")
                self.finished.emit(self.row, f"✅ Check nhóm OK, chưa thấy info profile")
        except Exception as e:
            self.log_update.emit(self.row, script, f"EXCEPTION: {e}")
            self.finished.emit(self.row, f"❌ {str(e)[:80]}")

# ── Edit dialog ────────────────────────────────────────────────────────────────
class EditDialog(QDialog):
    def __init__(self, acc: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chỉnh sửa tài khoản")
        self.setMinimumWidth(420)
        self.setStyleSheet(current_qss())
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        self.fields = {}
        labels = {
            "mail":"Email","passmail":"Pass Mail","passacc":"Pass Acc",
            "group_id":"Group ID",
            "groups":"Groups",
            "ho":"Họ","ten":"Tên","ho1":"Họ 1","ten1":"Tên 1",
            "hophienam":"Họ phiên âm","tenphienam":"Tên phiên âm",
            "mabuudien":"Mã bưu điện","diachi":"Địa chỉ","sdt":"Số điện thoại",
            "eid":"EID"
        }
        for k, lbl in labels.items():
            le = QLineEdit(acc.get(k,""))
            self.fields[k] = le
            form.addRow(QLabel(lbl), le)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_data(self):
        return {k: v.text().strip() for k, v in self.fields.items()}

# ── Settings tab ───────────────────────────────────────────────────────────────
class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = load_settings()
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.addWidget(scroll)

        main = QVBoxLayout(inner)
        main.setContentsMargins(20,20,20,20)
        main.setSpacing(16)

        # Gmail group
        g1 = QGroupBox("📧  Gmail")
        f1 = QFormLayout(g1)
        f1.setSpacing(10)
        self.e_gmail = QLineEdit(self.settings["GMAIL_MAIN"])
        self.e_apppass = QLineEdit(self.settings["GMAIL_APP_PASSWORD"])
        self.e_apppass.setEchoMode(QLineEdit.Password)
        f1.addRow(QLabel("Gmail chính"), self.e_gmail)
        f1.addRow(QLabel("App Password"), self.e_apppass)
        main.addWidget(g1)

        # Address group
        g2 = QGroupBox("🏠  Địa chỉ mặc định")
        f2 = QFormLayout(g2)
        f2.setSpacing(10)
        self.e_pref = QLineEdit(self.settings["prefecture"])
        self.e_city = QLineEdit(self.settings["city"])
        self.e_addr = QLineEdit(self.settings["address"])
        f2.addRow(QLabel("Prefecture"), self.e_pref)
        f2.addRow(QLabel("City"), self.e_city)
        f2.addRow(QLabel("Address"), self.e_addr)
        main.addWidget(g2)

        # Password group
        g3 = QGroupBox("🔑  Mật khẩu tài khoản")
        f3 = QFormLayout(g3)
        f3.setSpacing(10)
        self.e_pass = QLineEdit(self.settings["password"])
        f3.addRow(QLabel("Password mặc định"), self.e_pass)
        main.addWidget(g3)

        # Proxy group
        g4 = QGroupBox("🌐  Proxy  (ip:port  hoặc  ip:port:user:pass — mỗi dòng 1 proxy)")
        f4 = QVBoxLayout(g4)
        self.e_proxy = QTextEdit(self.settings.get("proxies",""))
        self.e_proxy.setMinimumHeight(120)
        self.e_proxy.setPlaceholderText("192.168.1.1:8080\n192.168.1.2:8080:user:pass")
        f4.addWidget(self.e_proxy)
        main.addWidget(g4)

        # Save button
        row = QHBoxLayout()
        row.addStretch()
        btn = QPushButton("💾  Lưu cài đặt")
        btn.setObjectName("btnSuccess")
        btn.setFixedWidth(160)
        btn.clicked.connect(self.save)
        row.addWidget(btn)
        main.addLayout(row)
        main.addStretch()

    def save(self):
        self.settings.update({
            "GMAIL_MAIN":         self.e_gmail.text().strip(),
            "GMAIL_APP_PASSWORD": self.e_apppass.text().strip(),
            "prefecture":         self.e_pref.text().strip(),
            "city":               self.e_city.text().strip(),
            "address":            self.e_addr.text().strip(),
            "password":           self.e_pass.text().strip(),
            "proxies":            self.e_proxy.toPlainText().strip(),
        })
        save_settings(self.settings)
        QMessageBox.information(self, "Đã lưu", "Cài đặt đã được lưu thành công!")

    def get_settings(self):
        return self.settings

# ── LP Info Worker ─────────────────────────────────────────────────────────────
class LPInfoWorker(QThread):
    finished = pyqtSignal(str, list)   # lp_text, [phone_numbers]
    error    = pyqtSignal(str)

    def __init__(self, acc: dict, settings: dict):
        super().__init__()
        self.acc      = acc
        self.settings = settings

    def run(self):
        try:
            import sys as _sys, os as _os
            _sys.path.insert(0, BASE)
            from login import do_login
            from bs4 import BeautifulSoup

            mail    = self.acc.get("mail", "")
            passacc = self.acc.get("passacc", "")
            gmail   = self.settings.get("GMAIL_MAIN", "")
            apppass = self.settings.get("GMAIL_APP_PASSWORD", "")
            proxy   = self.acc.get("_proxy", "")

            session, _, _ = do_login(mail, passacc, gmail, apppass, proxy, self.acc.get("group_id", ""))

            # Lấy LP
            r1   = session.get("https://linksmate.jp/mypage/")
            soup = BeautifulSoup(r1.text, "html.parser")
            lp_el = soup.select_one("#available_lp .mypage-lp__available-value")
            lp_text = lp_el.get_text(strip=True) if lp_el else "N/A"

            # Lấy danh sách SĐT
            r2    = session.get("https://linksmate.jp/mypage/simcardadd/")
            soup2 = BeautifulSoup(r2.text, "html.parser")
            phones = []
            for td in soup2.select("td[data-label='SIMカード電話番号']"):
                div = td.select_one(".simcardadd__div-data")
                if div:
                    phones.append(div.get_text(strip=True))

            self.finished.emit(lp_text, phones)
        except Exception as e:
            self.error.emit(str(e))


# ── LP Info Dialog ─────────────────────────────────────────────────────────────
class LPInfoDialog(QDialog):
    def __init__(self, mail: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Thông tin LP & SĐT — {mail}")
        self.setMinimumWidth(400)
        self.setStyleSheet(current_qss())
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.lbl_status = QLabel("⏳ Đang login và tải dữ liệu...")
        self.lbl_status.setStyleSheet("color:#f59e0b;font-weight:600;")
        layout.addWidget(self.lbl_status)

        # LP
        lp_group = QGroupBox("💎  LP khả dụng")
        lp_lay = QVBoxLayout(lp_group)
        self.lbl_lp = QLabel("—")
        self.lbl_lp.setStyleSheet("color:#22c55e;font-size:22px;font-weight:700;")
        self.lbl_lp.setAlignment(Qt.AlignCenter)
        lp_lay.addWidget(self.lbl_lp)
        layout.addWidget(lp_group)

        # SĐT
        sdt_group = QGroupBox("📱  Danh sách SĐT SIM")
        sdt_lay = QVBoxLayout(sdt_group)
        self.txt_sdt = QTextEdit()
        self.txt_sdt.setReadOnly(True)
        self.txt_sdt.setMinimumHeight(120)
        self.txt_sdt.setPlaceholderText("Chưa có dữ liệu...")
        sdt_lay.addWidget(self.txt_sdt)
        layout.addWidget(sdt_group)

        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def set_result(self, lp: str, phones: list):
        self.lbl_status.setText("✅ Đã tải xong")
        self.lbl_status.setStyleSheet("color:#22c55e;font-weight:600;")
        self.lbl_lp.setText(lp)
        self.txt_sdt.setPlainText("\n".join(phones) if phones else "Không có SĐT nào")

    def set_error(self, msg: str):
        self.lbl_status.setText(f"❌ Lỗi: {msg}")
        self.lbl_status.setStyleSheet("color:#ef4444;font-weight:600;")
        self.lbl_lp.setText("—")


# ── LP Charge Worker ───────────────────────────────────────────────────────────
class LPChargeWorker(QThread):
    finished = pyqtSignal(str)   # mã số thanh toán
    error    = pyqtSignal(str)

    def __init__(self, acc: dict, settings: dict, lp_amount: int):
        super().__init__()
        self.acc        = acc
        self.settings   = settings
        self.lp_amount  = lp_amount

    def run(self):
        try:
            import sys as _sys
            _sys.path.insert(0, BASE)
            from login import do_login
            from bs4 import BeautifulSoup
            from urllib.parse import urlencode

            mail    = self.acc.get("mail", "")
            passacc = self.acc.get("passacc", "")
            gmail   = self.settings.get("GMAIL_MAIN", "")
            apppass = self.settings.get("GMAIL_APP_PASSWORD", "")
            proxy   = self.acc.get("_proxy", "")

            session, csrf_name, csrf_value = do_login(mail, passacc, gmail, apppass, proxy, self.acc.get("group_id", ""))

            HEADERS = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.6,en;q=0.5",
                "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "upgrade-insecure-requests": "1",
            }

            # Bước 1: GET confirm page để lấy canonical URL (csrf trong query string)
            confirm_params = {
                "csrf_name": csrf_name,
                "csrf_value": csrf_value,
                "lp_amount": str(self.lp_amount),
                "payment_method_large": "cvs",
                "payment_method_cvs": "econFm",
                "enter_credit": "1",
                "credit_number_1": "", "credit_number_2": "",
                "credit_number_3": "", "credit_number_4": "",
                "credit_security_code": "",
            }
            confirm_url = "https://linksmate.jp/mypage/linkspoint/charge/confirm/?" + urlencode(confirm_params)

            r_get = session.get(confirm_url, headers={**HEADERS, "referer": "https://linksmate.jp/mypage/linkspoint/charge/"})
            soup_get = BeautifulSoup(r_get.text, "html.parser")

            # Lấy canonical URL (có chứa csrf mới)
            canonical = soup_get.find("link", rel="canonical")
            post_url  = canonical["href"] if canonical else confirm_url

            # Lấy csrf mới từ form trong trang confirm
            csrf_name2  = soup_get.find("input", {"class": "csrf-key"})
            csrf_value2 = soup_get.find("input", {"class": "csrf-value"})
            cn2 = csrf_name2["value"]  if csrf_name2  else csrf_name
            cv2 = csrf_value2["value"] if csrf_value2 else csrf_value

            # Bước 2: POST confirm
            post_data = {
                "csrf_name":                    cn2,
                "csrf_value":                   cv2,
                "lp_amount":                    str(self.lp_amount),
                "payment_method_large":         "cvs",
                "payment_method_cvs":           "econFm",
                "confirmed":                    "true",
                "veritrans_id":                 "",
                "googlepay_merchant_id":        "",
                "googlepay_veritrans_merchant_id": "",
                "googlepay_merchant_name":      "",
                "agreePaidLpCaution":           "1",
                "agreeNoCancel":                "1",
                "agreeCheck":                   "1",
            }
            session.post(post_url, data=post_data, headers={
                **HEADERS,
                "content-type": "application/x-www-form-urlencoded",
                "referer": post_url,
            })

            # Bước 3: Lấy mã số từ API JSON (item đầu tiên = mới nhất)
            r_list = session.get(
                "https://linksmate.jp/api/mypage/linkspoint/charge/list/",
                headers={**HEADERS, "accept": "application/json, text/javascript, */*; q=0.01",
                         "x-requested-with": "XMLHttpRequest"}
            )
            data = r_list.json()
            charge_list = data.get("data", {}).get("charge_lp_list", [])
            if not charge_list:
                raise Exception("Danh sách LP rỗng, có thể chưa tạo thành công")

            # Lấy item đầu tiên (mới nhất), parse mã số từ other_text
            # other_text = "お支払い番号: 936286" → lấy "936286"
            other_text = charge_list[0].get("other_text", "")
            if ":" in other_text:
                code = other_text.split(":")[-1].strip()
            else:
                code = other_text.strip()

            if not code:
                raise Exception("Không tìm thấy mã số trong kết quả")

            self.finished.emit(code)
        except Exception as e:
            self.error.emit(str(e))


# ── LP Charge Dialog ───────────────────────────────────────────────────────────
class LPChargeDialog(QDialog):
    do_charge = pyqtSignal(int)   # phát signal khi user bấm Tạo LP

    def __init__(self, mail: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Tạo LP — {mail}")
        self.setMinimumWidth(360)
        self.setStyleSheet(current_qss())
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(10)
        self.inp_lp = QLineEdit("125")
        self.inp_lp.setPlaceholderText("Nhập số LP muốn tạo...")
        form.addRow(QLabel("Số LP:"), self.inp_lp)
        layout.addLayout(form)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color:#f59e0b;font-weight:600;")
        layout.addWidget(self.lbl_status)

        self.lbl_code = QLabel("")
        self.lbl_code.setStyleSheet("color:#22c55e;font-size:20px;font-weight:700;")
        self.lbl_code.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_code)

        btns = QHBoxLayout()
        self.btn_ok = QPushButton("🚀  Tạo LP")
        self.btn_ok.setObjectName("btnSuccess")
        self.btn_ok.clicked.connect(self._on_ok)
        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(self.reject)
        btns.addWidget(self.btn_ok)
        btns.addWidget(btn_close)
        layout.addLayout(btns)

    def _on_ok(self):
        txt = self.inp_lp.text().strip()
        if not txt.isdigit() or int(txt) <= 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số LP hợp lệ!")
            return
        self.btn_ok.setEnabled(False)
        self.lbl_status.setText("⏳ Đang xử lý...")
        self.lbl_code.setText("")
        self.do_charge.emit(int(txt))

    def set_result(self, code: str):
        self.lbl_status.setText("✅ Tạo LP thành công!")
        self.lbl_status.setStyleSheet("color:#22c55e;font-weight:600;")
        self.lbl_code.setText(f"Mã số: {code}")
        self.btn_ok.setEnabled(True)

    def set_error(self, msg: str):
        self.lbl_status.setText(f"❌ Lỗi: {msg[:100]}")
        self.lbl_status.setStyleSheet("color:#ef4444;font-weight:600;")
        self.btn_ok.setEnabled(True)


# ── Draggable Table ────────────────────────────────────────────────────────────
class DraggableTable(QTableWidget):
    row_moved = pyqtSignal(int, int)  # from_row, to_row

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragDropOverwriteMode(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self._drag_source_row = -1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            row = self.rowAt(event.pos().y())
            self._drag_source_row = row
        super().mousePressEvent(event)

    def dropEvent(self, event):
        target_row = self.rowAt(event.pos().y())
        src = self._drag_source_row
        if src < 0 or target_row < 0 or src == target_row:
            super().dropEvent(event)
            return
        # Chèn vào trước target_row
        insert_at = target_row if target_row < src else target_row
        self.row_moved.emit(src, insert_at)
        event.accept()

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self._copy_selected_cells()
            return
        super().keyPressEvent(event)

    def _copy_selected_cells(self):
        indexes = sorted(self.selectedIndexes(), key=lambda i: (i.row(), i.column()))
        if not indexes:
            item = self.currentItem()
            if item:
                QApplication.clipboard().setText(item.data(Qt.UserRole) or item.text())
            return
        rows = {}
        for index in indexes:
            if self.isRowHidden(index.row()) or index.column() == 0:
                continue
            item = self.item(index.row(), index.column())
            widget = self.cellWidget(index.row(), index.column())
            if isinstance(widget, QLineEdit):
                text = widget.selectedText() or widget.text()
            else:
                text = (item.data(Qt.UserRole) or item.text()) if item else ""
            rows.setdefault(index.row(), {})[index.column()] = text
        if not rows:
            return
        min_col = min(col for cols in rows.values() for col in cols)
        max_col = max(col for cols in rows.values() for col in cols)
        lines = []
        for row in sorted(rows):
            lines.append("\t".join(rows[row].get(col, "") for col in range(min_col, max_col + 1)))
        QApplication.clipboard().setText("\n".join(lines))

# ── Accounts tab ───────────────────────────────────────────────────────────────
class AccountsTab(QWidget):
    def __init__(self, settings_tab: SettingsTab, parent=None):
        super().__init__(parent)
        self.settings_tab = settings_tab
        self.accounts     = load_accounts()
        self.workers      = {}   # row -> Worker
        self._proxy_index = 0
        self.page_size    = 50
        self.current_page = 0
        self.filtered_rows = []
        self._build_ui()
        self._load_table()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16,16,16,16)
        layout.setSpacing(12)

        # toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        # File management buttons
        btn_add  = QPushButton("➕  Thêm từ file")
        btn_add.clicked.connect(self.import_file)
        btn_add_empty = QPushButton("📝  Thêm dòng trống")
        btn_add_empty.clicked.connect(self.add_empty_row)
        btn_insert = QPushButton("⬆  Chèn dòng trên")
        btn_insert.clicked.connect(self.insert_row_above)
        btn_del  = QPushButton("🗑  Xóa đã chọn")
        btn_del.setObjectName("btnDanger")
        btn_del.clicked.connect(self.delete_selected)
        btn_export = QPushButton("📤  Xuất Excel")
        btn_export.clicked.connect(self.export_excel)

        # Sequential workflow buttons
        self.btn_create_acc = QPushButton("▶  Tạo tài khoản")
        self.btn_create_acc.setObjectName("btnSuccess")
        self.btn_create_acc.clicked.connect(lambda: self._run_selected("test1.py","⏳ Tạo TK"))

        self.btn_task3 = QPushButton("▶  Nhiệm vụ Nhóm 1")
        self.btn_task3.setObjectName("btnWarning")
        self.btn_task3.clicked.connect(lambda: self._run_selected_group1())

        # Utility buttons
        btn_xoa = QPushButton("📵  Xóa số")
        btn_xoa.setObjectName("btnDanger")
        btn_xoa.clicked.connect(lambda: self._run_selected("xoaso.py","⏳ Xóa số"))

        # Add buttons to toolbar
        for b in [btn_add, btn_add_empty, btn_insert, btn_del, btn_export, self.btn_create_acc, self.btn_task3, btn_xoa]:
            toolbar.addWidget(b)
        toolbar.addStretch()

        self.lbl_count = QLabel("0 tài khoản")
        self.lbl_count.setStyleSheet("color:#60a5fa;font-weight:700;")
        toolbar.addWidget(self.lbl_count)
        layout.addLayout(toolbar)

        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        search_row.addWidget(QLabel("Tìm kiếm"))
        self.e_search = QLineEdit()
        self.e_search.setPlaceholderText("Nhập email, trạng thái, group, SĐT...")
        self.e_search.textChanged.connect(self._on_search_changed)
        search_row.addWidget(self.e_search, 1)

        btn_select_all = QPushButton("Chọn All")
        btn_select_all.clicked.connect(self._select_all_visible)
        search_row.addWidget(btn_select_all)

        btn_clear_selection = QPushButton("Bỏ chọn All")
        btn_clear_selection.clicked.connect(self._clear_selection)
        search_row.addWidget(btn_clear_selection)
        layout.addLayout(search_row)

        page_row = QHBoxLayout()
        page_row.setSpacing(8)
        self.btn_first_page = QPushButton("«")
        self.btn_first_page.clicked.connect(lambda: self._set_page(0))
        self.btn_prev_page = QPushButton("‹")
        self.btn_prev_page.clicked.connect(lambda: self._set_page(self.current_page - 1))
        self.lbl_page = QLabel("Trang 1/1")
        self.lbl_page.setAlignment(Qt.AlignCenter)
        self.btn_next_page = QPushButton("›")
        self.btn_next_page.clicked.connect(lambda: self._set_page(self.current_page + 1))
        self.btn_last_page = QPushButton("»")
        self.btn_last_page.clicked.connect(lambda: self._set_page(self._page_count() - 1))
        page_row.addStretch()
        for w in [self.btn_first_page, self.btn_prev_page, self.lbl_page, self.btn_next_page, self.btn_last_page]:
            page_row.addWidget(w)
        page_row.addWidget(QLabel("50 row/trang"))
        layout.addLayout(page_row)

        # Track completion status for sequential workflow
        self.workflow_status = {
            "create_acc": False,
            "task3": False
        }

        # table
        self.table = DraggableTable(0, len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._context_menu)
        self.table.row_moved.connect(self._move_row)
        # col widths
        widths = [58,120,200,110,110,90,190,80,80,80,80,110,110,100,160,200,120,120]
        for i,w in enumerate(widths):
            self.table.setColumnWidth(i, w)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.setSpacing(8)

        log_toolbar = QHBoxLayout()
        lbl_log = QLabel("Log request")
        lbl_log.setStyleSheet("color:#60a5fa;font-weight:700;")
        log_toolbar.addWidget(lbl_log)
        log_toolbar.addStretch()
        btn_clear_log = QPushButton("Clear Log")
        btn_clear_log.clicked.connect(self._clear_log)
        log_toolbar.addWidget(btn_clear_log)
        right_layout.addLayout(log_toolbar)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMinimumWidth(320)
        self.txt_log.setPlaceholderText("Log request sẽ hiển thị ở đây...")
        right_layout.addWidget(self.txt_log, 1)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.table)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([900, 360])
        layout.addWidget(splitter, 1)

    # ── table helpers ──────────────────────────────────────────────────────────
    def _load_table(self):
        self.table.setRowCount(0)
        for acc in self.accounts:
            self._append_row(acc)
        self._apply_filter()

    def _append_row(self, acc: dict):
        r = self.table.rowCount()
        self.table.insertRow(r)
        check_item = QTableWidgetItem("")
        check_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
        check_item.setCheckState(Qt.Unchecked)
        check_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(r, 0, check_item)
        for c, key in enumerate(ACC_KEYS, start=1):
            val = acc.get(key, "")
            self._set_cell_text(r, c, val, center=(key == "status"))

    def _update_row(self, row: int, acc: dict):
        for c, key in enumerate(ACC_KEYS, start=1):
            self._set_cell_text(row, c, acc.get(key, ""), center=(key == "status"))

    def _set_status(self, row: int, text: str):
        self._set_cell_text(row, 1, text, center=True)
        item = self.table.item(row, 1)
        if item:
            color_map = {"✅":"#22c55e","❌":"#ef4444","⏳":"#f59e0b","⏰":"#f59e0b"}
            widget = self.table.cellWidget(row, 1)
            matched = False
            for k,v in color_map.items():
                if text.startswith(k):
                    item.setForeground(QColor(v))
                    if widget:
                        widget.setStyleSheet(f"color:{v};")
                    matched = True
                    break
            if not matched and widget:
                widget.setStyleSheet("")

    def _set_cell_text(self, row: int, col: int, value, center=False):
        text = str(value if value is not None else "")
        item = self.table.item(row, col)
        if not item:
            item = QTableWidgetItem("")
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, col, item)
        item.setText("")
        item.setData(Qt.UserRole, text)
        item.setTextAlignment((Qt.AlignCenter if center else Qt.AlignLeft) | Qt.AlignVCenter)

        widget = self.table.cellWidget(row, col)
        if not isinstance(widget, QLineEdit):
            widget = QLineEdit()
            widget.setObjectName("cellText")
            widget.setReadOnly(True)
            widget.setFrame(False)
            widget.setContextMenuPolicy(Qt.DefaultContextMenu)
            widget.setFocusPolicy(Qt.StrongFocus)
            self.table.setCellWidget(row, col, widget)
        widget.setText(text)
        widget.setAlignment(Qt.AlignCenter if center else Qt.AlignLeft)
        widget.setCursorPosition(0)

    def _on_search_changed(self):
        self.current_page = 0
        self._apply_filter()

    def _page_count(self):
        total = len(self.filtered_rows)
        return max(1, (total + self.page_size - 1) // self.page_size)

    def _set_page(self, page: int):
        self.current_page = max(0, min(page, self._page_count() - 1))
        self._apply_filter()

    def _apply_filter(self):
        if not hasattr(self, "table") or not hasattr(self, "e_search"):
            return
        query = self.e_search.text().strip().lower()
        self.filtered_rows = []
        for row, acc in enumerate(self.accounts):
            haystack = " ".join(str(acc.get(key, "")) for key in ACC_KEYS).lower()
            if not query or query in haystack:
                self.filtered_rows.append(row)

        page_count = self._page_count()
        if self.current_page >= page_count:
            self.current_page = page_count - 1
        start = self.current_page * self.page_size
        page_rows = set(self.filtered_rows[start:start + self.page_size])
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, row not in page_rows)

        shown_start = start + 1 if self.filtered_rows else 0
        shown_end = min(start + self.page_size, len(self.filtered_rows))
        total_text = f"{len(self.filtered_rows)}/{len(self.accounts)} tài khoản" if query else f"{len(self.accounts)} tài khoản"
        self.lbl_count.setText(f"{total_text} · {shown_start}-{shown_end}")
        self.lbl_page.setText(f"Trang {self.current_page + 1}/{page_count}")
        self.btn_first_page.setEnabled(self.current_page > 0)
        self.btn_prev_page.setEnabled(self.current_page > 0)
        self.btn_next_page.setEnabled(self.current_page < page_count - 1)
        self.btn_last_page.setEnabled(self.current_page < page_count - 1)

    def _visible_rows(self):
        return [row for row in range(self.table.rowCount()) if not self.table.isRowHidden(row)]

    def _checked_rows(self):
        rows = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                rows.append(row)
        return rows

    def _target_rows(self):
        checked = self._checked_rows()
        if checked:
            return checked
        selected = sorted({i.row() for i in self.table.selectedItems()})
        return selected

    def _select_all_visible(self):
        self.table.setUpdatesEnabled(False)
        for row in self._visible_rows():
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.Checked)
        self.table.setUpdatesEnabled(True)

    def _clear_selection(self):
        if not hasattr(self, "table"):
            return
        self.table.setUpdatesEnabled(False)
        for row in self._visible_rows():
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.Unchecked)
        self.table.clearSelection()
        self.table.setUpdatesEnabled(True)

    def _append_log(self, row: int, script: str, line: str):
        if not hasattr(self, "txt_log"):
            return
        ts = datetime.now().strftime("%H:%M:%S")
        mail = ""
        if 0 <= row < len(self.accounts):
            mail = self.accounts[row].get("mail", "")
        prefix = f"[{ts}] row {row + 1} {script}"
        if mail:
            prefix += f" {mail}"
        self.txt_log.append(f"{prefix} | {line}")
        self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())

    def _clear_log(self):
        if hasattr(self, "txt_log"):
            self.txt_log.clear()

    def _copy_cell_at(self, row: int, col: int):
        if row < 0 or col <= 0:
            return
        widget = self.table.cellWidget(row, col)
        if isinstance(widget, QLineEdit):
            selected = widget.selectedText()
            QApplication.clipboard().setText(selected or widget.text())
            return
        item = self.table.item(row, col)
        if item:
            QApplication.clipboard().setText(item.data(Qt.UserRole) or item.text())

    def _copy_row(self, row: int):
        if row < 0 or row >= self.table.rowCount():
            return
        values = []
        for col in range(1, self.table.columnCount()):
            widget = self.table.cellWidget(row, col)
            if isinstance(widget, QLineEdit):
                values.append(widget.text())
            else:
                item = self.table.item(row, col)
                values.append((item.data(Qt.UserRole) or item.text()) if item else "")
        QApplication.clipboard().setText("\t".join(values))

    # ── proxy picker ───────────────────────────────────────────────────────────
    def _next_proxy(self):
        proxies = [p.strip() for p in
                   self.settings_tab.get_settings().get("proxies","").splitlines()
                   if p.strip()]
        if not proxies:
            return ""
        proxy = proxies[self._proxy_index % len(proxies)]
        self._proxy_index += 1
        return proxy

    # ── run helpers ────────────────────────────────────────────────────────────
    def _run_row(self, row: int, script: str):
        if row in self.workers and self.workers[row].isRunning():
            return
        acc     = self.accounts[row]
        self._run_row_with_acc(row, script, acc)

    def _run_row_with_acc(self, row: int, script: str, acc: dict):
        proxy   = self._next_proxy()
        sett    = self.settings_tab.get_settings()
        worker  = Worker(script, row, acc, sett, proxy)
        worker.status_update.connect(self._set_status)
        worker.groups_update.connect(self._on_worker_groups_update)
        worker.info_update.connect(self._on_worker_info_update)
        worker.log_update.connect(self._append_log)
        worker.finished.connect(self._on_finished)
        self.workers[row] = worker
        worker.start()

    def _run_row_group(self, row: int, script: str, group_id: str):
        if row in self.workers and self.workers[row].isRunning():
            return
        acc = dict(self.accounts[row])
        acc["group_id"] = str(group_id or "").strip()
        self._run_row_with_acc(row, script, acc)

    def _check_groups_row(self, row: int):
        if row in self.workers and self.workers[row].isRunning():
            return
        acc = dict(self.accounts[row])
        proxy = self._next_proxy()
        sett = self.settings_tab.get_settings()
        worker = CheckGroupWorker(row, acc, sett, proxy)
        worker.status_update.connect(self._set_status)
        worker.groups_update.connect(self._on_worker_groups_update)
        worker.log_update.connect(self._append_log)
        worker.finished.connect(self._on_finished)
        self.workers[row] = worker
        worker.start()

    def _run_selected_group1(self):
        selected_rows = self._target_rows()
        if not selected_rows:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn ít nhất một dòng để chạy!")
            return
        for row in selected_rows:
            group_id = self._group_id_by_order(self.accounts[row].get("groups", ""), "1")
            self._run_row_group(row, "test3.py", group_id)

    def _run_selected(self, script: str, label: str):
        """Chạy script cho các dòng được chọn"""
        selected_rows = self._target_rows()
        if not selected_rows:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn ít nhất một dòng để chạy!")
            return
        for row in selected_rows:
            self._run_row(row, script)

    def _run_selected_sequential(self, script: str, label: str, step_name: str):
        """Chạy script cho các dòng được chọn và cập nhật workflow"""
        selected_rows = self._target_rows()
        if not selected_rows:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn ít nhất một dòng để chạy!")
            return
        
        # Store current step for completion tracking
        self.current_step = step_name
        self.selected_rows_count = len(selected_rows)
        self.completed_rows_count = 0
        
        for row in selected_rows:
            self._run_row(row, script)

    def _run_all(self, script: str, label: str):
        for r in range(len(self.accounts)):
            self._run_row(r, script)

    def _parse_groups_text(self, groups_text: str):
        groups = []
        for part in str(groups_text or "").split("|"):
            part = part.strip()
            if ":" not in part:
                continue
            order, group_id = [p.strip() for p in part.split(":", 1)]
            if order.isdigit() and group_id.isdigit():
                groups.append((order, group_id))
        return groups

    def _group_id_by_order(self, groups_text: str, order: str):
        for group_order, group_id in self._parse_groups_text(groups_text):
            if group_order == str(order):
                return group_id
        return ""

    def _on_worker_groups_update(self, row: int, groups_text: str):
        if row >= len(self.accounts):
            return
        self.accounts[row]["groups"] = groups_text
        group_ids = [group_id for _, group_id in self._parse_groups_text(groups_text)]
        current_group_id = self.accounts[row].get("group_id", "")
        if not current_group_id or current_group_id not in group_ids:
            first_group_id = group_ids[0] if group_ids else ""
            if first_group_id:
                self.accounts[row]["group_id"] = first_group_id
        self._update_row(row, self.accounts[row])
        save_accounts(self.accounts)

    def _on_worker_info_update(self, row: int, info: dict):
        if row >= len(self.accounts):
            return
        updated = False
        for key in ACC_KEYS:
            value = info.get(key)
            if value is None:
                continue
            value = str(value).strip()
            if value:
                self.accounts[row][key] = value
                updated = True
        if updated:
            normalize_romaji_fields(self.accounts[row])
            self._update_row(row, self.accounts[row])
            save_accounts(self.accounts)

    def _on_finished(self, row: int, result: str):
        self._set_status(row, result)
        if row < len(self.accounts):
            self.accounts[row]["status"] = result
            save_accounts(self.accounts)
        
        # Check if this was part of a sequential workflow
        if hasattr(self, 'current_step') and hasattr(self, 'selected_rows_count'):
            self.completed_rows_count += 1
            
            # If all selected rows completed, check if successful and update workflow
            if self.completed_rows_count >= self.selected_rows_count:
                if result.startswith("✅"):  # Success
                    self._update_workflow_status(self.current_step)
                
                # Reset tracking
                delattr(self, 'current_step')
                delattr(self, 'selected_rows_count')
                self.completed_rows_count = 0

    def _update_workflow_status(self, completed_step: str):
        """Update workflow status and show next button"""
        self.workflow_status[completed_step] = True
        
        if completed_step == "create_acc":
            QMessageBox.information(self, "Hoàn thành", "Tạo tài khoản thành công!")
        elif completed_step == "task3":
            QMessageBox.information(self, "Hoàn thành", "Nhiệm vụ 3 thành công! Quy trình hoàn tất.")

    def add_empty_row(self):
        """Thêm một dòng trống vào cuối bảng"""
        acc = empty_acc()
        acc["status"] = "Mới"
        self.accounts.append(acc)
        self._append_row(acc)
        save_accounts(self.accounts)
        self._apply_filter()
        new_row = self.table.rowCount() - 1
        item = self.table.item(new_row, 0)
        if item:
            item.setCheckState(Qt.Checked)
        self.table.scrollToItem(self.table.item(new_row, 0))

    def insert_row_above(self):
        """Chèn dòng trống vào TRƯỚC dòng đang chọn (hoặc đầu bảng nếu không có gì được chọn)"""
        selected = self._target_rows()
        insert_at = selected[0] if selected else 0
        self._insert_row_at(insert_at)

    def _insert_row_at(self, insert_at: int):
        """Chèn dòng trống tại vị trí insert_at"""
        acc = empty_acc()
        acc["status"] = "Mới"
        self.accounts.insert(insert_at, acc)
        self.table.insertRow(insert_at)
        check_item = QTableWidgetItem("")
        check_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
        check_item.setCheckState(Qt.Checked)
        check_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(insert_at, 0, check_item)
        for c, key in enumerate(ACC_KEYS, start=1):
            self._set_cell_text(insert_at, c, acc.get(key, ""), center=(key == "status"))
        save_accounts(self.accounts)
        self._apply_filter()
        self.table.scrollToItem(self.table.item(insert_at, 0))

    def _move_row(self, from_row: int, to_row: int):
        """Di chuyển dòng (kéo thả) từ from_row đến to_row"""
        if from_row == to_row or from_row < 0 or to_row < 0:
            return
        acc = self.accounts.pop(from_row)
        self.accounts.insert(to_row, acc)
        self._load_table()
        save_accounts(self.accounts)
        item = self.table.item(to_row, 0)
        if item:
            item.setCheckState(Qt.Checked)

    # ── import ─────────────────────────────────────────────────────────────────
    def import_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file tài khoản", "", "Text/CSV (*.txt *.csv);;All (*)"
        )
        if not path:
            return
        added = 0
        with open(path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                # ho|ten|ho1|ten1|hophienam|tenphienam|mabuudien|diachi|sdt|mail|passmail|eid|group_id|groups
                keys_order = ["ho","ten","ho1","ten1","hophienam","tenphienam",
                              "mabuudien","diachi","sdt","mail","passmail","eid","group_id","groups"]
                acc = empty_acc()
                for i, k in enumerate(keys_order):
                    if i < len(parts):
                        acc[k] = parts[i].strip()
                normalize_romaji_fields(acc)
                self.accounts.append(acc)
                self._append_row(acc)
                added += 1
        save_accounts(self.accounts)
        self._apply_filter()
        QMessageBox.information(self, "Nhập xong", f"Đã thêm {added} tài khoản.")

    def export_excel(self):
        default_name = datetime.now().strftime("%d-%m-%Y.xlsx")
        default_path = os.path.join(BASE, default_name)
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Chọn nơi lưu file Excel",
            default_path,
            "Excel Workbook (*.xlsx)"
        )
        if not path:
            return
        if not path.lower().endswith(".xlsx"):
            path += ".xlsx"

        try:
            self._write_xlsx(path, COLS[1:], ACC_KEYS, self.accounts)
            QMessageBox.information(self, "Xuất xong", f"Đã xuất {len(self.accounts)} tài khoản:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi xuất file", str(e))

    def _write_xlsx(self, path: str, headers: list, keys: list, rows: list):
        def col_name(index: int):
            name = ""
            while index:
                index, rem = divmod(index - 1, 26)
                name = chr(65 + rem) + name
            return name

        def cell_xml(row_index: int, col_index: int, value):
            ref = f"{col_name(col_index)}{row_index}"
            text = xml_escape(str(value if value is not None else ""))
            return f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>'

        sheet_rows = []
        header_cells = "".join(cell_xml(1, i + 1, header) for i, header in enumerate(headers))
        sheet_rows.append(f'<row r="1">{header_cells}</row>')

        for row_index, acc in enumerate(rows, start=2):
            cells = "".join(cell_xml(row_index, col_index + 1, acc.get(key, "")) for col_index, key in enumerate(keys))
            sheet_rows.append(f'<row r="{row_index}">{cells}</row>')

        last_col = col_name(len(headers))
        dimension = f"A1:{last_col}{max(1, len(rows) + 1)}"
        sheet_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <dimension ref="{dimension}"/>
  <sheetViews><sheetView workbookViewId="0"/></sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <cols>{''.join(f'<col min="{i}" max="{i}" width="18" customWidth="1"/>' for i in range(1, len(headers) + 1))}</cols>
  <sheetData>{''.join(sheet_rows)}</sheetData>
</worksheet>'''

        workbook_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="Accounts" sheetId="1" r:id="rId1"/></sheets>
</workbook>'''
        workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''
        root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>'''
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>'''
        styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="1"><fill><patternFill patternType="none"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
</styleSheet>'''

        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", content_types)
            z.writestr("_rels/.rels", root_rels)
            z.writestr("xl/workbook.xml", workbook_xml)
            z.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
            z.writestr("xl/worksheets/sheet1.xml", sheet_xml)
            z.writestr("xl/styles.xml", styles_xml)

    # ── delete ─────────────────────────────────────────────────────────────────
    def delete_selected(self):
        rows = sorted(self._target_rows(), reverse=True)
        if not rows:
            return
        if QMessageBox.question(self,"Xác nhận",f"Xóa {len(rows)} dòng?",
                                QMessageBox.Yes|QMessageBox.No) != QMessageBox.Yes:
            return
        for r in rows:
            self.table.removeRow(r)
            if r < len(self.accounts):
                self.accounts.pop(r)
        save_accounts(self.accounts)
        self._apply_filter()

    # ── context menu ───────────────────────────────────────────────────────────
    def _context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        menu = QMenu(self)

        a_add = QAction("➕  Thêm tài khoản từ file", self)
        a_add.triggered.connect(self.import_file)
        menu.addAction(a_add)

        a_add_empty = QAction("📝  Thêm dòng trống (cuối)", self)
        a_add_empty.triggered.connect(self.add_empty_row)
        menu.addAction(a_add_empty)

        if row >= 0:
            a_insert_above = QAction("⬆  Chèn dòng trống phía trên", self)
            a_insert_above.triggered.connect(lambda: self._insert_row_at(row))
            menu.addAction(a_insert_above)

            a_insert_below = QAction("⬇  Chèn dòng trống phía dưới", self)
            a_insert_below.triggered.connect(lambda: self._insert_row_at(row + 1))
            menu.addAction(a_insert_below)

            menu.addSeparator()
            a_edit = QAction("✏️  Chỉnh sửa dòng này", self)
            a_edit.triggered.connect(lambda: self._edit_row(row))
            menu.addAction(a_edit)

            a_copy_cell = QAction("📋  Copy ô này", self)
            a_copy_cell.triggered.connect(lambda: self._copy_cell_at(row, self.table.columnAt(pos.x())))
            menu.addAction(a_copy_cell)

            a_copy_row = QAction("📋  Copy dòng này", self)
            a_copy_row.triggered.connect(lambda: self._copy_row(row))
            menu.addAction(a_copy_row)

            menu.addSeparator()
            a_create = QAction("▶  Tạo tài khoản  (test1.py)", self)
            a_create.triggered.connect(lambda: self._run_row(row,"test1.py"))
            menu.addAction(a_create)

            a_check_group = QAction("🔎  CheckNhom", self)
            a_check_group.triggered.connect(lambda: self._check_groups_row(row))
            menu.addAction(a_check_group)

            group_items = self._parse_groups_text(self.accounts[row].get("groups", ""))
            if not group_items:
                group_items = [("1", self.accounts[row].get("group_id", ""))]
            for group_order, group_id in group_items:
                a_group = QAction(f"▶  Làm Nhiệm vụ Nhóm {group_order}  (test3.py)", self)
                a_group.triggered.connect(lambda checked=False, gid=group_id: self._run_row_group(row, "test3.py", gid))
                menu.addAction(a_group)

            a_xoa = QAction("📵  Xóa số  (xoaso.py)", self)
            a_xoa.triggered.connect(lambda: self._run_row(row,"xoaso.py"))
            menu.addAction(a_xoa)

            menu.addSeparator()
            a_lp = QAction("💎  Xem LP & Danh sách SĐT", self)
            a_lp.triggered.connect(lambda: self._show_lp_info(row))
            menu.addAction(a_lp)

            a_charge = QAction("🚀  Tạo LP (mua LP)", self)
            a_charge.triggered.connect(lambda: self._create_lp(row))
            menu.addAction(a_charge)

            menu.addSeparator()
            a_del = QAction("🗑  Xóa dòng này", self)
            a_del.triggered.connect(lambda: self._delete_row(row))
            menu.addAction(a_del)

        menu.exec_(QCursor.pos())

    def _edit_row(self, row: int):
        if row >= len(self.accounts):
            return
        dlg = EditDialog(self.accounts[row], self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            normalize_romaji_fields(data)
            self.accounts[row].update(data)
            self._update_row(row, self.accounts[row])
            save_accounts(self.accounts)

    def _delete_row(self, row: int):
        if QMessageBox.question(self,"Xác nhận","Xóa dòng này?",
                                QMessageBox.Yes|QMessageBox.No) != QMessageBox.Yes:
            return
        self.table.removeRow(row)
        if row < len(self.accounts):
            self.accounts.pop(row)
        save_accounts(self.accounts)
        self._apply_filter()

    def _show_lp_info(self, row: int):
        """Login và hiển thị LP + danh sách SĐT của tài khoản"""
        if row >= len(self.accounts):
            return
        acc = dict(self.accounts[row])
        acc["_proxy"] = self._next_proxy()
        sett = self.settings_tab.get_settings()
        mail = acc.get("mail", f"dòng {row + 1}")

        dlg = LPInfoDialog(mail, self)

        worker = LPInfoWorker(acc, sett)
        worker.finished.connect(lambda lp, phones: dlg.set_result(lp, phones))
        worker.error.connect(lambda msg: dlg.set_error(msg))
        worker.start()
        # Giữ reference tránh bị GC
        self._lp_worker = worker

        dlg.exec_()

    def _create_lp(self, row: int):
        """Mở dialog nhập số LP → chạy worker → lưu mã số vào cột lp_code"""
        if row >= len(self.accounts):
            return
        acc  = dict(self.accounts[row])
        acc["_proxy"] = self._next_proxy()
        sett = self.settings_tab.get_settings()
        mail = acc.get("mail", f"dòng {row + 1}")

        dlg = LPChargeDialog(mail, self)

        def on_charge(lp_amount: int):
            worker = LPChargeWorker(acc, sett, lp_amount)

            def on_done(code: str):
                dlg.set_result(code)
                # Lưu mã số vào data và bảng
                self.accounts[row]["lp_code"] = code
                lp_col = ACC_KEYS.index("lp_code") + 1
                self._set_cell_text(row, lp_col, code)
                item = self.table.item(row, lp_col)
                if item:
                    item.setForeground(QColor("#22c55e"))
                save_accounts(self.accounts)

            worker.finished.connect(on_done)
            worker.error.connect(dlg.set_error)
            worker.start()
            self._lp_charge_worker = worker  # giữ reference

        dlg.do_charge.connect(on_charge)
        dlg.exec_()

# ── Main window ────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoLinksMate  v1.0")
        self.setMinimumSize(1200, 680)
        tabs = QTabWidget()
        self.settings_tab  = SettingsTab()
        self.settings = self.settings_tab.settings
        self.accounts_tab  = AccountsTab(self.settings_tab)
        tabs.addTab(self.accounts_tab, "📋  Tài khoản & Chạy")
        tabs.addTab(self.settings_tab, "⚙️  Cài đặt")
        self.setCentralWidget(tabs)

        self.btn_theme = QPushButton()
        self.btn_theme.setFixedWidth(44)
        self.btn_theme.clicked.connect(self._toggle_theme)
        self.statusBar().addPermanentWidget(self.btn_theme)
        self._apply_theme(self.settings.get("theme", "dark"))
        self.statusBar().showMessage("Sẵn sàng")

    def _apply_theme(self, theme: str):
        self.settings["theme"] = "light" if theme == "light" else "dark"
        qss = LIGHT_QSS if self.settings["theme"] == "light" else QSS
        QApplication.instance().setStyleSheet(qss)
        self.setStyleSheet(qss)
        if self.settings["theme"] == "light":
            self.btn_theme.setText("☀")
            self.statusBar().setStyleSheet("background:#e2e8f0;color:#1d4ed8;font-size:12px;padding:2px 10px;")
        else:
            self.btn_theme.setText("☾")
            self.statusBar().setStyleSheet("background:#1a2035;color:#60a5fa;font-size:12px;padding:2px 10px;")

    def _toggle_theme(self):
        next_theme = "light" if self.settings.get("theme", "dark") != "light" else "dark"
        self._apply_theme(next_theme)
        self.settings_tab.settings["theme"] = self.settings["theme"]
        save_settings(self.settings)

# ── entry ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
