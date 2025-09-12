from ..imports import *
# — UI helpers —
from abstract_apis import *
# RequestThread/functions.py
from ..imports import *
from abstract_apis import getRequest, postRequest
import json, requests
def run(self):
        try:
            if self.is_detect:
                # For API prefix detection
                candidates = [f"{self.url}/config", f"{self.url}/__config", f"{self.url}/_meta"]
                found = None
                for url in candidates:
                    try:
                        r = getRequest(url=url, headers=self.headers, timeout=self.timeout)
                        if isinstance(r, dict):
                            val = r.get("static_url_path") or r.get("api_prefix")
                            if isinstance(val, str) and val.strip():
                                found = val.strip()
                                break
                    except Exception:
                        continue
                txt = found or "/api"
                log_msg = f"API prefix detected: {txt}"
                self.response_signal.emit(txt, log_msg)
            else:
                # Normal request
                if self.method == "GET":
                    res = getRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
                else:
                    res = postRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
                txt = json.dumps(res, indent=4) if isinstance(res, (dict, list)) else str(res)
                log_msg = f"✔ {self.method} {self.url}"
                self.response_signal.emit(txt, log_msg)
        except Exception as ex:
            self.error_signal.emit(f"✖ Error: {ex}")
