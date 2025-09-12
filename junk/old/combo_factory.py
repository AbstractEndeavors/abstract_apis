# combo_factory.py
from typing import Iterable, Tuple, Any, Optional, List
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QComboBox, QWidget  # or PyQt6
from PyQt5.QtWidgets import QSizePolicy
# If you’re using the auto-signal code from earlier:
from .auto_signals import connect_signals  # <- from previous message

def _resolve_insert_policy(policy: Optional[str | int]) -> int:
    """
    Accepts: None | 'NoInsert' | 'Insert' | 'InsertAlphabetically' | int
    Returns the correct QComboBox.InsertPolicy enum value for PyQt5/6.
    """
    if policy is None:
        return QComboBox.InsertPolicy.NoInsert
    if isinstance(policy, int):
        return policy
    name = str(policy).strip().lower()
    mapping = {
        "noinsert": QComboBox.InsertPolicy.NoInsert,
        "insert": QComboBox.InsertPolicy.InsertAtBottom,
        "insertalphabetically": QComboBox.InsertPolicy.InsertAlphabetically,
        "insertatcurrent": QComboBox.InsertPolicy.InsertAtCurrent,
        "insertatbottom": QComboBox.InsertPolicy.InsertAtBottom,
        "insertattop": QComboBox.InsertPolicy.InsertAtTop,
        "insertaftercurrent": QComboBox.InsertPolicy.InsertAfterCurrent,
        "insertbeforecurrent": QComboBox.InsertPolicy.InsertBeforeCurrent,
    }
    return mapping.get(name, QComboBox.InsertPolicy.NoInsert)

def _safe_attr_name_from_label(label: str) -> str:
    return f"{label.strip().lower().replace(' ', '_').replace(':','')}_combo"

def _add_items(combo: QComboBox, items: Iterable[Any]) -> None:
    """
    Accepts:
      - ["http://a", "http://b"]
      - [("http://a", "/api"), ("http://b", "/v1")]
      - [{"text": "...", "data": obj}, ...]  (if you prefer dicts)
    """
    for it in items or []:
        if isinstance(it, tuple) and len(it) >= 2:
            combo.addItem(it[0], it[1])
        elif isinstance(it, dict) and "text" in it:
            combo.addItem(it["text"], it.get("data"))
        else:
            combo.addItem(str(it))

def make_combo_row(
    parent,
    layout=None,
    *,
    label: str = "Combo:",
    attr_name: Optional[str] = None,
    items: Optional[Iterable[Any]] = None,
    editable: bool = True,
    insert_policy: Optional[str | int] = "NoInsert",
    placeholder: Optional[str] = None,
    default_index: int = 0,
    on_change: Optional[List[callable] | callable] = None,
    connect_signals_subset: Optional[List[str]] = None,  # e.g. ["currentTextChanged"]
) -> QHBoxLayout:
    """
    Build 'Label: [ QComboBox ]' and attach combo to parent.

    Signals:
      - If on_change is provided, we auto-connect via connect_signals().
      - If connect_signals_subset is provided, we connect only those; else use auto discovery.
    """
    
    combo = QComboBox()


    combo.setEditable(bool(editable))
    combo.setInsertPolicy(_resolve_insert_policy(insert_policy))

    if placeholder:
        combo.setEditable(True)
        combo.setPlaceholderText(placeholder)

    _add_items(combo, items)
    if 0 <= default_index < combo.count():
        combo.setCurrentIndex(default_index)

    # Pick attribute name automatically if not provided
    if not attr_name:
        attr_name = _safe_attr_name_from_label(label)
    setattr(parent, attr_name, combo)

    # Auto-connect signals (introspection) if requested
    if on_change:
        if connect_signals_subset:
            connect_signals(combo, callbacks=on_change, signals=connect_signals_subset)
        else:
            # rely on auto discovery & ranking (usually: currentTextChanged, currentIndexChanged, activated)
            connect_signals(combo, callbacks=on_change)

    
    return combo
