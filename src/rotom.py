import requests
import logging

Logger = logging.getLogger(__name__)


class Rotom:
    def __init__(self, url, schema):
        self.url = url
        self.schema = schema if schema is not None else 'http'
        self.info = RotomCheck()
        self.last_stats = self.get_stats()

    def get_stats(self):
        self.last_stats = requests.get(''.join([self.schema, '://', self.url.rstrip('/'), '/api/status'])).json()

    def get_atvs(self):
        for atv in self.last_stats['devices']:
            yield atv

    def get_workers(self):
        for worker in self.last_stats['workers']:
            if worker["isAllocated"]:
                yield worker

    def get_info(self):
        for atv in self.get_atvs():
            self.info.add_device(atv, atv['lastMemory']['memFree'], atv['lastMemory']['memMitm'], atv['lastMemory']['memStart'], atv["isAlive"])
        for worker in self.get_workers():
            Logger.info(worker)
            if worker['isAllocated']:
                Logger.info(f"{worker['controller']['origin']}")
                self.info.add_online_worker(worker['controller']['origin'], worker['workerId'], worker['worker']['isAlive'])
            # self.info.add_online_worker(atv['origin'], worker['workerId'], worker['worker']['isAlive'])
        return self.info.get_complete()

    def iterate_atvs(self):
        Logger.info("------------------------------------------")
        for atv in self.get_atvs():
            # Logger.info(atv)
            Logger.info(f"ATV          : {atv['origin']}")
            Logger.info(f"Free memory  : {atv['lastMemory']['memFree']}")
            Logger.info(f"Last memory  : {atv['lastMemory']['memMitm']}")
            Logger.info(f"Start memory : {atv['lastMemory']['memStart']}")
            Logger.info(f"Liveness     : {atv['isAlive']}")
            Logger.info("------------------------------------------")
        
        # for atv in self.get_atvs():
        #     print(atv)

    def iterate_workers(self):
        Logger.info("------------------------------------------")
        for worker in self.get_workers():
            # Logger.info(worker)
            Logger.info(f"ATV       : {worker['controller']['origin']}")
            Logger.info(f"Worker ID : {worker['workerId'].split('_')[-1]}")
            Logger.info(f"Liveness  : {worker['worker']['isAlive']}")
            Logger.info("------------------------------------------")


class RotomCheck:
    def __init__(self):
        self.devices = {}

    def add_device(self, device, free, mitm, start, alive):
        self.devices[device['origin']] = {
                "free_memory": free,
                "mitm_memory": mitm,
                "start_memory": start,
                "is_alive": alive,
                "workers": {}
            }

    def add_online_worker(self, device, worker, is_alive):
        self.devices[device]["workers"][worker.split('_')[-1]] = is_alive

    def get_complete(self):
        return self.devices
