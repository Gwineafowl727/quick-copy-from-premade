
from aqt.qt import QDialog, QLabel, QVBoxLayout, QScrollArea, QPushButton, QWidget
from aqt import QButtonGroup, QRadioButton, mw
from aqt.utils import showInfo

class DuplicateSelector(QDialog):

    def get_audio_embeds():
        pass

    def __init__(self, result=None, field_name=None, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("Duplicate selection")
        self.setFixedWidth(400)

        # Main layout (contains the label and then the scroll area)
        self.main_layout = QVBoxLayout(self)
        
        # Instructions for user
        self.label = QLabel(f"Select which content to enter into the field {field_name}:")
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


        # Choice buttons for selecting field
        self.buttongroup = QButtonGroup()
        radios = []
        for r in result:



            radio = QRadioButton(field)
            radio.field = field
            radios.append(radio)
        [self.buttongroup.addButton(x) for x in radios]
        [self.scroll_layout.addWidget(x) for x in radios]
        self.buttongroup.buttonClicked.connect(self.selection_changed)
        self.selected_field = None

        # Submit button
        self.submit_btn = QPushButton("Continue")
        self.submit_btn.clicked.connect(self.accept_selection)  # Connect to accept logic
        self.main_layout.addWidget(self.submit_btn)

    def selection_changed(self):
        """Update the selected_field when a radio button is clicked."""
        selected = self.buttongroup.checkedButton()
        if selected:
            self.selected_field = selected.field

    def accept_selection(self):
        """Accept the dialog if a field is selected, or show a warning otherwise."""
        if self.selected_field is not None:
            self.accept()  # Set dialog result to QDialog.Accepted
        else:
            showInfo("Please select a field before continuing.")

    def exec(self):
        """Override exec to return the selected field."""
        result = super().exec()  # This shows the dialog
        if self.selected_field:
            return self.selected_field


