try:
    from PyQt6.sip import isdeleted
except Exception:
    def isdeleted(obj):
        try:
            _ = obj.metaObject()
            return False
        except Exception:
            return True

def emit(self, record):
    # Widget might be deleted during shutdown; fail gracefully.
    if getattr(self, "widget", None) is None:
        return
    if isdeleted(self.widget):
        return
    msg = self.format(record)
    try:
        self.widget.append(msg)
        self.widget.ensureCursorVisible()
    except Exception:
        # Swallow shutdown races
        pass
