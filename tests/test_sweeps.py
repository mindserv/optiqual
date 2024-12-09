import pytest
from base_test import BaseTest
import os
import yaml
import matplotlib.pyplot as plt

TEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

SWEEP_CONFIG_DIR = os.path.join(TEST_DIR, "recipes")
# TODO: Move to base cls. Recipe file name must match with class name but with underscores. Example, TestSweeps will
#  become test_sweeps
SWEEP_CONFIG_PATH = os.path.join(SWEEP_CONFIG_DIR, "test_sweeps.yaml")


class SweepSettings(object):

    @classmethod
    def sweep_settings(cls):
        with open(SWEEP_CONFIG_PATH) as sweep_config:
            return yaml.safe_load(sweep_config.read())


#@pytest.mark.usefixtures("station")
class TestSweeps(BaseTest):

    def setup_method(self):
        self.opm = self.station.tx_opm
        self.att = self.station.tx_attenuator
        self.sweep_configs = SweepSettings.sweep_settings().get('sweep_settings')
        self.wavelength = self.sweep_configs['initial_wl']
        self.initial_attn = self.sweep_configs['initial_attenuation']
        self.sweep_start = self.sweep_configs['sweep_start']
        self.sweep_stop = self.sweep_configs['sweep_stop']
        self.sweep_step = self.sweep_configs['sweep_step']
        self.delay_sec = self.sweep_configs['delay_sec']

        print(self.sub20)

    #import matplotlib.pyplot as plt

    # Input data
    """
    data = [
        (0, -83.35007),
        (1, -83.35007),
        (2, -83.35007),
        (3, -83.35007),
        (4, -83.35007),
        (5, -83.35007),
        (6, -83.35007),
        (7, -83.35007),
        (8, -83.35007),
        (9, -83.35007),
        (10, -83.35007),
        (11, -83.35007),
        (12, -83.35007),
        (13, -83.35007),
        (14, -83.35007),
    ]
    """

    result_data = {"wavelength": [1310.00, 1310.00, 1310.00, 1310.00, 1310.00, 1310.00, 1310.00,
                          1310.00, 1310.00, 1310.00, 1310.00, 1310.00, 1310.00, 1310.00, 1310.00],
                   "attenuation": [0.00, 1.01, 2.02, 3.03, 4.04, 5.05, 6.06, 7.07, 8.08, 9.09, 10.10, 11.11, 12.12, 13.13,
                             14.14],
                   "rx_power": [-84.29186, -84.34473, -84.34473, -84.34473, -84.34473, -84.34473, -84.34473,
                                -84.34473, -84.34473, -84.34473, -84.34473, -84.33258, -84.33258, -84.33258, -84.33258]}

    def generate_chart(self, data):
        # Extract x and y values
        x_values = [point[0] for point in data]
        y_values = [point[1] for point in data]

        # Create a line plot
        plt.figure(figsize=(10, 5))
        plt.plot(x_values, y_values, marker='o', linestyle='-', color='b')

        # Add labels and title
        plt.title('Line Plot of Input Data')
        plt.xlabel('X values')
        plt.ylabel('Y values')
        plt.axhline(y=-83.35007, color='r', linestyle='--', label='Y = -83.35007')  # Highlight constant value
        plt.legend()
        plt.grid()

        # Show the plot
        plt.show()

    @pytest.mark.dependency
    def test_attenuator_sweep(self):
        test_status = False
        self.setup(self.__class__.__name__, SWEEP_CONFIG_PATH)
        self.log.info("Enabling the attenuator with initial attenuation")
        """
        self.att.output = 1
        self.att.attenuation = self.initial_attn
        self.att.wavelength = self.wavelength
        self.opm.wavelengthc = self.wavelength
        data_string = "Idx,Attenuation_dB,Power_dBm"
        self.log.log_csv(data_string)
        index = 0
        data_list = list()
        wl_list = list()
        data_results = {"wl":[], "pwr":[], "atten":[]}
        for attn in range(self.sweep_start, self.sweep_stop, self.sweep_step):
            data_string = ""
            self.att.attenuation = attn
            data_string += f'{str(index)},'
            data_string += f'{str(attn)},'
            data_string += str(self.opm.power)
            self.log.info(data_string)
            data_list.append((attn, self.opm.power))
            self.log.log_csv(data_string)
            wl_list.append(self.wavelength)
            index += 1

        data_results['Wl'] = wl_list
        data_results['atten'] = [point[0] for point in data_list]
        data_results['pwr'] = [point[1] for point in data_list]


        self.generate_chart(data_list)
        """
        self.record_results("TestSweeps", TestSweeps.result_data, test_status)
        # TODO: Better pass/fail criteria
        self.log.info(f'Test completed, final status is {test_status} (False=FAILED, True=PASSED)')
        # Assert force pass
        assert not test_status