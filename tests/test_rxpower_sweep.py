import pytest
from base_test import BaseTest
import os
import yaml
import matplotlib.pyplot as plt
import math
import time

TEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

SWEEP_CONFIG_DIR = os.path.join(TEST_DIR, "recipes")
SWEEP_CONFIG_PATH = os.path.join(SWEEP_CONFIG_DIR, "test_rxpower_sweep.yaml")

class SweepSettings(object):
    @classmethod
    def sweep_settings(cls):
        with open(SWEEP_CONFIG_PATH) as sweep_config:
            return yaml.safe_load(sweep_config.read())

class TestRxpowerSweep(BaseTest):

    #region setupMethod
    def setup_method(self):
        self.opm = self.station.tx_opm
        self.att = self.station.tx_attenuator
        self.dut = self.sub20
        self.sweep_configs = SweepSettings.sweep_settings().get('sweep_settings')
        self.wavelength = self.sweep_configs['initial_wl']
        self.initial_attn = self.sweep_configs['initial_attenuation']
        self.sweep_start = self.sweep_configs['sweep_start']
        self.sweep_stop = self.sweep_configs['sweep_stop']
        self.sweep_step = self.sweep_configs['sweep_step']
        self.delay_ms = self.sweep_configs['delay_sec']
        self.pm_configs = SweepSettings.sweep_settings().get('powermeter_settings')
        self.pm_wavelength = self.pm_configs['initial_wl']
        self.pm_averaging = self.pm_configs['averaging']
        self.pm_unit = self.pm_configs['unit']
        self.memaddr = 0xA0

    # endregion

    # region configureEquipment
    def configure_equipment(self):
        self.att.output = 1
        self.att.attenuation = self.initial_attn
        self.att.wavelength = self.wavelength
        self.log.info("Attenuation = {} and WaveLength = {}".format(self.att.attenuation, self.att.wavelength))

        self.opm.wavelength = self.pm_wavelength
        self.opm.averaging_time = self.pm_averaging
        self.opm.unit = self.pm_unit
        self.log.info("pm_wl = {}, pm_averaging = {}, unit = {}".format(self.opm.wavelength, self.opm.averaging_time, self.opm.unit))

    # endregion

    # region configureDut
    def configure_dut(self):
        dut_sn = self.dut.i2c_read(self.memaddr, 0xC4, 16)
        chrlist= [chr(decimal) for decimal in dut_sn]
        module_sn = ''.join(chrlist)
        self.log.info("Module SN: {}".format(module_sn.strip("")))
        dut_tx_status = self.dut.i2c_read(self.memaddr, 86, 1)
        if(dut_tx_status[0] & 0xF == 0xF):
            self.log.info("dut tx is disabled, so enable the Tx on all 4 channels")
            self.dut.i2c_write(self.memaddr, 86, (dut_tx_status[0] & 0xF0))
        else:
            if (dut_tx_status[0] & 0xF == 0):
                self.log.info("Dut Tx is enabled")

        dut_rx_reporting_mode = self.dut.i2c_read(self.memaddr, 220, 1)
        if (dut_rx_reporting_mode[0] & 0x8 == 0):
            self.log.info("Dut rx reporting mode is OMA")
        else:
            self.log.info("Dut rx reporting mode is average power")

        dut_temp = self.dut.i2c_read(self.memaddr, 22, 2)
        dut_temperature = self.get_dut_temp(dut_temp)

        dut_volt = self.dut.i2c_read(self.memaddr, 26, 2)
        dut_voltage = self.get_dut_vol(dut_volt)

        self.log.info("Dut Temperature = {} and Dut Voltage = {}".format(dut_temperature, dut_voltage))

        tx_bias_mA = self.get_tx_bias_current()
        self.log.info("Tx1 Bias = {}mA, Tx2 Bias = {}mA, Tx3 Bias = {}mA, Tx4 Bias = {}mA".format(tx_bias_mA[0], tx_bias_mA[1], tx_bias_mA[2], tx_bias_mA[3]))

        tx_power_mW = self.get_tx_power()
        self.log.info("Tx1 power = {}mW, Tx2 power = {}mW, Tx3 power = {}mW, Tx4 power = {}mW".format(tx_power_mW[0], tx_power_mW[1], tx_power_mW[2], tx_power_mW[3]))

        tx_total_power_mW = tx_power_mW[0] + tx_power_mW[1] + tx_power_mW[2] + tx_power_mW[3]
        self.log.info("tx total power = {} mW".format(tx_total_power_mW))

        tx_total_power_dBm = 10 * math.log10(tx_total_power_mW)
        self.log.info("tx total power = {} dBm".format(tx_total_power_dBm))

        rx_power_mW = self.get_rx_power()
        self.log.info("Rx1 power = {}mW, Rx2 power = {}mW, Rx3 power = {}mW, Rx4 power = {}mW".format(rx_power_mW[0],
                                                                                                      rx_power_mW[1],
                                                                                                      rx_power_mW[2],
                                                                                                      rx_power_mW[3]))

        rx_total_power_mW = rx_power_mW[0] + rx_power_mW[1] + rx_power_mW[2] + rx_power_mW[3]
        self.log.info("tx total power = {} mW".format(rx_total_power_mW))

        rx_total_power_dBm = 10 * math.log10(rx_total_power_mW)
        self.log.info("tx total power = {} dBm".format(rx_total_power_dBm))
    # endregion

    # region getDutTemp
    def get_dut_temp(self, dut_temp):
        dut_temp_adc = dut_temp[0] << 8 | dut_temp[1]
        if(dut_temp_adc > 32767):
            return (-1 * (0x10000 - dut_temp_adc) / 256.0)
        else:
            return (dut_temp_adc / 256.0)

    # endregion

    #region getDutVoltage
    def get_dut_vol(self, dut_voltage):
        dut_volt = dut_voltage[0] << 8 | dut_voltage[1]
        return (dut_volt / 10000.0)
    # endregion

    # region getTxBiasCurrent
    def get_tx_bias_current(self):
        tx_bias_list = list()
        tx_bias_current = self.dut.i2c_read(self.memaddr, 42, 8)
        tx1_bias = (tx_bias_current[0] << 8 | tx_bias_current[1]) * 2
        tx2_bias = (tx_bias_current[2] << 8 | tx_bias_current[3]) * 2
        tx3_bias = (tx_bias_current[4] << 8 | tx_bias_current[5]) * 2
        tx4_bias = (tx_bias_current[6] << 8 | tx_bias_current[7]) * 2

        tx_bias_list.append(tx1_bias / 1000.0)
        tx_bias_list.append(tx2_bias / 1000.0)
        tx_bias_list.append(tx3_bias / 1000.0)
        tx_bias_list.append(tx4_bias / 1000.0)

        return tx_bias_list
    # endregion

    # region getTxPower
    def get_tx_power(self):
        tx_power_mW = list()
        tx_power = self.dut.i2c_read(self.memaddr, 50, 8)
        tx1_power = (tx_power[0] << 8 | tx_power[1]) * 0.1
        tx2_power = (tx_power[2] << 8 | tx_power[3]) * 0.1
        tx3_power = (tx_power[4] << 8 | tx_power[5]) * 0.1
        tx4_power = (tx_power[6] << 8 | tx_power[7]) * 0.1

        tx_power_mW.append(tx1_power / 1000.0)
        tx_power_mW.append(tx2_power / 1000.0)
        tx_power_mW.append(tx3_power / 1000.0)
        tx_power_mW.append(tx4_power / 1000.0)

        return tx_power_mW
    # endregion

    # region getRxPower
    def get_rx_power(self):
        rx_power_mW = list()
        rx_power = self.dut.i2c_read(self.memaddr, 50, 8)
        rx1_power = (rx_power[0] << 8 | rx_power[1]) * 0.1
        rx2_power = (rx_power[2] << 8 | rx_power[3]) * 0.1
        rx3_power = (rx_power[4] << 8 | rx_power[5]) * 0.1
        rx4_power = (rx_power[6] << 8 | rx_power[7]) * 0.1

        rx_power_mW.append(rx1_power / 1000.0)
        rx_power_mW.append(rx2_power / 1000.0)
        rx_power_mW.append(rx3_power / 1000.0)
        rx_power_mW.append(rx4_power / 1000.0)

        return rx_power_mW
    # endregion

    def test_rxpower_sweep(self):

        test_status = False
        self.setup(self.__class__.__name__, SWEEP_CONFIG_PATH)
        self.log.info("Enabling the attenuator with initial attenuation")

        data_results = {}
        self.log.info("Start Measurements...")
        self.configure_equipment()
        if(self.att.output == 0):
            self.log.info("Enable the attenuator")
            self.att.output = 1
            time.sleep(self.delay_ms)
        else:
            self.log.info("Attenuator is enabled")


        self.configure_dut()

        data_string = "Idx,Attenuation_dB,Power_dBm,Rx1_Power_mW,Rx2_Power_mW,Rx3_Power_mW,Rx4_Power_mW,Rx_Total_power_dBm"
        self.log.info(data_string)
        self.log.log_csv(data_string)
        index = 0
        data_list = list()
        wl_list = list()
        for attn in range(self.sweep_start, self.sweep_stop, self.sweep_step):
            data_string = ""
            self.att.attenuation = attn
            time.sleep(self.delay_ms)
            rx_power_mW = self.get_rx_power()

            rx_total_power_mW = rx_power_mW[0] + rx_power_mW[1] + rx_power_mW[2] + rx_power_mW[3]
            self.log.info("tx total power = {} mW".format(rx_total_power_mW))

            rx_total_power_dBm = 10 * math.log10(rx_total_power_mW)
            self.log.info("tx total power = {} dBm".format(rx_total_power_dBm))

            data_string += f'{str(index)},'
            data_string += f'{str(attn)},'
            data_string += str(self.opm.power)
            data_string += str(rx_power_mW[0])
            data_string += str(rx_power_mW[1])
            data_string += str(rx_power_mW[2])
            data_string += str(rx_power_mW[3])
            data_string += str(rx_total_power_dBm)
            self.log.info(data_string)
            data_list.append((attn, self.opm.power, rx_power_mW[0], rx_power_mW[1], rx_power_mW[2], rx_power_mW[3]))
            self.log.log_csv(data_string)
            wl_list.append(self.wavelength)
            index += 1

        data_results['wavelength'] = wl_list
        data_results['attenuation'] = [point[0] for point in data_list]
        data_results['tx_opm_power'] = [point[1] for point in data_list]
        data_results['rx1_power_mW'] = [point[2] for point in data_list]
        data_results['rx2_power_mW'] = [point[3] for point in data_list]
        data_results['rx3_power_mW'] = [point[3] for point in data_list]
        data_results['rx4_power_mW'] = [point[4] for point in data_list]
        data_results['rx_total_power_dBm'] = [point[5] for point in data_list]

        self.record_results("TestRxPowerSweep", data_results, test_status)















