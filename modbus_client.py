import subprocess
import time
import json
import re

from typing import List, Tuple
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
        return self._fill_data_dict('Urms')

    def get_currents(self):
        return self._fill_data_dict('Irms')

    def get_energy_channels(self):
        return self._fill_data_dict('Total AP energy')

    def get_frequency(self):
        return self._fill_data_dict('Frequency')

    def get_power_for_phase(self):
        return self._fill_data_dict('P L')

    def get_phase_angle(self):
        return self._fill_data_dict('Phase angle L')

    def get_voltage_angle(self):
        return self._fill_data_dict('Voltage angle')

    # TODO как то обработать для всех случаев запрос строки
    def get_active_powers(self):
        total_power = {}
        scale = self._get_scale('Total P')
        for key, val in self._fill_address_dict_for_P('Total P').items():
            total_power[key] = self._convert_from_big_endian(self._get_numbers_int(val, 2)) * scale
        return total_power

    def _fill_data_dict(self, param_name):
        out_dict = {}
        scale, reg_count, is_little_endian = self._get_name_stat(param_name)

        for key, val in self._fill_address_dict(param_name).items():
            if is_little_endian:
                out_dict[key] = self._convert_from_little_endian(self._get_numbers_int(val, reg_count)) * scale
            else:
                out_dict[key] = self._convert_from_big_endian(self._get_numbers_int(val, reg_count)) * scale

        return out_dict

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
                try:
                    output = subprocess.check_output(command.split())
                    out_str_list = str(output).split('Data:')[1].split()[0:registers_count]
                except subprocess.CalledProcessError:
                    print('subprocess.CalledProcessError')
                    out_str_list = ''
                    pass

        return out_str_list

    def _fill_address_dict(self, name):
        out_dict = {}
        for x in self.config_data:
            if name in x['name']:
                out_dict[x['name']] = x['address']
        return out_dict

    def _fill_address_dict_for_P(self, name):
        out_dict = {}
        n = 'Total P'
        for x in self.config_data:
            try:
                raw_regex = f'Ch \d {n}$'
                regex = r'{}'.format(raw_regex)
                test = re.findall(regex, x['name'])[0]
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

    def _get_name_stat(self, name) -> Tuple[int, int, bool]:
        scale = 0
        reg_count = 1
        is_little = False
        for x in self.config_data:
            if name in x['name']:
                scale = x['scale']
                reg_count = int(x['format'][1:]) // 16
                if 'word_order' in x.keys():
                    if x['word_order'] == 'little_endian':
                        is_little = True
                break
        return scale, reg_count, is_little

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
