import logging
import csv
import os
import time

OPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LOG_DIR = os.path.join(OPT_DIR, "test_logs")
DEFAULT_LOG_FILE_NAME_PREFIX = "MINDSERV-OPTIQUAL-"
TXT_LOGNAME_FORMAT: str = "{}.{}.log"
HTML_LOGNAME_FORMAT: str = "{}.{}.html"
CSV_LOGNAME_FORMAT: str = "{}.{}.csv"


class CSVFormatter(logging.Formatter):
    def format(self, record):
        return f'{record.asctime},{record.levelname},{record.message}'


class HTMLFormatter(logging.Formatter):
    def format(self, record):
        return f'<tr><td>{record.asctime}</td><td>{record.levelname}</td><td>{record.message + '\n'}</td></tr>'


# Special handling for HTML: Add table headers
def create_html_header(html_log_file):
    with open(html_log_file, 'w') as file:
        file.write('<html><body><table border="1"><tr><th>Time</th><th>Level</th><th>Message</th></tr>')


def finalize_html(html_log_file):
    with open(html_log_file, 'a') as file:
        file.write('</table></body></html>')


class DirectoryException(Exception):
    """
    Custom exception when creating a log directory

    """

    def __init__(self, log_dir):
        self.msg = f"Failed to create directory {log_dir}"

    def __str__(self):
        return f"[{self.__class__.__name__}] {self.msg}"


def _create_logging_dir(log_dir):
    """
    :param log_dir:
    :return:
    """
    try:
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir, 0o755)
    except OSError:
        raise DirectoryException(log_dir)


def init_log(log_dir=DEFAULT_LOG_DIR, log_file_name_suffix=DEFAULT_LOG_FILE_NAME_PREFIX, log_level=logging.INFO):
    _create_logging_dir(log_dir)

    logging.basicConfig(level=log_level)
    timefmt = time.strftime("%Y-%m-%d-%H-%M-%S")

    # Create logger
    logger = logging.getLogger('MyLogger')
    logger.setLevel(log_level)

    text_log_file = os.path.join(log_dir, TXT_LOGNAME_FORMAT.format(log_file_name_suffix, timefmt))
    csv_log_file = os.path.join(log_dir, CSV_LOGNAME_FORMAT.format(log_file_name_suffix, timefmt))
    html_log_file = os.path.join(log_dir, HTML_LOGNAME_FORMAT.format(log_file_name_suffix, timefmt))

    # Create file handlers
    text_handler = logging.FileHandler(text_log_file)
    csv_handler = logging.FileHandler(csv_log_file)
    html_handler = logging.FileHandler(html_log_file)
    console_handler = logging.StreamHandler()

    # Set formatters
    text_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s')
    text_handler.setFormatter(text_formatter)

    csv_formatter = CSVFormatter('%(asctime)s - %(levelname)s - %(message)s')
    csv_handler.setFormatter(csv_formatter)

    html_formatter = HTMLFormatter('%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s')
    html_handler.setFormatter(html_formatter)

    console_handler.setFormatter(text_formatter)

    # Add handlers to logger
    logger.addHandler(text_handler)
    logger.addHandler(csv_handler)
    logger.addHandler(html_handler)
    logger.addHandler(console_handler)

    # Write headers initially
    create_html_header(html_log_file)

    # Finalize HTML after logging
    finalize_html(html_log_file)

    return logger
