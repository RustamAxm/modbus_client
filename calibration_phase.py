import time
import requests

from modbus_client import ModbusClientForMap12e

def print_dic(dic):
    for key, val in dic.items():

        print(key, val)

def calibration():
    ip = '172.17.27.127'
    port = 23
    print("CLIENT RUNING")
    slave_1 = 34
    slave_2 = 34
    client1 = ModbusClientForMap12e(ip=ip,
                                    port=port,
                                    slave_address=slave_1)
    print_dic(client1.get_power_for_phase())
    print_dic(client1.get_voltages())
    print_dic(client1.get_currents())
    print_dic(client1.get_phase_angle())
    print_dic(client1.get_voltage_angle())


if __name__ == '__main__':
    calibration()
