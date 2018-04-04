import logging
import os
import sys
import traceback
from logging.handlers import TimedRotatingFileHandler

log = logging.getLogger("heron")


def get_logging_config(cfg_path=None):
    """
    读取logging的配置
    :param cfg_path: 配置文件路径
    """
    logging_config = {
        "log_level": None,
    }

    return logging_config


def get_log_date_format():
    return "%Y-%m-%d %H:%M:%S %Z"


def get_log_format(logger_name):
    return '%%(asctime)s | %%(levelname)s | %s | %%(name)s(%%(filename)s:%%(lineno)s) | %%(message)s' % logger_name


def initialize_logging(logger_name):
    try:
        logging_config = get_logging_config()

        logging.basicConfig(
            format=get_log_format(logger_name),
            level=logging_config.get("log_level") or logging.INFO,
        )

        log_file = logging_config.get("%s_log_file" % logger_name)
        if not log_file:
            log_file = "/data/logs/%s.log" % logger_name

        if not logging_config.get("disable_file_logging"):
            if os.access(os.path.dirname(log_file), os.R_OK | os.W_OK):
                file_handler = TimedRotatingFileHandler(log_file)

                formatter = logging.Formatter(get_log_format(logger_name), get_log_date_format())
                file_handler.setFormatter(formatter)

                root_log = logging.getLogger()
                root_log.addHandler(file_handler)
            else:
                sys.stderr.write("Log file is unwritable: '%s'\n" % log_file)

    except Exception as e:
        sys.stderr.write("Couldn't initialize logging: %s\n" % str(e))
        traceback.print_exc()

        logging.basicConfig(
            format=get_log_format(logger_name),
            level=logging.INFO,
        )

    global log
    log = logging.getLogger(__name__)