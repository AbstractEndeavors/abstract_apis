from PyQt6.QtCore import QTimer

def emit(self, record):
    # Run the UI update on the main thread
    msg = self.format(record)
    QTimer.singleShot(0, lambda m=msg: (
        self.widget.append(m),
        self.widget.ensureCursorVisible()
    ))
