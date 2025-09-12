from .imports import QObject,pyqtSignal
from .initFuncs import initFuncs
from ..imports import getRequest,postRequest,json

class RequestWorker(QObject):
    success = pyqtSignal(str)
    failure = pyqtSignal(str)

    def __init__(self, method: str, url: str, headers: dict, params: dict, timeout: float = 15.0):
        super().__init__()
        self.method  = method
        self.url     = url
        self.headers = headers or {}
        self.params  = params or {}
        self.timeout = timeout
    def run(self):
        try:
            # Try to pass timeout; if your helpers don't accept it, fallback.
            try:
                if self.method == "GET":
                    res = getRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
                else:
                    res = postRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
            except TypeError:
                if self.method == "GET":
                    res = getRequest(url=self.url, headers=self.headers, data=self.params)
                else:
                    res = postRequest(url=self.url, headers=self.headers, data=self.params)

            txt = json.dumps(res, indent=4) if isinstance(res, (dict, list)) else str(res)
            self.success.emit(txt)
        except Exception as ex:
            self.failure.emit(f"✖ Error: {ex}")


