import pytest
import logging
from optilogger import  init_log, OptiLogger
from database import TestStatus, TestResults, Dut, DummyRxAccuracy
from datetime import datetime
from sqlalchemy import insert

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

        TestResults.DutSN = self.dut
        TestResults.PartNum = self.pn
        TestResults.StartTime = datetime.now()
        TestResults.EndTime = datetime.now()
        TestResults.TestName = self.__name__
        TestResults.Comments = 'Test Started'
        TestResults.ConfigFile = self.__name__+".yaml"
        TestResults.TestScript = self.__name__+".py"
        TestResults.PassFail = "In Progress"
        TestResults.ResultsCsvFile = None
        TestResults.ResultsHtmlFile = None
        self.db_client.execute(insert(TestResults), [{}])


    def execute_example(self):
        hp81635a()
        print(self.station)

    def record_results(self, test_table_name, **data):
        """
        db_record: <should have database name, table name
        data: {column1: <data> column2: <data> column3: <data>
        Logic:
        1. Update the test results table
        2. Update test name table with data.
            Data is key:value pair (where key is column name, data is value (list))

        """
        insert_result_record = "INSERT INTO TestResults <>"

        #TestResults.TestName
        pass


    def clean_up_resources(self):
        pass

    def upload_logs(self):
        pass

    def setup_resources(self):
        pass
