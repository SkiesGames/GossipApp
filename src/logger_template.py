import os
import json
import logging
import pathlib
import inspect
import re
from logging.handlers import RotatingFileHandler
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def __init__(self, include_emojis=True):
        super().__init__(datefmt="%Y-%m-%d %H:%M:%S")
        self.include_emojis = include_emojis

    def format(self, record: logging.LogRecord) -> str:
        # Determine the caller module, skipping logging-related frames
        caller_module = "unknown"
        stack = inspect.stack()
        # Start from index 3 to skip:
        # stack[0]: this format method
        # stack[1]: emit method in CustomRotatingFileHandler
        # stack[2]: logging module or global_logger
        for frame_info in stack[3:]:
            module_name = frame_info.frame.f_globals.get("__name__", "unknown")
            # Skip frames from logging or global_logger
            if not module_name.startswith(
                ("logging", "src.LoggingInteractions.global_logger")
            ):
                caller_module = module_name
                break

        # Get the message and ensure it's a string
        message = record.getMessage()
        if not isinstance(message, str):
            message = str(message)

        # Handle emoji filtering
        if not self.include_emojis:
            # Remove emojis using regex pattern for Unicode emoji characters
            message = re.sub(r'[^\w\s\-_.,!?;:()[\]{}"\']', "", message)
            # Clean up extra spaces
            message = re.sub(r"\s+", " ", message).strip()

        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "caller": caller_module,
        }

        # Mask sensitive data
        if "secrets" in message.lower():
            log_data["message"] = "[REDACTED]"

        return json.dumps(log_data, ensure_ascii=False)


class EmojiFilter(logging.Filter):
    """Filter to remove emojis from log messages"""

    def filter(self, record):
        if hasattr(record, "msg") and isinstance(record.msg, str):
            # Remove emojis using regex pattern for Unicode emoji characters
            record.msg = re.sub(r'[^\w\s\-_.,!?;:()[\]{}"\']', "", record.msg)
            # Clean up extra spaces
            record.msg = re.sub(r"\s+", " ", record.msg).strip()
        return True


class CustomRotatingFileHandler(RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_first_log = True  # Flag for tracking the first log of a session

    def emit(self, record: logging.LogRecord):
        """
        Overrides emit to add empty lines for messages longer than n characters
        and a session separator for the first log of a new session.
        """
        try:
            msg = self.format(record)
            is_long_message = len(msg) > 300
            with self.lock:
                # Add session separator for the first log of a new session
                if self.is_first_log:
                    separator = f"\n\n\n===== NEW APP SESSION STARTED {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====\n\n\n"
                    self.stream.write(separator)
                    self.is_first_log = False  # Disable flag after first log
                if is_long_message:
                    self.stream.write("\n")  # Empty line before
                self.stream.write(msg + "\n")
                if is_long_message:
                    self.stream.write("\n")  # Empty line after
                self.flush()
        except Exception:
            self.handleError(record)


def initialize_logger(
    logger_name: str, debug_mode: bool, include_emojis: bool = True
) -> logging.Logger:
    """
    Initializes a logger with a JSON-handler for a file and a minimalistic console output.

    Parameters
    ----------
    logger_name : str
        Logger name, usually the module name.
    debug_mode : bool
        If True, sets logging level to DEBUG; otherwise, INFO.
    include_emojis : bool
        If True, emojis are included in log messages. If False, emojis are filtered out.

    Returns
    -------
    logging.Logger
        A logger for writing messages of different levels to the console and file.
    """
    path = pathlib.Path(os.path.join(os.getcwd(), "logs"))
    path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(logger_name)
    if logger.handlers:  # Prevent duplicate handlers
        return logger

    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

    # Console handler (level DEBUG or INFO based on debug_mode, minimalistic)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if debug_mode else logging.INFO)

    # Console formatter with emoji support
    if include_emojis:
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    else:
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        ch.addFilter(EmojiFilter())

    ch.setFormatter(console_formatter)
    logger.addHandler(ch)

    # JSON handler for file with custom formatting
    json_log_filename = f'logs/{datetime.now().strftime("%m-%d")}_{logger_name}.log'
    json_fh = CustomRotatingFileHandler(
        filename=json_log_filename,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    json_fh.setLevel(logging.DEBUG)
    json_formatter = JsonFormatter(include_emojis=include_emojis)
    json_fh.setFormatter(json_formatter)
    logger.addHandler(json_fh)

    return logger


def create_emoji_free_logger(logger_name: str, debug_mode: bool) -> logging.Logger:
    """
    Creates a logger specifically for environments where emojis should be filtered out
    (e.g., production systems, log aggregation pipelines).

    Parameters
    ----------
    logger_name : str
        Logger name, usually the module name.
    debug_mode : bool
        If True, sets logging level to DEBUG; otherwise, INFO.

    Returns
    -------
    logging.Logger
        A logger with emojis filtered out from all messages.
    """
    return initialize_logger(logger_name, debug_mode, include_emojis=False)
