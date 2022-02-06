import psycopg2
from psycopg2.extras import execute_values
import logging
from configparser import ConfigParser


class Database:
    def __init__(self, config_filename="database.ini"):
        self.conn = self.__connect(config_filename)

    def __config(self, filename, section="postgresql"):
        logging.info("Reading config file...")
        parser = ConfigParser()
        parser.read(filename)

        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception(
                "Section {0} not found in the {1} file".format(section, filename)
            )

        return db

    def __connect(self, config_file):
        params = self.__config(filename=config_file)
        logging.info("Connecting to database...")
        conn = psycopg2.connect(**params)
        logging.info("Connected to database")
        return conn

    def query(self, query):
        cur = self.conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        cur.close()

        return result

    def write_to_db(self, query, data, template):
        cur = self.conn.cursor()
        execute_values(cur, query, data, template=template)
        self.conn.commit()
        cur.close()
