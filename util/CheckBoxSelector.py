from aqt.qt import QDialog, QLabel, QVBoxLayout, QCheckBox, QPushButton
from aqt import QScrollArea, QWidget, mw
from aqt.utils import showInfo

class CheckBoxSelector(QDialog):
    def __init__(self, dialog: str, item_list=None, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("Checkbox selection")
        self.setFixedWidth(300)

        # Main layout (contains the label and then the scroll area)
        self.main_layout = QVBoxLayout(self)
        
        # Instructions for user
        self.label = QLabel(dialog)
        self.main_layout.addWidget(self.label)

        # Create a scrollable area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Create a widget to hold the radio buttons
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)

        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)

        # Add checkboxes for multiple choice
        self.checkboxes = []
        for option in item_list:
            checkbox = QCheckBox(option)
            self.scroll_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
        
        # Add the "Continue" button
        self.continue_btn = QPushButton("Continue")
        self.continue_btn.clicked.connect(self.on_continue)
        self.main_layout.addWidget(self.continue_btn)

    def on_continue(self):
        """Collect the selected checkbox contents when the button is clicked."""
        self.selected_items = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
        self.accept()  # Close the dialog
        showInfo(f"{', '.join(self.selected_items)}")
        return self.selected_items

    def exec(self):
        """Override exec to return the list of selected items."""
        result = super().exec()  # This shows the dialog
        if self.selected_items:
            return self.selected_items
