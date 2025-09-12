from __future__ import annotations
import os
from abstract_gui import get_for_all_tabs
CONSOLE_DIR_PATH = os.path.abspath(__file__)
CONSOLE_ABS_DIR = os.path.dirname(CONSOLE_DIR_PATH)
get_for_all_tabs(CONSOLE_ABS_DIR)
from .apiTab import apiConsole
from abstract_gui.QT6.startConsole import startConsole 
import traceback,sys
def startApiConsole():
    startConsole(apiConsole)
# framework/base_console.py
import logging, sys
from PyQt6.QtCore import QObject, QThread
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QTabWidget,  QApplication
)



from abstract_gui.QT6 import attach_textedit_to_logs, add_logs_tab
from  abstract_gui.QT6 import install_qt_logging

def init_logging():
    """
    Call once after QApplication is created and before showing any windows.
    """
    install_qt_logging()



class UiOnceMixin:
    """
    Mixin that ensures _build_ui() runs once and you always have a layout().
    """
    def _ensure_layout(self):
        if self.layout() is None:
            QVBoxLayout(self)

    def _build_ui_once(self, builder):
        if getattr(self, "_ui_built", False):
            return
        self._ui_built = True
        self._ensure_layout()
        builder()

class LogAreaMixin:
    """
    Mixin that gives you a ready-made log area attached to robust_utils.
    """
    def add_inline_log(self, parent_layout=None, *, label: str = "Log", tail_file: str | None = None) -> QPlainTextEdit:
        parent_layout = parent_layout or self.layout()
        row = QVBoxLayout()
        row.addWidget(QLabel(label))
        log_view = QPlainTextEdit(self)
        log_view.setReadOnly(True)
        row.addWidget(log_view)
        parent_layout.addLayout(row)
        # ONE attach call per widget
        attach_textedit_to_logs(log_view, tail_file=tail_file)  # None = live stream only
        self.log_view = log_view
        return log_view

    def add_logs_tab(self, tabs: QTabWidget, *, title: str = "Logs"):
        # Uses robust_utils.LogConsole under the hood
        return add_logs_tab(tabs, title=title)

class BaseConsole(QWidget, UiOnceMixin, LogAreaMixin):
    """
    Your consoles can subclass this. You get:
      - _build_ui_once(...) guard
      - add_inline_log(...)
      - add_logs_tab(...)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ensure_layout()

    def get_logger(self, name: str):
        return logging.getLogger(name)
# framework/threads.py


def run_worker(worker: QObject, *, on_success=None, on_failure=None):
    """
    Move a QObject(worker) with .run(), .success(str), .failure(str) into a QThread safely.
    Returns (thread, worker).
    """
    thread = QThread()
    worker.moveToThread(thread)

    if hasattr(worker, "run"):
        thread.started.connect(worker.run)

    if on_success and hasattr(worker, "success"):
        worker.success.connect(on_success)
    if on_failure and hasattr(worker, "failure"):
        worker.failure.connect(on_failure)

    # Ensure the thread actually stops and objects are cleaned up
    if hasattr(worker, "success"):
        worker.success.connect(thread.quit)
    if hasattr(worker, "failure"):
        worker.failure.connect(thread.quit)

    thread.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    thread.start()
    return thread, worker
def main():
    app = QApplication(sys.argv)
    init_logging()  # <— install robust logger once

    w = apiConsole()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
