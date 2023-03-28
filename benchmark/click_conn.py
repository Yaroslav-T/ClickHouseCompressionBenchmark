from clickhouse_driver import Client
import config
from typing import Dict, List
import time
from generator import ColumnValue

# Connect to the ClickHouse database
clickhouse_client = Client(
    host=config.CLICKHOUSE_HOST,
    port=config.CLICKHOUSE_PORT,
    user=config.CLICKHOUSE_USERNAME,
    database=config.CLICKHOUSE_DATABASE,
    password=config.CLICKHOUSE_PASSWORD
)


class Clickhouse:
    def __init__(self, gen_list: List[ColumnValue]):
        self.conn = clickhouse_client
        self.gen_list = gen_list
        self._create_table()

    def _create_table(self):
        self.conn.execute(f'drop table if exists {config.CLICKHOUSE_BENCHMARK_TABLE_NAME};')
        query_middle = ''
        for column in self.gen_list:
            query_middle += f"{column['name']} {column['type']} {column['codec']},\n"
        query = f'''
        create table if not exists {config.CLICKHOUSE_BENCHMARK_TABLE_NAME}
        (
        {query_middle}

        dt DATETIME default now()
        )
         engine = MergeTree()
        ORDER BY dt
                '''

        self.conn.execute(query)

    def _get_avg_exec_time(self, query):

        self.conn.execute('SYSTEM FLUSH LOGS;')
        system_query = f'''
        SELECT avg(query_duration_ms) duration 
        FROM system.query_log WHERE type = 'QueryFinish'
and query = '{query}'
and query_start_time > now() - INTERVAL 1 minute;
'''
        data = self.conn.execute(system_query)
        duration = data[0][0]
        return duration

    def insert_data(self, names: List[str], data: list[Dict]):
        names = ', '.join(names)
        query = f'INSERT INTO {config.CLICKHOUSE_BENCHMARK_TABLE_NAME} ({names}) VALUES'
        self.conn.execute(query,
                          data)

    def exec_query(self, query, n=11):
        for i in range(n):
            self.conn.execute(query)
        return self._get_avg_exec_time(query)

    def table_size(self, column_name):
        query = f'''
        select name, type, data_compressed_bytes, 
            data_uncompressed_bytes
        from system.columns where database='{config.CLICKHOUSE_DATABASE}'
        and table='{config.CLICKHOUSE_BENCHMARK_TABLE_NAME}'
'''
        data = self.conn.execute(query)
        for d in data:
            if d[0] == column_name:
                return d[2], d[3]
