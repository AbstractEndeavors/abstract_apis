#!/usr/bin/env python3
# temp_py_qt6.py — GUI front-end for abstract_apis (Qt6 / PySide6)

import sys
import json
import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QTextEdit, QComboBox, QMessageBox,
    QTableWidget, QSizePolicy, QTableWidgetItem, QAbstractItemView
)
from PyQt6.QtCore import Qt, QUrl, QTimer, QByteArray
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QMessageBox, QMainWindow, QTableWidgetSelectionRange
    )
from abstract_apis import getRequest, postRequest


# ─── Configuration ──────────────────────────────────────────────────────
PREDEFINED_BASE_URLS = [
    "https://abstractendeavors.com",
    "https://clownworld.biz",
    "https://typicallyoutliers.com",
    "https://thedailydialectics.com",
]
PREDEFINED_HEADERS = [
    ("Content-Type", "application/json"),
    ("Accept", "application/json"),
    ("Authorization", "Bearer "),
]


# ─── Logging Handler ───────────────────────────────────────────────────
class QTextEditLogger(logging.Handler):
    def __init__(self, widget: QTextEdit):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.widget.append(msg)
        self.widget.ensureCursorVisible()


# ─── Main GUI ──────────────────────────────────────────────────────────
class APIConsole(QWidget):
    def __init__(self,
                 default_prefix: str = "/api"):
        super().__init__()
        self.setWindowTitle("API Console for abstract_apis (Qt6)")
        self.resize(900, 950)
        self._api_prefix = default_prefix if default_prefix.startswith("/") else f"/{default_prefix}"

        self.config_cache = {}  # cache per-endpoint settings
        self._build_ui()
        self._wire()

        self._setup_logging()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Base URL selection
        layout.addWidget(QLabel("Base URL:"))
        self.base_combo = QComboBox(self)
        self.base_combo.setEditable(True)
        self.base_combo.addItems(PREDEFINED_BASE_URLS)
        self.base_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        layout.addWidget(self.base_combo)

        # Prefix row
        row = QHBoxLayout()
        row.addWidget(QLabel("API Prefix:"))
        self.prefix_in = QLineEdit(self._api_prefix, self)
        self.prefix_in.setPlaceholderText("/api")
        self.prefix_in.setClearButtonEnabled(True)
        row.addWidget(self.prefix_in)

        self.detect_btn = QPushButton("Detect", self)
        row.addWidget(self.detect_btn)
        layout.addLayout(row)



        # Endpoints table
        layout.addWidget(QLabel("Endpoints (select one row):"))
        self.endpoints_table = QTableWidget(0, 2, self)
        self.endpoints_table.setHorizontalHeaderLabels(["Endpoint Path", "Methods"])
        self.endpoints_table.horizontalHeader().setStretchLastSection(True)
        self.endpoints_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.endpoints_table.setFixedHeight(240)
        self.endpoints_table.cellClicked.connect(self.on_endpoint_selected)
        layout.addWidget(self.endpoints_table)

        # Method override selector
        row = QHBoxLayout()
        row.addWidget(QLabel("Override Method:"))
        self.method_box = QComboBox(self)
        self.method_box.addItems(["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
        row.addWidget(self.method_box)
        layout.addLayout(row)

        # Headers table
        layout.addWidget(QLabel("Headers (check to include):"))
        self.headers_table = QTableWidget(len(PREDEFINED_HEADERS) + 1, 3, self)
        self.headers_table.setHorizontalHeaderLabels(["Use", "Key", "Value"])
        self.headers_table.setFixedHeight(220)
        layout.addWidget(self.headers_table)

        for i, (k, v) in enumerate(PREDEFINED_HEADERS):
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk.setCheckState(Qt.CheckState.Checked)
            self.headers_table.setItem(i, 0, chk)
            self.headers_table.setItem(i, 1, QTableWidgetItem(k))
            self.headers_table.setItem(i, 2, QTableWidgetItem(v))

        # trailing blank row
        empty_chk = QTableWidgetItem()
        empty_chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        empty_chk.setCheckState(Qt.CheckState.Unchecked)
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 0, empty_chk)
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 1, QTableWidgetItem(""))
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 2, QTableWidgetItem(""))
        self.headers_table.cellChanged.connect(self._maybe_add_header_row)

        # Body / Query-Params table
        layout.addWidget(QLabel("Body / Query-Params (key → value):"))
        self.body_table = QTableWidget(1, 2, self)
        self.body_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.body_table.setFixedHeight(220)
        self.body_table.setItem(0, 0, QTableWidgetItem(""))
        self.body_table.setItem(0, 1, QTableWidgetItem(""))
        self.body_table.cellChanged.connect(self._maybe_add_body_row)
        layout.addWidget(self.body_table)

        # Send button
        # Buttons
        brow = QHBoxLayout()
        self.fetch_btn = QPushButton(self._fetch_label(), self)
        self.send_btn = QPushButton("▶ Send", self)
        self.abort_btn = QPushButton("■ Abort", self)
        self.abort_btn.setEnabled(False)
        brow.addWidget(self.fetch_btn)
        brow.addStretch(1)
        brow.addWidget(self.send_btn)
        brow.addWidget(self.abort_btn)
        layout.addLayout(brow)

        # Response
        layout.addWidget(QLabel("Response:"))
        self.response_output = QTextEdit(self)
        self.response_output.setReadOnly(True)
        self.response_output.setFixedHeight(280)
        layout.addWidget(self.response_output)

        # Logs
        layout.addWidget(QLabel("Logs:"))
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(160)
        layout.addWidget(self.log_output)
        
    def _wire(self):
        self.prefix_in.textChanged.connect(self._on_prefix_changed)
        self.fetch_btn.clicked.connect(self.fetch_endpoints)
        self.send_btn.clicked.connect(self.send_request)
        self.abort_btn.clicked.connect(self.abort_request)
        self.headers_table.cellChanged.connect(self._maybe_add_header_row)
        self.body_table.cellChanged.connect(self._maybe_add_body_row)
        self.detect_btn.clicked.connect(self.detect_prefix)
    def _build_url(self, ep: str) -> str:
        base = (self.base_combo.currentText().strip().rstrip('/'))
        if not base:
            raise ValueError("Base URL is empty.")
        pref = self._normalized_prefix().rstrip('/')
        ep = ep.strip()
        ep = ep if ep.startswith('/') else '/' + ep
        return f"{base}{pref}{ep}"
    def _on_prefix_changed(self, _txt: str):
        self.fetch_btn.setText(self._fetch_label())

    def _normalized_prefix(self) -> str:
        p = (self.prefix_in.text().strip() or "/api")
        return p if p.startswith("/") else "/" + p

    def abort_request(self):
        if self._inflight:
            self._log("■ Abort requested by user.", "warning")
            self._inflight.abort()
    def detect_prefix(self):
        """Try /config, /__config, /_meta for {'static_url_path' or 'api_prefix'}."""
        base = self.base_combo.currentText().strip().rstrip("/")
        if not base:
            QMessageBox.warning(self, "Invalid base URL", "Provide a base URL first.")
            return
        candidates = [f"{base}/config", f"{base}/__config", f"{base}/_meta"]
        self._log(f"→ Detecting prefix from {candidates}")

        # simple chain: issue the first; on finish try next if not found
        self._detect_chain = list(candidates)  # keep state
        self._detect_try_next()
    # ── data helpers ─────────────────────────────────────────────────────
    def _collect_table_data(self, table: QTableWidget) -> dict:
        data = {}
        for r in range(table.rowCount()):
            key_item = table.item(r, 0)
            if not key_item or not key_item.text().strip():
                continue
            val_item = table.item(r, 1)
            data[key_item.text().strip()] = val_item.text().strip() if val_item else ""
        return data

    def _fetch_label(self) -> str:
        p = (self.prefix_in.text().strip() or "/api")
        if not p.startswith("/"):
            p = "/" + p
        return f"Fetch {p}/endpoints"


    def _collect_headers(self) -> dict:
        headers = {}
        for r in range(self.headers_table.rowCount()):
            chk = self.headers_table.item(r, 0)
            if not chk or chk.checkState() != Qt.CheckState.Checked:
                continue
            key_item = self.headers_table.item(r, 1)
            val_item = self.headers_table.item(r, 2)
            if key_item and key_item.text().strip():
                headers[key_item.text().strip()] = val_item.text().strip() if val_item else ""
        return headers

    # ── table row grow helpers ───────────────────────────────────────────
    def _maybe_add_header_row(self, row: int, _col: int):
        last = self.headers_table.rowCount() - 1
        if row != last:
            return
        key_item = self.headers_table.item(row, 1)
        val_item = self.headers_table.item(row, 2)
        if (key_item and key_item.text().strip()) or (val_item and val_item.text().strip()):
            self.headers_table.blockSignals(True)
            self.headers_table.insertRow(last + 1)
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk.setCheckState(Qt.CheckState.Unchecked)
            self.headers_table.setItem(last + 1, 0, chk)
            self.headers_table.setItem(last + 1, 1, QTableWidgetItem(""))
            self.headers_table.setItem(last + 1, 2, QTableWidgetItem(""))
            self.headers_table.blockSignals(False)

    def _maybe_add_body_row(self, row: int, _col: int):
        last = self.body_table.rowCount() - 1
        key_item = self.body_table.item(row, 0)
        val_item = self.body_table.item(row, 1)
        if row == last and ((key_item and key_item.text().strip()) or (val_item and val_item.text().strip())):
            self.body_table.blockSignals(True)
            self.body_table.insertRow(last + 1)
            self.body_table.setItem(last + 1, 0, QTableWidgetItem(""))
            self.body_table.setItem(last + 1, 1, QTableWidgetItem(""))
            self.body_table.blockSignals(False)

    # ── logging ──────────────────────────────────────────────────────────
    def _setup_logging(self):
        layout = logging.getLogger()
        layout.setLevel(logging.DEBUG)
        # drop duplicate handlers if rerun in same process
        for h in list(layout.handlers):
            if isinstance(h, QTextEditLogger):
                layout.removeHandler(h)
        handler = QTextEditLogger(self.log_output)
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%H:%M:%S'))
        layout.addHandler(handler)

    # ── network actions (sync via abstract_apis) ─────────────────────────
    def fetch_remote_endpoints(self):
        base = self.base_combo.currentText().rstrip('/')
        url = f"{base}/api/endpoints"
        self.log_output.clear()
        logging.info(f"Fetching remote endpoints from {url}")
        try:
            data = getRequest(url=url)
            if isinstance(data, list):
                self._populate_endpoints(data)
                logging.info("✔ Remote endpoints loaded")
            else:
                logging.warning("/api/endpoints returned non-list, ignoring")
        except Exception as e:
            logging.error(f"Failed to fetch endpoints: {e}")
            QMessageBox.warning(self, "Fetch Error", str(e))
    # ------------------------------------------------------------- actions ----
    def fetch_endpoints(self):
        """GET {base}{prefix}/endpoints -> list[[path, methods], ...]"""
        try:
            url = self._build_url("/endpoints")
        except Exception as e:
            QMessageBox.warning(self, "Invalid URL", str(e))
            return

        req = QNetworkRequest(QUrl(url))
        self._log(f"→ GET {url}")
        reply = self._nam.get(req)
        self._bind_common(reply, f"GET {url}")

        # Also populate table when finished (if parseable)
        def after():
            if reply.error() != QNetworkReply.NetworkError.NoError:
                return
            raw = bytes(reply.readAll())
            try:
                data = json.loads(raw.decode(errors="replace"))
            except Exception:
                return
            if isinstance(data, list):
                self._populate_endpoints(data)

        reply.finished.connect(after)
    def _populate_endpoints(self, lst):
        self.endpoints_table.clearContents()
        self.endpoints_table.setRowCount(len(lst))
        for i, item in enumerate(lst):
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                path, methods = item[0], item[1]
            elif isinstance(item, dict):
                path, methods = item.get("path", ""), item.get("methods", "")
            else:
                path, methods = str(item), ""
            self.endpoints_table.setItem(i, 0, QTableWidgetItem(path))
            self.endpoints_table.setItem(i, 1, QTableWidgetItem(methods))

    def on_endpoint_selected(self, row: int, _col: int):
        ep = self.endpoints_table.item(row, 0).text()
        cfg = self.config_cache.get(ep, {})
        # restore method
        if 'method' in cfg:
            self.method_box.setCurrentText(cfg['method'])
        # restore headers
        for r in range(self.headers_table.rowCount()):
            chk = self.headers_table.item(r, 0)
            key_item = self.headers_table.item(r, 1)
            if not chk or not key_item:
                continue
            k = key_item.text()
            if k in cfg.get('headers', {}):
                chk.setCheckState(Qt.CheckState.Checked)
                self.headers_table.setItem(r, 2, QTableWidgetItem(cfg['headers'][k]))
            else:
                chk.setCheckState(Qt.CheckState.Unchecked)
        # restore params
        self.body_table.blockSignals(True)
        self.body_table.setRowCount(0)
        for k, v in cfg.get('params', {}).items():
            idx = self.body_table.rowCount()
            self.body_table.insertRow(idx)
            self.body_table.setItem(idx, 0, QTableWidgetItem(k))
            self.body_table.setItem(idx, 1, QTableWidgetItem(v))
        # ensure one blank editable row
        idx = self.body_table.rowCount()
        self.body_table.insertRow(idx)
        self.body_table.setItem(idx, 0, QTableWidgetItem(""))
        self.body_table.setItem(idx, 1, QTableWidgetItem(""))
        self.body_table.blockSignals(False)

    def send_request(self):
        sel = self.endpoints_table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.warning(self, "No endpoint", "Please select an endpoint.")
            return
        ep = self.endpoints_table.item(sel[0].row(), 0).text()
        base = self.base_combo.currentText().rstrip('/')
        url = base + ep
        method = self.method_box.currentText().upper()
        headers = self._collect_headers()
        params = self._collect_table_data(self.body_table)

        # cache per-endpoint config
        self.config_cache[ep] = {'headers': headers, 'params': params, 'method': method}

        logging.info(f"➡ {method} {url} | headers={headers} | params={params}")
        self.response_output.clear()

        try:
            if method == "GET":
                res = getRequest(url=url, headers=headers, data=params)
            elif method in ("POST", "PUT", "PATCH", "DELETE", "OPTIONS"):
                # abstract_apis exposes postRequest; use it for non-GET
                res = postRequest(url=url, headers=headers, data=params)
            else:
                raise ValueError(f"Unsupported method: {method}")

            txt = json.dumps(res, indent=4) if isinstance(res, (dict, list)) else str(res)
            self.response_output.setPlainText(txt)
            logging.info("✔ Response displayed")
        except Exception as ex:
            err = f"✖ Error: {ex}"
            self.response_output.setPlainText(err)
            logging.error(err)


def run_abstract_api_gui():
    app = QApplication(sys.argv)
    win = APIConsole()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_abstract_api_gui()
