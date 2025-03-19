from aqt.qt import QDialog, QLabel, QVBoxLayout, QListWidget, QPushButton, Qt
from aqt import mw
from aqt.utils import showInfo

class DragDropSelector(QDialog):
    def __init__(self, dialog: str, deck_list=None, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("Ordering")
        self.setFixedWidth(300)
        self.layout = QVBoxLayout()

        # Instructions for user
        self.label = QLabel(dialog)
        self.layout.addWidget(self.label)

        self.list_widget = QListWidget()
        self.list_widget.addItems(deck_list)
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)

        # Add the "Continue" button
        self.continue_btn = QPushButton("Continue")
        self.continue_btn.clicked.connect(self.on_continue)
        self.layout.addWidget(self.continue_btn)

    def on_continue(self):
        """Gets the list in order"""
        self.ordered_decks = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        self.accept()
        showInfo(f"Order: {', '.join(self.ordered_decks)}")
        return self.ordered_decks

    def exec(self):
        """Override exec to return the list of selected deck names."""
        result = super().exec()  # This shows the dialog
        if self.ordered_decks:
            return self.ordered_decks
