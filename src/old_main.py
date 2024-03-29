import requests
import json
from adb_shell.adb_device import AdbDeviceTcp
import time

devices = {}
workers = {}

device_list = {}

with open("../devices.json") as f:
    device_list = json.loads(f.read())

def append_status_to_device(device, state):
    if len(devices[device]) >= 5:
        del devices[device][-1]
    devices[device].append(state)

def append_status_to_worker(device, state):
    if len(workers[device]) >= 12:
        del workers[device][-1]
    workers[device].append(state)

def scan_devices():
    res = requests.get("http://10.0.0.77:7072/api/status")

    if res.status_code != 200:
        print(f"Non-200 status code issued: {res.status_code}")
    else:
        data = res.json()
        i = 0
        for device in data['devices']:
            if device["origin"] not in devices:
                # print(f"Adding device {device['origin']} to devices")
                devices[device["origin"]] = []
                # print(devices)
            append_status_to_device(device["origin"], device["isAlive"])
            i += 1
        for worker in data['workers']:
            if worker["worker"]["origin"] not in workers:
                workers[worker["controller"]["origin"]] = []
            try:
                append_status_to_worker(worker["controller"]["origin"], worker["worker"]["isAlive"])
            except KeyError as ex:
                print(f"""Exception: {type(ex)} {ex.args} {ex}""")
                print(f"Worker    : {worker}")

def reboot_device(ip_address):
    dev = AdbDeviceTcp(ip_address)
    print("constructed")
    dev.connect()
    print("connected")
    dev.reboot()
    print("rebooted")
    time.sleep(90)
    print("slept 90")
    dev = AdbDeviceTcp(ip_address)
    print("device initialised agane")
    dev.connect()
    print("connected agane")
    dev.shell('/data/local/tmp/run_egg.sh')
    print("launched process")

def restart_process(ip_address):
    dev = AdbDeviceTcp(ip_address)
    print("constructed")
    dev.connect()
    print("connected")
    dev.shell("/data/local/tmp/stop_egg.sh")
    print("killed process")
    time.sleep(10)
    print("slept 10")
    dev.shell('/data/local/tmp/run_egg.sh')
    print("launched process")

def check_states():
    for device in devices:
        if not all(devices[device]):
            ip = device_list[device]
            print(f"Device {device} offline, attempting reboot {ip}")
            devices[device] = []
            restart_process(ip)

# while True:
#     scan_devices()
#     check_states()
#     time.sleep(90)


# reboot_device("10.0.1.4")
reboot_device("10.0.1.5")
# reboot_device("10.0.1.6")
# reboot_device("10.0.1.7")

# restart_process("10.0.1.4")
# restart_process("10.0.1.5")
# restart_process("10.0.1.6")
# restart_process("10.0.1.7")


#17:33:49 WARNING main.py:58 atv6 :   {'free_memory': 223984, 'mitm_memory': 831651, 'start_memory': 353098, 'is_alive': False, 'workers': {}}


# to release accounts, query:
# UPDATE account
# SET last_released = 1, last_selected = 1
# WHERE last_released IS NOT NULL
# AND level < 30
# AND last_released < UNIX_TIMESTAMP(NOW() - INTERVAL 2 HOUR);
#
# then simply call http://10.0.0.77:7072/reload/accounts