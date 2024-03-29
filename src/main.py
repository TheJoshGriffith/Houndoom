from atv_manager import ATVManager
from configparser import ConfigParser
from rotom import Rotom
from database import DBWrapper
import logging
import sys
import time

Logger = logging.getLogger(__name__)

config = ConfigParser()
config.read('config.ini')

root = logging.getLogger()
root.setLevel(logging.getLevelName(config.get('logger', 'level')))
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)8s %(levelname)5s %(filename)s:%(lineno)d %(message)s', "%H:%M:%S")
handler.setFormatter(formatter)
root.addHandler(handler)

rotom_url = config.get('rotom', 'url')
rotom_schema = config.get('rotom', 'schema')
db_url = config.get('database', 'url')
db_port = config.get('database', 'port')
db_user = config.get('database', 'user')
db_password = config.get('database', 'password')
db_database = config.get('database', 'database')
atvs = config['atvs']

Logger.info("Connecting to ATVs")

atv_objects = {}

for k, v in atvs.items():
    Logger.info(f"Connecting to {k}, {v}")
    atv_objects[k] = ATVManager(v)
    atv_objects[k].connect()

rtm = Rotom(rotom_url, rotom_schema)


#within the ATV, we need to iterate the ATVs and ship the data to mysql
# rtm.iterate_atvs()
# rtm.iterate_workers()
while True:
    rtm.get_stats()
    info = rtm.get_info()

    import json

    Logger.info(json.dumps(info))
    Logger.info(atvs)

    d = DBWrapper(db_url, db_port, db_user, db_password, db_database)

    for k,v in info.items():
        Logger.warning(atvs[k])
        Logger.warning(f"{k} :   {v}")
        if not v['is_alive']:
            Logger.warning(f"Restarting device : {k}, as it is not alive")
            atv_objects[k].restart_process()

        if len(v['workers']) == 0:
            Logger.warning(f"Rebooting device : {k}, as it has no workers")
            atv_objects[k].restart_process()

        d.create_atv(k, atvs[k])
        d.create_mitm_memory(v['mitm_memory'], v['start_memory'], v['free_memory'], k)

        for i,j in v['workers'].items():
            Logger.info(f"Creating worker {j} : {k}_{i}")
            d.create_worker(i, k)
            d.create_worker_online(i, k, j)

    time.sleep(120)
