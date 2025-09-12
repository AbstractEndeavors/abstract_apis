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
