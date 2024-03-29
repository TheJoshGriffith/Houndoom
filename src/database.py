import mysql.connector
import logging

Logger = logging.getLogger(__name__)


class DBWrapper:
    def __init__(self, host, port, user, password, db):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_conn = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db
        )
        self.create_atvs_table()
        self.create_mitm_memory_table()
        self.create_workers_table()
        self.create_workers_online_table()

    def create_atvs_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS atvs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            ip_address VARCHAR(255)
        )
        """
        self.execute(query)

    def create_mitm_memory_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS mitm_memory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            current_memory INT,
            max_memory INT,
            free_memory INT,
            atv_id INT,
            FOREIGN KEY (atv_id) REFERENCES atvs(id)
        )
        """
        self.execute(query)

    def create_workers_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS workers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            atv_id INT,
            worker_id INT,
            FOREIGN KEY (atv_id) REFERENCES atvs(id)
        )
        """
        self.execute(query)

    def create_workers_online_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS worker_online (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            worker_id INT,
            is_alive BOOLEAN,
            atv_id INT,
            FOREIGN KEY (atv_id) REFERENCES atvs(id),
            FOREIGN KEY (worker_id) REFERENCES workers(id)
        )
        """
        self.execute(query)

    def create_atv(self, name, ip_address):
        query = """
        INSERT INTO atvs (name, ip_address)
        SELECT %s, %s
        WHERE NOT EXISTS (
            SELECT * FROM atvs WHERE name = %s AND ip_address = %s
        )
        """
        params = (name, ip_address, name, ip_address)
        self.execute(query, params)
        self.db_conn.commit()

    def create_mitm_memory(self, current_memory, max_memory, free_memory, atv_name):
        query = """
        INSERT INTO mitm_memory (current_memory, max_memory, free_memory, atv_id)
        VALUES (%s, %s, %s, (SELECT id FROM atvs WHERE name = %s))
        """
        params = (current_memory, max_memory, free_memory, atv_name)
        Logger.info(query % params)
        self.execute(query, params)
        self.db_conn.commit()

    def create_worker(self, worker_id, atv_name):
        query = """
        INSERT INTO workers (atv_id, worker_id, name)
        VALUES ((SELECT id FROM atvs WHERE name = %s), %s, %s)
        ON DUPLICATE KEY UPDATE id=id
        """
        params = (atv_name, worker_id, ''.join([atv_name, '_', worker_id]))
        Logger.info(query % params)
        self.execute(query, params)
        self.db_conn.commit()

    def create_worker_online(self, worker_id, atv_name, is_alive):
        query = """
        INSERT INTO worker_online (worker_id, atv_id, is_alive)
        VALUES ((SELECT id FROM workers WHERE name = %s), (SELECT id FROM atvs WHERE name = %s), %s)
        """
        params = (''.join([atv_name, '_', worker_id]), atv_name, is_alive)
        Logger.info(query % params)
        self.execute(query, params)
        self.db_conn.commit()

    def get_workers(self):
        query = """
        SELECT * FROM workers
        """
        c = self.db_conn.cursor()
        c.execute(query)
        return c.fetchall()

    def execute(self, query, params=None):
        c = self.db_conn.cursor()
        c.execute(query, params)

    def close(self):
        self.pool.close()
        self.pool.wait_closed()
