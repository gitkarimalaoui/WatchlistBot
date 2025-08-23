from time import perf_counter
import logging
import json

log = logging.getLogger("perf")

class step:
    def __init__(self, name: str):
        self.name = name
        self.t0 = 0.0

    def __enter__(self):
        self.t0 = perf_counter()

    def __exit__(self, *_):
        log.info(json.dumps({"step": self.name, "sec": round(perf_counter() - self.t0, 3)}))
