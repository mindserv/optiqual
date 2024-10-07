import pytest
import logging
from optilogger import  init_log, OptiLogger



@pytest.mark.usefixtures("station")
class BaseTest(object):
    """
    Tests written in pytest format will inherit from this base class.
    """
    def setup_class(self):
        # self.log = init_log(log_file_name_suffix=self.__name__)
        self.log = OptiLogger(log_file_name_suffix=self.__name__)
        self.log.info(f'Starting test {self.__name__}')
        #self.log.info(f'Test station {self.station}')

    def execute_example(self):
        hp81635a()
        print(self.station)

    def record_results(self):
        pass

    def clean_up_resources(self):
        pass

    def upload_logs(self):
        pass

    def setup_resources(self):
        pass
