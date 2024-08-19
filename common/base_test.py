import pytest


@pytest.mark.usefixtures("station")
class BaseTest(object):
    """
    Tests written in pytest format will inherit from this base class.
    """

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
