import logging
import os
import sys

LOG_FORMAT = "%(asctime)s [%(levelname)s] (%(name)s): %(message)s"

handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

log_file = os.getenv("TEACHLAB_LOG_FILE")
if log_file:
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=handlers,
)

logger = logging.getLogger("TeachLab")
