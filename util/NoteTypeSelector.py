from aqt.qt import QDialog, QLabel, QVBoxLayout, QCheckBox, QPushButton
from aqt import QButtonGroup, QRadioButton, QScrollArea, QWidget, mw
from aqt.utils import showInfo

class NoteTypeSelector(QDialog):
    def __init__(self, deck_name=None, c_field=None, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("Note type selection")
        self.setFixedWidth(500)
        
        # Main layout (contains the label and then the scroll area)
        self.main_layout = QVBoxLayout(self)
        
        # Top instructions for user
        message = f"""
        Configuring for: {c_field}
        Searching inside deck: {deck_name}

        Choose a note type to search for within {deck_name}:
        """
        self.label = QLabel(message)
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

        # Returning these items
        self.selected_note_type = None
        self.card_type_restriction = False
        self.key_restriction = False

        # Add notetype options (usually will contain one)
        # Possible WIP: reduce down only to note types present in deck
        all_note_types = mw.col.models.all()
        all_note_type_names = [nt["name"] for nt in all_note_types]

        # Choice buttons for selecting notetype
        self.buttongroup = QButtonGroup()
        radios = []
        for nt in all_note_type_names:
            radio = QRadioButton(nt)
            radio.note_type = nt
            radios.append(radio)
        [self.buttongroup.addButton(x) for x in radios]
        [self.scroll_layout.addWidget(x) for x in radios]
        self.buttongroup.buttonClicked.connect(self.selection_changed)
        self.selected_note_type = None

        # Allow checkbox options to prompt for card type restriction or key restriction
        self.label_2 = QLabel(f"Options to restrict search to certain cards:")
        self.main_layout.addWidget(self.label_2)
        self.checkboxes = []
        for option in ["Restrict search to a particular card type", "Restrict search to a key in set field"]:
            checkbox = QCheckBox(option)
            self.main_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        # Submit button
        self.submit_btn = QPushButton("Continue")
        self.submit_btn.clicked.connect(self.accept_selection)  # Connect to accept logic
        self.main_layout.addWidget(self.submit_btn)

    def selection_changed(self):
        """Update the selected_note_type when a radio button is clicked."""
        selected = self.buttongroup.checkedButton().text()
        if selected:
            self.selected_note_type = selected

    def accept_selection(self):
        """Accept the dialog if a note type is selected, or show a warning otherwise."""
        if self.selected_note_type is not None:
            self.card_type_restriction = True if self.checkboxes[0].isChecked() else False
            self.key_restriction = True if self.checkboxes[1].isChecked() else False
            self.accept()  # Set dialog result to QDialog.Accepted
        else:
            showInfo("Please select a note type before continuing.")

    def exec(self):
        """Override exec to return the list of selected deck names."""
        result = super().exec()  # This shows the dialog
        if self.selected_note_type:
            showInfo(f"{', '.join([self.selected_note_type, str(self.card_type_restriction), str(self.key_restriction)])}")
            return self.selected_note_type, self.card_type_restriction, self.key_restriction

