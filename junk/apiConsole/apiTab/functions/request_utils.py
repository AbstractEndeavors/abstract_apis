from ..imports import *
import logging
def _on_request_success(self, txt):
    print('_on_request_success')
    try:
        if not self.append_chk.isChecked():
            self.response_output.clear()
        #self.response_output.moveCursor(QTextCursor.MoveOperation.End)
        #self.response_output.insertPlainText(f"✔ {self._current_method} {self._current_url}\n{txt}\n")
        logging.info(f"✔ {self._current_method} {self._current_url}")
    except Exception as e:
        print(f"{e}")
    finally:
        self.send_button.setEnabled(True)
        QApplication.restoreOverrideCursor()
        self._active_thread = None
        self._active_worker = None

def _on_request_failure(self, err):
    print('_on_request_failure')
    try:
        if not self.append_chk.isChecked():
            self.response_output.clear()
        self.response_output.moveCursor(QTextCursor.MoveOperation.End)
        self.response_output.insertPlainText(err + "\n")
        logging.error(err)
    except Exception:
        logging.exception("Error handling failure slot")
    finally:
        self.send_button.setEnabled(True)
        QApplication.restoreOverrideCursor()
        self._active_thread = None
        self._active_worker = None



def send_request(self, *args, **kwargs):
    # ... collect ep/base/url/method/headers/params as you already do ...
    self.send_button.setEnabled(False)
    QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
    print(self.base_combo.currentText().rstrip('/'))
    worker = RequestWorker(self.base_combo.currentIndex(), url, headers, params)  # your QObject with success/failure
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
