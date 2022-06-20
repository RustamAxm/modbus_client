import time
import requests

from modbus_client import ModbusAPI_WB_MAP12E


def print_dic(dic):
    for key, val in dic.items():
        print(key, val)


def upload_dic(dic, table):
    url = 'http://lava.qat.yadro.com:8086/write?db=wirenboard_db'
    headers = {'Content-Type': 'text/plain'}
    for key, val in dic.items():
        payload = f"{table},channel={str(key).replace(' ', '_')},region=us-west value={round(val, 3)}"
        requests.request("POST", url, headers=headers, data=payload, verify=False)


def send_to_bd(client, slave):
    current = client.get_currents()
    voltage = client.get_voltages()
    upload_dic(current, f'slave_{slave}')
    upload_dic(voltage, f'slave_{slave}')


def test_my_api():
    ip = '172.17.27.127'
    port = 23
    print("CLIENT RUNING")
    slave_1 = 76
    slave_2 = 34
    client1 = ModbusAPI_WB_MAP12E(ip=ip,
                                  port=port,
                                  slave_address=slave_1)


    client2 = ModbusAPI_WB_MAP12E(ip=ip,
                                  port=port,
                                  slave_address=slave_2)

    while True:
        send_to_bd(client1, slave_1)
        send_to_bd(client2, slave_2)
        time.sleep(10)


def all(client):
    print_dic(client.get_voltages())
    print_dic(client.get_energy_channels())
    print_dic(client.get_frequency())
    print_dic(client.get_currents())
    print_dic(client.get_active_powers())

def test_all_stat():
    ip = '172.17.27.127'
    port = 23
    print("CLIENT RUNING")

    client1 = ModbusAPI_WB_MAP12E(ip=ip,
                                  port=port,
                                  slave_address=76)

    client2 = ModbusAPI_WB_MAP12E(ip=ip,
                                  port=port,
                                  slave_address=34)

    all(client1)
    print("__________________________________")
    all(client2)


if __name__ == '__main__':
    test_my_api()
    # test_all_stat()
