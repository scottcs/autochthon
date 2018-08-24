"""Entity editor."""
import sys
from typing import Optional

from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QWidget, QVBoxLayout


class Form(QDialog):
    """Form"""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Entity Editor')
        self.edit = QLineEdit('Write my name here...')
        self.button = QPushButton('Show Greetings')
        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.button.clicked.connect(self.greetings)

    def greetings(self) -> None:
        """Give a nice greeting."""
        print(f'Hello {self.edit.text()}')


def main() -> int:
    """ Main function """
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
