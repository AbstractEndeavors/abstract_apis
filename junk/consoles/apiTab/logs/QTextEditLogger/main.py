from __future__ import annotations
import json,logging
from typing import Optional, Dict, Tuple
from urllib.parse import urlencode

# --- Qt imports (PyQt6) -------------------------------------------------------
from PyQt6.QtCore import Qt, QUrl, QTimer, QByteArray
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QMessageBox, QMainWindow, QTableWidgetSelectionRange
)

# --- Optional: pull user’s helpers if present ---------------------------------
try:
    # Your project constants/utilities (if available)
    from abstract_utilities import get_logFile  # noqa
except Exception:  # pragma: no cover - safe fallback
    import logging
    def get_logFile(name: str):
        logger = logging.getLogger(name)
        if not logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%H:%M:%S'))
            logger.addHandler(h)
            logger.setLevel(logging.INFO)
        return logger

logger = get_logFile(__name__)
# ─── Logging Handler ──────────────────────────────────────────────────────
class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)
        self.api_prefix = "/api" # default; will update on detect or user edit
    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
        self.widget.ensureCursorVisible()


