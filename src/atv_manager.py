from adb_shell.adb_device import AdbDeviceTcp


class ATVManager:
    def __init__(self, ip_address):
        self.device = AdbDeviceTcp(ip_address)

    def connect(self):
        self.device.connect()

    def reboot(self):
        self.device.reboot()

    def stop_process(self):
        self.device.shell("/data/local/tmp/stop_egg.sh")

    def start_process(self):
        self.device.shell('/data/local/tmp/run_egg.sh')

    def restart_process(self):
        self.stop_process()
        self.start_process()
