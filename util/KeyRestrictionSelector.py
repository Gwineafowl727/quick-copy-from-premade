from aqt.qt import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton
from aqt import mw
from aqt.utils import showInfo

class KeyRestrictionSelector(QDialog):
    def __init__(self, deck_name=None, c_field=None, note_type_name=None, key_field_name=None, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("Note type selection")
        self.setFixedWidth(500)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Top instructions for user
        message = f"""
        Configuring for: {c_field}
        Searching inside deck: {deck_name}
        Searching in note type: {note_type_name}
        Checking for key inside field: {key_field_name}

        Type the expected key corresponding to {key_field_name} (i.e. "Vocabulary", "Kanji", etc.):
        """
        self.label = QLabel(message)
        self.layout.addWidget(self.label)

        # Add the Line edit
        self.line_edit = QLineEdit()
        self.layout.addWidget(self.line_edit)

        # Add the "Continue" button
        self.continue_btn = QPushButton("Continue")
        self.continue_btn.clicked.connect(self.on_continue)
        self.layout.addWidget(self.continue_btn)

    def on_continue(self):
        """Gets the string typed in the box"""

        self.key = self.line_edit.text()
        self.accept()

    def exec(self):
        """Overrides exec to return string"""
        result = super().exec()
        if self.key:
            showInfo(self.key)
            return self.key
