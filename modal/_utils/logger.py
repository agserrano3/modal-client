# Copyright Modal Labs 2022
import logging
import os


log_level = os.environ.get("MODAL_LOGLEVEL", "WARNING")
log_format = os.environ.get("MODAL_LOG_FORMAT", "STRING")

logger = logging.getLogger("modal-utils")
configure_logger(logger, log_level, log_format)
