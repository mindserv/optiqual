import logging
import sys
import os
import time
from sys import version_info

OPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LOG_DIR = os.path.join(OPT_DIR, "test_logs")
DEFAULT_LOG_FILE_NAME_PREFIX = "MINDSERV-OPTIQUAL-"
TXT_LOGNAME_FORMAT: str = "{}.{}.log"
HTML_LOGNAME_FORMAT: str = "{}.{}.html"
CSV_LOGNAME_FORMAT: str = "{}.{}.csv"


class OptiLogger(object):

    def __init__(self, log_dir: object = DEFAULT_LOG_DIR, log_file_name_suffix: object = DEFAULT_LOG_FILE_NAME_PREFIX) -> object:

        self.test_status = None
        self.timing_failed = None
        self.last_flush = time.time()
        self.flush_timer = 300  # in seconds

        _create_logging_dir(log_dir)

        # self.fileName = scriptName + '_'+timeStamp
        timefmt = time.strftime("%Y-%m-%d-%H-%M-%S")

        text_log_file = os.path.join(log_dir, TXT_LOGNAME_FORMAT.format(log_file_name_suffix, timefmt))
        csv_log_file = os.path.join(log_dir, CSV_LOGNAME_FORMAT.format(log_file_name_suffix, timefmt))
        html_log_file = os.path.join(log_dir, HTML_LOGNAME_FORMAT.format(log_file_name_suffix, timefmt))

        self.text_fd = open(text_log_file, 'w')
        self.html_fd = open(html_log_file, 'w')
        self.csv_fd = open(csv_log_file, 'w')
        self.add_log_header()

    def add_log_header(self):
        self.text_fd.write("%s\n" % (sys.argv))
        self.text_fd.write(f'Logging start time {time.ctime()}')

        self.csv_fd.write(f'{sys.argv}')
        self.csv_fd.write(f'Logging start time {time.ctime()}')

        self.html_fd.write("<html>\n")
        self.html_fd.write("<head>\n")

        self.html_fd.write("<style type=\"text/css\">\n")

        self.html_fd.write("body {background: white; color: black;\n")
        self.html_fd.write("margin: .25in; border: 0; padding: 0;\n")
        self.html_fd.write("font:13px/1.45 sans-serif;}\n")

        self.html_fd.write("p {\n")
        self.html_fd.write("margin: 0;\n")
        self.html_fd.write("padding: 0;\n")
        self.html_fd.write("margin-left: .5in;\n")
        self.html_fd.write("font-family: monospace;\n")
        self.html_fd.write("}\n")

        self.html_fd.write("span.passed {\n")
        self.html_fd.write("color: green;\n")
        self.html_fd.write("font-weight: bold;\n")
        self.html_fd.write("}\n")

        self.html_fd.write("span.failed {\n")
        self.html_fd.write("color: red;\n")
        self.html_fd.write("font-weight: bold;\n")
        self.html_fd.write("}\n")

        self.html_fd.write("span.warning {\n")
        self.html_fd.write("color: yellow;\n")
        self.html_fd.write("font-weight: bold;\n")
        self.html_fd.write("}\n")

        self.html_fd.write("span.incomplete {\n")
        self.html_fd.write("color: yellow;\n")
        self.html_fd.write("font-weight: bold;\n")
        self.html_fd.write("}\n")

        self.html_fd.write("</style>\n")
        self.html_fd.write("</head>\n")
        self.html_fd.write("<body>\n")
        self.html_fd.write("<p>%s</p>\n" % (sys.argv))
        self.html_fd.write("<p>logging start time %s</p>\n" %
                           (time.ctime()))

    def close_log_files(self):

        self.text_fd.flush()
        self.text_fd.close()

        self.csv_fd.flush()
        self.csv_fd.close()

        self.html_fd.flush()
        self.html_fd.close()

    def flush_logs(self):

        if ((time.time() - self.last_flush) >= self.flush_timer):

            self.text_fd.flush()
            self.html_fd.flush()
            self.csv_fd.flush()
            self.last_flush = time.time()

    def log_csv(self, s):
        print(s)
        self.csv_fd.write("%s\n" % (s))

        if time.time() - self.last_flush > self.flush_timer:
            self.flush_logs()
            self.last_flush = time.time()

        self.flush_logs()

    def info(self, s):
        print(s)
        self.text_fd.write("%s\n" % (s))

        # if (self.hasCsv):
        #    self.csv_fd.write("%s\n" % (s))

        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        self.html_fd.write("<p>%s</p>\n" % (s))

        self.flush_logs()

    def diagnostic(self, s):
        print('\033[93m' + "%s" % (s) + '\033[0m')
        self.text_fd.write("%s\n" % (s))

        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        self.html_fd.write("<p>%s</p>\n" % (s))

        self.flush_logs()

    def error(self, s):
        print('\033[91m' + "Error - %s" % (s) + '\033[0m')

        self.text_fd.write("Error - %s\n" % (s))

        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        self.html_fd.write(
            '<p><span class="error">ERROR</span>:%s</p>\n' % (s))

        self.flush_logs()

    def passed(self, s):
        print('\033[92m' + "Passed - %s" % (s) + '\033[0m')

        if self.test_status.find('fail') == -1:
            self.test_status = 'passed'

        self.text_fd.write("Passed - %s\n" % (s))

        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        self.html_fd.write(
            '<p><span class="passed">PASSED</span>:%s</p>\n' % (s))

        self.flush_logs()

    def failed(self, s, type=None):

        if (type == 'timing'):
            fail_header = 'Failed Timing'
            # If already 'failed', keep
            # test_status as 'failed'. Timing
            # fail is a special case of FAIL

            if (self.test_status != 'failed'):
                self.test_status = 'failed_timing'

        else:
            self.test_status = 'failed'
            fail_header = 'Failed'

        print('\033[91m' + "%s - %s" % (fail_header, s) + '\033[0m')

        self.text_fd.write("%s - %s\n" % (fail_header, s))

        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        self.html_fd.write(
            '<p><span class="failed">%s</span>:%s</p>\n' % (fail_header, s))

        self.flush_logs()

    def failed_timing(self, s):
        if (self.test_status != 'failed'):
            self.test_status = 'failed_timing'

        self.timing_failed = True

        print("Failed Timing - %s" % (s))

        self.text_fd.write("Failed Timing - %s\n" % (s))

        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        self.html_fd.write(
            '<p><span class="failed">FAILED Timing</span>:%s</p>\n' % (s))

        self.flush_logs()

    def warning(self, s):
        print('\033[35m' + "Warning - %s" % (s) + '\033[0m')

        self.text_fd.write("Warning - %s\n" % (s))

        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        self.html_fd.write(
            '<p><span class="warning">WARNING</span>:%s</p>\n' % (s))

        self.flush_logs()

    def incomplete(self, s):
        print(s)

        self.text_fd.write("Incomplete - %s\n" % (s))

        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        self.html_fd.write(
            '<p><span class="incomplete">INCOMPLETE</span>:%s</p>\n' % (s))

        self.flush_logs()

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


if __name__ == '__main__':
    log = OptiLogger("/tmp/kk", "kathir")
    log.info("Custom")
    log.incomplete("Custom")
    log.error("Custom")
    log.warning("Custom")
    log.failed("Custom")
