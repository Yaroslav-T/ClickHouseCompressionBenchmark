import csv
import time
import os
from utils import progress_bar
import config
from click_conn import Clickhouse
from generator import get_list_of_generators

HEADERS = [
    'column_type',
    'exec_time (sec)',
    'comparison_of_exec_time_with_raw_column (%)',
    'compress_data (b)',
    'uncompress_data (b)',
    'ratio compress/uncompress',
    'comparison_of_compression_with_raw_column (%)'
]

RESULT_PATH = './report/results.csv'


class Benchmark:

    def __init__(self):
        self._generators = get_list_of_generators()
        self._column_names = [g['name'] for g in self._generators]
        self._click = Clickhouse(self._generators)
        self._file = None
        self._csv = None

    def __enter__(self):
        self._file = open(RESULT_PATH, 'w+')
        self._csv = csv.writer(self._file)
        self._write(HEADERS)
        return self

    def _write(self, row):
        self._csv.writerow(row)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()

    def _create_data(self, size: int = 1000):
        d = []
        for _ in range(size):
            row = {}
            for g in self._generators:
                row[g['name']] = next(g['generator_value'])
            d.append(row)
        return d

    def _prepare_table(self):
        cycles = config.BENCHMARK_SIZE // config.BATCH_SIZE
        for i in range(cycles):
            progress_bar(i + 1, cycles)
            generate = self._create_data(config.BATCH_SIZE)
            t1 = time.time()
            self._click.insert_data(self._column_names, generate)

    def _run_benchmark(self):
        raw_exec_time = 0
        compressed_size_raw = 0
        for g in self._generators:
            column_name = g['name']
            is_raw = g['is_raw']
            exec_time = self._get_exec_time(column_name)
            compressed_size, uncompressed_size = self._get_column_size(column_name)
            if compressed_size == 0:
                raise ArithmeticError(f'Column {column_name} is too small')
            ratio = uncompressed_size / (compressed_size if compressed_size > 0 else 1)
            if is_raw:
                raw_exec_time = exec_time
                compressed_size_raw = ratio
                exec_with_raw = 100
                compress_with_raw = 100
            else:
                exec_with_raw = int((exec_time / raw_exec_time) * 100)
                compress_with_raw = int((ratio / (compressed_size_raw if compressed_size_raw > 0 else 1)) * 100)
            row = [column_name, round(exec_time / 10 ** 3, 5), exec_with_raw, compressed_size, uncompressed_size,
                   ratio, compress_with_raw]
            self._write(row)

    def _get_exec_time(self, column_name):
        return self._click.exec_query(f'SELECT max({column_name}) from test')

    def _get_column_size(self, column_name):
        compressed_size, uncompressed_size = self._click.table_size(column_name)
        return compressed_size, uncompressed_size

    def run(self):
        print('Prepare table...')
        self._prepare_table()
        try:
            self._run_benchmark()
        except ArithmeticError as e:
            print('Error: ', e)
        else:
            print('Done! Result in ./report/results.csv')


def main():
    with Benchmark() as benchmark:
        benchmark.run()


if __name__ == '__main__':
    main()
