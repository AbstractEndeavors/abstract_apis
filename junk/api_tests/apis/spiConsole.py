# framework/base_console.py
from __future__ import annotations
import logging, sys
from PyQt6.QtCore import QObject, QThread
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QTabWidget,  QApplication
)

# apiConsole/functions/request_utils.py (trimmed)
from framework.threads import run_worker
from ..imports import *
import logging

from .initFuncs import initFuncs
from .imports import *

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



def send_request(self, *args, **kwargs):
    # ... collect ep/base/url/method/headers/params as you already do ...
    self.send_button.setEnabled(False)
    QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)

    worker = RequestWorker(method, url, headers, params)  # your QObject with success/failure
    self._current_method = method
    self._current_url = url

    def _done():
        self.send_button.setEnabled(True)
        QApplication.restoreOverrideCursor()
        self._active_thread = None
        self._active_worker = None

    # wrap your existing slots to ensure UI consistency
    def on_success(txt: str):
        try:
            if not self.append_chk.isChecked():
                self.response_output.clear()
            self.response_output.insertPlainText(f"✔ {self._current_method} {self._current_url}\n{txt}\n")
            logging.info("✔ %s %s", self._current_method, self._current_url)
        finally:
            _done()

    def on_failure(err: str):
        try:
            if not self.append_chk.isChecked():
                self.response_output.clear()
            self.response_output.insertPlainText(err + "\n")
            logging.error(err)
        finally:
            _done()

    t, w = run_worker(worker, on_success=on_success, on_failure=on_failure)
    self._active_thread = t
    self._active_worker = w
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

    w = reactRunnerConsole()
    w.show()
    sys.exit(app.exec())

class apiConsole(BaseConsole):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("API Console for abstract_apis")
        self.api_prefix = "/api"
        self.resize(900, 1000)
        self.config_cache = {}

        self._build_ui_once(self._build_ui)   # guard
        self._setup_logging()                  # optional level tweak

    def _build_ui(self):
        layout = self.layout()

        # ... your existing UI creation ...
        # make the big form, tables etc.

        # add Logs inline at the bottom and attach to robust stream
        self.add_inline_log(layout, label="Logs", tail_file=None)  # None = no file tail

        # If you want a “Response” box too, keep your QTextEdit as before.

    def _setup_logging(self):
        import logging
        logging.getLogger().setLevel(logging.DEBUG)

apiConsole = initFuncs(apiConsole)
if __name__ == "__main__":
    main()
