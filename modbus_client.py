import subprocess
import time
from typing import List
import json
import time
import requests

def parser():
    ip = '172.17.27.127'
    port = 23
    register = 5136
    count = 1
    slave_address = 76
    command = 'modbus_client --debug -mtcp -t0x03 {} -p{} -a{} -r{} -c {}'.format(ip,
                                                                                  port,
                                                                                  slave_address,
                                                                                  register,
                                                                                  count).split()
    output = subprocess.run(command, capture_output=True)
    print(output)


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
        for key, val in self._fill_address_dict('Total P').items():
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
        command = self.command_str + ' {} -p{} -a{} -r{} -c {}'.format(self.ip,
                                                                       self.port,
                                                                       self.slave_address,
                                                                       register,
                                                                       registers_count)

        output = subprocess.check_output(command.split())
        out_str_list = str(output).split('Data:')[1].split()[0:registers_count]
        return out_str_list

    def _fill_address_dict(self, name):
        out_dict = {}
        for x in self.config_data:
            if name in x['name']:
                out_dict[x['name']] = x['address']
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
            sum_ += 2**(i * 16) * reg_list_[i]
        return sum_

    @staticmethod
    def _convert_from_big_endian(reg_list_):
        sum_ = 0
        for i in range(len(reg_list_)):
            sum_ += 2 ** (i * 16) * reg_list_[len(reg_list_) - i - 1]
        return sum_



# def test_modbus():
#     client = ModbusTcpClient('172.17.27.127', port=23)
#     # client.write_coil(1, True)
#     result = client.read_holding_registers(address=5136, count=1, SLAVE=76)
#     print(result)
#     client.close()


def print_dic(dic):
    for key, val in dic.items():
        print(key, val)


        # command = 'curl -i -XPOST "http://lava.qat.yadro.com:8086/write?db=wirenboard_db" --data-binary "current,sensor={},region=us-west value={}"'\
        #     .format(str(key).replace(' ', '_'), round(val, 4))
        # subprocess.run(command.split())
        # time.sleep(0.1)

def upload_dic(dic):
    url = 'http://lava.qat.yadro.com:8086/write?db=wirenboard_db'
    headers = {'Content-Type': 'text/plain'}
    for key, val in dic.items():
        payload = f"current,channel={str(key).replace(' ', '_')},region=us-west value={round(val, 3)}"
        requests.request("POST", url, headers=headers, data=payload, verify=False)

def all(client):
    # print_dic(client1.get_voltages())
    # print_dic(client1.get_energy_channels())
    # print_dic(client1.get_frequency())
    print_dic(client.get_currents())
    # print_dic(client1.get_active_powers())

def data_base_send(client, repeat):
    dict_ = client.get_currents()
    for _ in range(repeat):
        upload_dic(dict_)
        print_dic(dict_)
        time.sleep(2)

def test_my_api():
    ip = '172.17.27.127'
    port = 23
    print("CLIENT RUNING")

    client1 = ModbusAPI_WB_MAP12E(ip=ip,
                                     port=port,
                                     slave_address=76)


    client2 = ModbusAPI_WB_MAP12E(ip=ip,
                                  port=port,
                                  slave_address=34)

    while True:
        try:  # used try so that if user pressed other than the given key error will not be shown
            current = client1.get_currents()
            voltage = client1.get_voltages()
            upload_dic(current)
            upload_dic(voltage)
            time.sleep(30)
            print("send")
        except:
            break



if __name__ == '__main__':

    test_my_api()