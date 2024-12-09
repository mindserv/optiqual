import pytest
from optilogger import init_log, OptiLogger
from database import TestStatus, TestResults, Dut, DummyRxAccuracy, TestSweeps, Station, TestRxPowerSweep

from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.sql import text
import datetime

# TODO: Auto detect test table names
TEST_CLASS_TABLE_MAP = {"TestSweeps": TestSweeps, "TestResults": TestResults,
                        "Dut": Dut, "DummyRxAccuracy": DummyRxAccuracy, "Station": Station,
                        "TestRxPowerSweep": TestRxPowerSweep}


@pytest.mark.usefixtures("station", "db", "artifacts", "db_session", "sub20")
class BaseTest(object):
    """
    Tests written in pytest format will inherit from this base class.
    """

    def _record_test_results(self, dut_id, test_name, test_config, start_time, station_id):
        """
        :param dut_id: PK from DUT table
        :param test_name: Test class name
        :param start_time: Test start time
        :param station_id: PK from station table used for testing
        :param config_file: Test config file (recipe)
        :return:
        """
        insert_sql = text("INSERT INTO test_results(dut_id, test_name, start_time, station_id, config_file, "
                          "pass_fail) values ("
                          ":dut_id, :test_name, :start_time, :station_id,"
                          ":config_file, :pass_fail)")
        with self.db.connect() as conn:
            conn.execute(insert_sql, {"dut_id": dut_id, "test_name": test_name, "start_time": start_time,
                                      "station_id": station_id, "config_file": test_config,
                                      "pass_fail": TestStatus.INCOMPLETE})

            conn.commit()

            res = conn.execute(text("select id from test_results where dut_id=:dut_id and test_name=:test_name and "
                                    "start_time=:start_time and station_id=:station_id and config_file=:config_file "
                                    "and pass_fail=:pass_fail"),
                               {"dut_id": dut_id, "test_name": test_name, "start_time": start_time,
                                "station_id": station_id, "config_file": test_config,
                                "pass_fail": TestStatus.INCOMPLETE})

            self.tr_id = res.fetchone()[0]

    def _start_record_results(self, test_name, test_config, station_id):
        """

        :return:
        """
        # Create a datetime object
        now = datetime.datetime.now()

        # Format the datetime object for PostgreSQL
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        self.dut_id = None
        try:
            with self.db.connect() as conn:
                with conn.begin():
                    # TODO: dut_id should be checked
                    conn.execute(
                        text("INSERT INTO Dut (dut_sn, dut_part_num, dut_part_num_rev, date) values (:sn, "
                             ":pn, :rev, :date)"),
                        {"sn": self.artifacts.sn, "pn": self.artifacts.pn, "rev": "00", "date": formatted_datetime})

                with conn.begin():
                    res = conn.execute(text("SELECT id from Dut where dut_sn=:sn and dut_part_num=:pn and date=:date"),
                                       {"sn": self.artifacts.sn, "pn": self.artifacts.pn, "date": formatted_datetime})
                    self.dut_id = res.fetchone()[0]
        except IntegrityError as exp:
            if exp._sql_message().__contains__("duplicate key value"):

                with self.db.connect() as conn:
                    self.dut_id = conn.execute(text("SELECT id from Dut where dut_sn = :sn and dut_part_num = :pn"),
                                               {"sn": self.artifacts.sn, "pn": self.artifacts.pn}).fetchone()[0]

            else:
                raise
            self.log.info(f'SN {self.artifacts.sn} and PN {self.artifacts.pn}-00 already exists in the database')

        self.log.info("Fetching Station id")
        with self.db.connect() as conn:
            res = conn.execute(text("select id from station where station_name=:station_name"),
                               {"station_name": self.station.name})
            self.station_id = res.fetchone()[0]
        self._record_test_results(self.dut_id, test_name, test_config, formatted_datetime, station_id)

    def setup(self, test_name, test_config):
        #self.log = init_log(log_file_name_suffix=test_name)
        self.log = OptiLogger(log_file_name_suffix=test_name)
        self.log.info(f'Starting test {test_name}')
        self.log.info(f'Test station {self.station}')
        # Insert entry if the SN and PN is missing
        # Find the test station id from self.station
        self._start_record_results(test_name, test_config, 1)
        # Insert entry into the TestResults table.

    def execute_example(self):
        hp81635a()
        print(self.station)

    def record_results(self, test_table_name, result_data, test_status):
        """
        db_record: <should have database name, table name
        data: {column1: <data> column2: <data> column3: <data>
        Logic:
        1. Update the test results table
        2. Update test name table with data.
            Data is key:value pair (where key is column name, data is value (list))
            :param result_data:
            :param test_table_name:
            :param data:

        """

        print(test_table_name)

        print(result_data)
        # TODO: validate the list size fo each key is the same.
        # TODO: Also validate the key is same as column in the table.
        # Step 1: Determine the maximum length of the lists
        max_length = max(len(lst) for lst in result_data.values())

        # Step 2: Create a list of dictionaries
        mapped_data = []
        for i in range(max_length):
            entry = {}
            for key in result_data:
                if i < len(result_data[key]):
                    entry[key] = result_data[key][i]
                else:
                    entry[key] = None  # or you can choose to skip this key
            mapped_data.append(entry)

        # Display the result
        for entry in mapped_data:
            print(entry)
            entry['test_results_id'] = self.tr_id

        table_cls = TEST_CLASS_TABLE_MAP.get(test_table_name)
        self.db_session.bulk_insert_mappings(table_cls, mapped_data)
        self.db_session.commit()

        # Finally update the test_results table with final result
        # TODO: CSV, HTML, DUT_SW_VERSION etc.. later
        now = datetime.datetime.now()
        end_time = now.strftime("%Y-%m-%d %H:%M:%S")
        update_test_results = text("UPDATE test_results set pass_fail = :test_status, end_time = :end_time where id = "
                                   ":tr_id")
        if test_status:
            test_status = TestStatus.PASS
        else:
            test_status = TestStatus.FAIL
        with self.db.connect() as conn:
            self.log.info("Finally, updating the test_result status")
            conn.execute(update_test_results, {"test_status": test_status, "end_time": end_time, "tr_id": self.tr_id})
            conn.commit()

    def clean_up_resources(self):
        pass

    def upload_logs(self):
        pass

    def setup_resources(self):
        pass
