#!/usr/bin/env python3
# live_editor.py — Qt Live Editor/Creator (PyQt6)

from __future__ import annotations
from typing import Any, List, Dict, Optional, Tuple, Type
import inspect
import sys

from PyQt6 import QtCore, QtWidgets

# ---------- Utilities: ensure app ----------
def ensure_app():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv[:1])
    return app

# ---------- Safe instance creation for introspection / demo ----------
_CONSTRUCTOR_TRIES: Tuple[Tuple[Tuple, dict], ...] = (
    ((), {}),
    ((None,), {}),  # many widgets accept parent=None
    ((QtCore.Qt.Orientation.Horizontal,), {}),
    ((QtCore.Qt.Orientation.Vertical,), {}),
)

def new_instance(cls: Type) -> Optional[object]:
    for args, kwargs in _CONSTRUCTOR_TRIES:
        try:
            return cls(*args, **kwargs)
        except Exception:
            continue
    return None

# ---------- Signal auto-discovery (derived registry) ----------
INTERESTING_SUFFIXES = (
    "Changed", "Pressed", "Clicked", "Toggled",
    "Activated", "Released", "Finished", "Moved",
    "Triggered",
)

PRIORITY_ORDER = [
    "textChanged", "currentTextChanged", "valueChanged", "stateChanged",
    "currentIndexChanged", "editingFinished", "returnPressed",
    "clicked", "toggled", "activated", "triggered", "pressed", "released",
    "sliderMoved", "dateChanged", "timeChanged", "dateTimeChanged",
]
PRIO_INDEX = {n: i for i, n in enumerate(PRIORITY_ORDER)}

def _rank(names: List[str]) -> List[str]:
    dedup = list(dict.fromkeys(names))
    dedup.sort(key=lambda n: PRIO_INDEX.get(n, len(PRIORITY_ORDER)))
    return dedup

@QtCore.pyqtSlot(object, result=list)
def discover_signal_names(obj: object) -> List[str]:
    names: List[str] = []

    # A) Meta-object (reliable)
    try:
        mo = obj.metaObject()
        for i in range(mo.methodCount()):
            m = mo.method(i)
            # PyQt6: QMetaMethod.MethodType.Signal
            if m.methodType() == QtCore.QMetaMethod.MethodType.Signal:
                n = bytes(m.name()).decode("utf-8")
                if n.endswith(INTERESTING_SUFFIXES):
                    names.append(n)
    except Exception:
        pass

    # B) Python attribute scan (PyQt bound signals)
    pyqt_bound = getattr(QtCore, "pyqtBoundSignal", None)
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            attr = getattr(obj, name)
        except Exception:
            continue
        is_signal = (
            (pyqt_bound and isinstance(attr, pyqt_bound)) or
            (hasattr(attr, "connect") and hasattr(attr, "disconnect"))
        )
        if is_signal and name.endswith(INTERESTING_SUFFIXES):
            names.append(name)

    return _rank(names)

# ---------- Attribute helpers ----------
SIMPLE_TYPES = (int, float, str, bool)

def read_simple_attrs(obj: object) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for name in dir(obj):
        if name.startswith("_"):
            continue
        # Exclude callables and Qt internals
        try:
            val = getattr(obj, name)
        except Exception:
            continue
        if callable(val):
            continue
        # Only show simple values (editable)
        if isinstance(val, SIMPLE_TYPES):
            out[name] = val
    return out

def coerce_value(text: str, current: Any) -> Any:
    if isinstance(current, bool):
        return text.lower() in ("1", "true", "yes", "on")
    if isinstance(current, int):
        return int(text)
    if isinstance(current, float):
        return float(text)
    return text  # str or fallback

