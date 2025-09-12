from ..imports import getRequest,postRequest,json
def run(self):
    try:
        # Try to pass timeout; if your helpers don't accept it, fallback.
        try:
            if self.method == "GET":
                res = getRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
            else:
                res = postRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
        except Exception as e:
            print(f"{e}")
        if isinstance(res,dict):
            txt = json.dumps(res, indent=4) if isinstance(res, (dict, list)) else str(res)
        else:
            txt = str(res)
        
    except Exception as ex:
        self.failure.emit(f"✖ Error: {ex}")
