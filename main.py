import time
import requests

from modbus_client import ModbusClientForMap12e


def print_dict(dic):
    for key, val in dic.items():
        print(key, val)


def upload_dict(dic, table):
    url = 'http://lava.qat.yadro.com:8086/write?db=wirenboard_db'
    headers = {'Content-Type': 'text/plain'}
    for key, val in dic.items():
        payload = f"{table},channel={str(key).replace(' ', '_')},region=us-west value={round(val, 3)}"
        requests.request("POST", url, headers=headers, data=payload, verify=False)


def send_to_bd(client, slave):
    current = client.get_currents()
    voltage = client.get_voltages()
    power = client.get_active_powers()
    energy = client.get_energy_channels()
    power_for_phase = client.get_power_for_phase()
    upload_dict(current, f'slave_{slave}')
    upload_dict(voltage, f'slave_{slave}')
    upload_dict(power, f'slave_{slave}')
    upload_dict(energy, f'slave_{slave}')
    upload_dict(power_for_phase, f'slave_{slave}')
    # for extremum of values
    # extremum_voltage = client.get_peak_voltages()
    # extremum_current = client.get_peak_currents()
    # upload_dict(extremum_voltage, f'extremum_{slave}')
    # upload_dict(extremum_current, f'extremum_{slave}')


def test_my_api():
    ip = '172.17.27.127'
    port = 23
    print("CLIENT RUNING")
    slave_1 = 76
    slave_2 = 34
    client1 = ModbusClientForMap12e(ip=ip,
                                    port=port,
                                    slave_address=slave_1)


    client2 = ModbusClientForMap12e(ip=ip,
                                    port=port,
                                    slave_address=slave_2)

    while True:
        send_to_bd(client1, slave_1)
        send_to_bd(client2, slave_2)
        time.sleep(10)


def all(client):
    print_dict(client.get_voltages())
    print_dict(client.get_energy_channels())
    print_dict(client.get_frequency())
    print_dict(client.get_currents())
    print_dict(client.get_active_powers())
    print_dict(client.get_peak_voltages())
    print_dict(client.get_peak_currents())


def test_all_stat():
    ip = '172.17.27.127'
    port = 23
    print("CLIENT RUNING")

    client1 = ModbusClientForMap12e(ip=ip,
                                    port=port,
                                    slave_address=76)

    client2 = ModbusClientForMap12e(ip=ip,
                                    port=port,
                                    slave_address=34)

    all(client1)
    print("__________________________________")
    all(client2)


if __name__ == '__main__':
    test_my_api()
    # test_all_stat()
