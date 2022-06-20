import subprocess
import time
import json
import re

from typing import List
from contextlib import suppress


class ModbusAPI_WB_MAP12E:
    def __init__(self, ip, port, slave_address):
        self.ip = ip
        self.port = port
        self.slave_address = slave_address
        self.command_str = 'modbus_client --debug -mtcp -t0x03'

        with open('config_map12e.json', 'r') as read_file:
            self.config_data = json.load(read_file)['device']['channels']

    def device_name(self):
        self._send_command(200, 6)

    def get_voltages(self):
        voltages_dic = {}
        scale = self._get_scale('Urms')
        for key, val in self._fill_address_dict('Urms').items():
            voltages_dic[key] = self._convert_from_big_endian(self._get_numbers_int(val, 2)) * scale

        return voltages_dic

    def get_currents(self):
        current_dic = {}
        scale = self._get_scale('Irms')
        for key, val in self._fill_address_dict('Irms').items():
            current_dic[key] = self._convert_from_big_endian(self._get_numbers_int(val, 2)) * scale

        return current_dic

    # TODO сделать отдельный считыватель показаний по типу данных в словаре u32 - 2 регистра и тд
    def get_active_powers(self):
        total_power = {}
        scale = self._get_scale('Total P')
        for key, val in self._fill_address_dict_for_P('Total P').items():
            total_power[key] = self._convert_from_big_endian(self._get_numbers_int(val, 2)) * scale
        return total_power

    def get_energy_channels(self):
        energy_dic = {}
        scale = self._get_scale('Total AP energy')
        for key, val in self._fill_address_dict('Total AP energy').items():
            energy_dic[key] = self._convert_from_little_endian(self._get_numbers_int(val, 4)) * scale

        return energy_dic

    def get_frequency(self):
        freq_dic = {}
        scale = self._get_scale('Frequency')
        for key, val in self._fill_address_dict('Frequency').items():
            freq_dic[key] = self._convert_from_big_endian(self._get_numbers_int(val, 1)) * scale
        return freq_dic

    def _get_numbers_int(self, register, registers_count):
        out_str_list = self._send_command(register, registers_count)
        out_int = [int(x, 16) for x in out_str_list]
        return out_int

    def _send_command(self, register, registers_count) -> List[str]:

        command = self.command_str + \
                  f' {self.ip} -p{self.port} -a{self.slave_address} -r{register} -c {registers_count}'

        out_str_list = ''

        while not out_str_list:
            with suppress(IndexError):
                time.sleep(0.1)
                output = subprocess.check_output(command.split())
                out_str_list = str(output).split('Data:')[1].split()[0:registers_count]

        return out_str_list

    def _fill_address_dict(self, name):
        out_dict = {}
        for x in self.config_data:
            if name in x['name']:
                out_dict[x['name']] = x['address']
        return out_dict

    def _fill_address_dict_for_P(self, name):
        out_dict = {}
        for x in self.config_data:
            try:
                test = re.findall(r'Ch \d{1} Total P$', x['name'])[0]
                out_dict[test] = x['address']
            except IndexError:
                pass
        return out_dict

    def _get_scale(self, name):
        scale = 0
        for x in self.config_data:
            if name in x['name']:
                scale = x['scale']
                break
        return scale

    @staticmethod
    def _convert_from_little_endian(reg_list_):
        sum_ = 0
        for i in range(len(reg_list_)):
            sum_ += 2 ** (i * 16) * reg_list_[i]
        return sum_

    @staticmethod
    def _convert_from_big_endian(reg_list_):
        sum_ = 0
        for i in range(len(reg_list_)):
            sum_ += 2 ** (i * 16) * reg_list_[len(reg_list_) - i - 1]
        return sum_
