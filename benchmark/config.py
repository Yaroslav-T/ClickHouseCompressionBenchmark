import os

CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'localhost')
CLICKHOUSE_PORT = os.getenv('CLICKHOUSE_PORT', 9000)
CLICKHOUSE_DATABASE = os.getenv('CLICKHOUSE_DATABASE', 'default')
CLICKHOUSE_USERNAME = os.getenv('CLICKHOUSE_USERNAME', 'default')
CLICKHOUSE_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD', '')

CLICKHOUSE_BENCHMARK_TABLE_NAME = 'test'
BENCHMARK_SIZE = int(os.getenv('BENCHMARK_SIZE', 10 ** 5))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10 ** 5))

CODEC_LIST = (
    ('raw', '', True),

    # T64 codec only for integer types
    ('T64', 'CODEC(T64, LZ4)', False),
    ('Delta', 'CODEC(Delta(8), LZ4)', False),
    ('DoubleDelta', 'CODEC(DoubleDelta, LZ4)', False),
    ('Gorilla', 'CODEC(Gorilla, LZ4)', False),

    # FPC codec only for float types
    ('FPC', 'CODEC(FPC, LZ4)', False)
)

DEFAULT_GAUSS_MU = 10 ** 7
DEFAULT_GAUSS_SIGMA = 10 ** 7 // 2

CSV_FILENAME = os.getenv('CSV_FILENAME', 'test.csv')
CSV_DATATYPE = os.getenv('CSV_DATATYPE', 'Int64')
ONLY_CSV = os.getenv('ONLY_CSV', 'True').lower() in ("yes", "true", "t", "1")
