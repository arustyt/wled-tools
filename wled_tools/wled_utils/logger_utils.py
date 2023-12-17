import logging
import logging.handlers
import sys

DEFAULT_LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(threadName)s] [%(filename)s.%(funcName)s] - %(message)s'
DEFAULT_LOG_DIR = "/apps_data_01/logs"

STDOUT = "stdout"

global init_count


# init_logger() allows that log_name can be __file__ from the calling module.  As a result, any preceding
# directories will be stripped from the log_name.  If the resulting base name has a '.py' extension it will be
# removed to get the base name of the log file, to which '.log' will be appended.  If the base name has a '.log'
# extension it will be used as-is as the log file name.  Otherwise, '.log' will be appended the base name to get the
# log file name.
def init_logger(log_name: str = STDOUT, log_dir: str = DEFAULT_LOG_DIR, level=logging.INFO,
                log_format=DEFAULT_LOG_FORMAT):
    global init_count
    if log_name == STDOUT:
        log_to_stdout(level, log_format)
    else:
        log_to_file(log_name, log_dir, level, log_format)

    get_logger().info("Exit #{count} init_logger({log_name}, {log_dir}, {level}, {log_format})".format(count=init_count,
                                                                                                       log_name=log_name,
                                                                                                       log_dir=log_dir,
                                                                                                       level=level,
                                                                                                       log_format=log_format))


def log_to_file(log_name, log_dir, level, log_format):
    if log_dir.endswith('/'):
        log_file = log_dir
    else:
        log_file = log_dir + '/'
    script_name_parts = log_name.split('/')
    file_name = script_name_parts[len(script_name_parts) - 1]
    if file_name.endswith('.py'):
        log_file += file_name[0:-3] + '.log'
    elif file_name.endswith('.log'):
        log_file += file_name
    else:
        log_file += file_name + '.log'
    handler = logging.handlers.TimedRotatingFileHandler(log_file, when='D')
    handler.setFormatter(logging.Formatter(log_format))
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)


def log_to_stdout(level, log_format):
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    root.addHandler(handler)


def get_logger():
    return logging.getLogger()
