from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QDialogButtonBox, QTabWidget


class GroupCheckDetailDialog(QDialog):
    def __init__(self, mail: str, details: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Chi tiết Check nhóm — {mail}")
        self.resize(760, 520)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.lbl_title = QLabel("📋 Chi tiết từng nhóm")
        self.lbl_title.setStyleSheet("font-size:14px;font-weight:700;")
        layout.addWidget(self.lbl_title)

        self.tabs = QTabWidget(self)
        for idx, item in enumerate(details, start=1):
            order = item.get("order", idx)
            group_id = item.get("group_id", "")
            label = item.get("label", "")
            lp = item.get("lp", "N/A")
            phones = item.get("phones") or []
            phone_text = ", ".join(phones) if phones else "N/A"

            tab_text = f"Nhóm {order}"
            editor = QTextEdit(self)
            editor.setReadOnly(True)
            editor.setPlainText(
                f"Group ID: {group_id}\n"
                f"Tên nhóm: {label or '—'}\n"
                f"LP: {lp}\n"
                f"SĐT: {phone_text}"
            )
            self.tabs.addTab(editor, tab_text)

        layout.addWidget(self.tabs)

        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