# ---------- The main window ----------
class LiveEditor(QtWidgets.QMainWindow):
    def __init__(self, module=QtWidgets):
        super().__init__()
        self.setWindowTitle("Qt Live Editor / Creator")
        self.resize(1100, 720)

        # State
        self.module = module
        self.current_class: Optional[Type] = None
        self.current_obj: Optional[object] = None

        # UI
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        self.setCentralWidget(splitter)

        # Left: module/class browser
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        self.search_in = QtWidgets.QLineEdit()
        self.search_in.setPlaceholderText("Filter classes…")
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type"])
        self.tree.setUniformRowHeights(True)
        left_layout.addWidget(self.search_in)
        left_layout.addWidget(self.tree)

        # Right: inspector panel
        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)

        # Instance controls
        inst_box = QtWidgets.QGroupBox("Instance")
        inst_layout = QtWidgets.QHBoxLayout(inst_box)
        self.btn_create = QtWidgets.QPushButton("Create")
        self.btn_destroy = QtWidgets.QPushButton("Destroy")
        self.signal_list = QtWidgets.QListWidget()
        self.signal_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.btn_autowire = QtWidgets.QPushButton("Auto-connect selected signals")
        inst_layout.addWidget(self.btn_create)
        inst_layout.addWidget(self.btn_destroy)
        inst_layout.addWidget(QtWidgets.QLabel("Signals:"))
        inst_layout.addWidget(self.signal_list, 1)
        inst_layout.addWidget(self.btn_autowire)

        # Attribute editor
        attr_box = QtWidgets.QGroupBox("Attributes (simple types)")
        attr_layout = QtWidgets.QVBoxLayout(attr_box)
        self.attr_table = QtWidgets.QTableWidget(0, 2)
        self.attr_table.setHorizontalHeaderLabels(["Name", "Value"])
        self.attr_table.horizontalHeader().setStretchLastSection(True)
        self.attr_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked |
                                        QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed |
                                        QtWidgets.QAbstractItemView.EditTrigger.AnyKeyPressed)
        attr_layout.addWidget(self.attr_table)

        right_layout.addWidget(inst_box)
        right_layout.addWidget(attr_box, 1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 1)

        # Signals
        self.search_in.textChanged.connect(self._filter_tree)
        self.tree.itemSelectionChanged.connect(self._on_tree_select)
        self.btn_create.clicked.connect(self._create_instance)
        self.btn_destroy.clicked.connect(self._destroy_instance)
        self.btn_autowire.clicked.connect(self._auto_wire_selected)
        self.attr_table.itemChanged.connect(self._on_attr_changed)

        # Populate
        self._fill_tree()

    # ----- Populate class browser -----
    def _fill_tree(self):
        self.tree.clear()
        module_item = QtWidgets.QTreeWidgetItem([self.module.__name__, "module"])
        self.tree.addTopLevelItem(module_item)

        names = [n for n in dir(self.module)]
        names.sort()
        for name in names:
            obj = getattr(self.module, name, None)
            if not inspect.isclass(obj):
                continue
            # Keep QObject subclasses only; comment this to see all
            if not issubclass(obj, QtCore.QObject):
                continue
            item = QtWidgets.QTreeWidgetItem([name, "class"])
            item.setData(0, QtCore.Qt.ItemDataRole.UserRole, obj)
            module_item.addChild(item)

        self.tree.expandItem(module_item)

    def _filter_tree(self, text: str):
        it = QtWidgets.QTreeWidgetItemIterator(self.tree)
        t = text.lower()
        while it.value():
            item = it.value()
            if item.parent():  # class items
                visible = (t in item.text(0).lower())
                item.setHidden(not visible)
            it += 1

    # ----- Selection handler -----
    def _on_tree_select(self):
        items = self.tree.selectedItems()
        self.current_class = None
        if not items:
            return
        item = items[0]
        obj = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if inspect.isclass(obj):
            self.current_class = obj
        self._refresh_instance_ui()

    # ----- Instance lifecycle -----
    def _create_instance(self):
        if not self.current_class:
            return
        inst = new_instance(self.current_class)
        if inst is None:
            QtWidgets.QMessageBox.warning(self, "Cannot Instantiate",
                                          f"Could not create {self.current_class.__name__} with simple defaults.")
            return
        self.current_obj = inst
        self._refresh_instance_ui()

    def _destroy_instance(self):
        self.current_obj = None
        self._refresh_instance_ui()

    # ----- UI refresh -----
    def _refresh_instance_ui(self):
        # signals list
        self.signal_list.clear()
        if self.current_obj:
            sigs = discover_signal_names(self.current_obj)
            for s in sigs:
                self.signal_list.addItem(s)

        # attributes table
        self.attr_table.blockSignals(True)
        self.attr_table.setRowCount(0)
        if self.current_obj:
            attrs = read_simple_attrs(self.current_obj)
            for i, (k, v) in enumerate(sorted(attrs.items())):
                self.attr_table.insertRow(i)
                self.attr_table.setItem(i, 0, QtWidgets.QTableWidgetItem(k))
                self.attr_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(v)))
        self.attr_table.blockSignals(False)

    # ----- Attribute editing -----
    def _on_attr_changed(self, item: QtWidgets.QTableWidgetItem):
        if not self.current_obj or item.column() != 1:
            return
        name = self.attr_table.item(item.row(), 0).text()
        try:
            current = getattr(self.current_obj, name)
        except Exception:
            return
        try:
            new_val = coerce_value(item.text(), current)
            setattr(self.current_obj, name, new_val)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Set attribute failed", f"{e}")

    # ----- Auto-wire signals -----
    def _auto_wire_selected(self):
        if not self.current_obj:
            return
        selected = [it.text() for it in self.signal_list.selectedItems()]
        if not selected:
            selected = [self.signal_list.item(i).text() for i in range(self.signal_list.count())]

        connected = []
        for sig_name in selected:
            sig = getattr(self.current_obj, sig_name, None)
            if sig is None:
                continue
            # Generic debug slot: prints signal emission
            def make_slot(name):
                def _slot(*args, **kwargs):
                    print(f"[SIGNAL] {name} args={args} kwargs={kwargs}")
                return _slot
            try:
                sig.connect(make_slot(sig_name))
                connected.append(sig_name)
            except Exception:
                pass

        if connected:
            QtWidgets.QMessageBox.information(self, "Connected",
                f"Wired: {', '.join(connected)}\nTry interacting with the instance; check stdout.")

# ---------- main ----------
if __name__ == "__main__":
    ensure_app()
    w = LiveEditor(module=QtWidgets)
    w.show()
    sys.exit(QtWidgets.QApplication.instance().exec())
