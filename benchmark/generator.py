import random
from typing import TypedDict, Iterator, List
import config
from config import CODEC_LIST
from utils import max_click_dt, min_click_dt


def gen_rand(a, b):
    while 1:
        r = random.randint(a, b)
        yield r


def gen_rand_float():
    while 1:
        r = random.random() * (10 ** random.randint(1, 9))
        yield r * 100


def gen_const(a, b):
    while 1:
        for i in range(a, b):
            yield i


def gen_const_float(a, b):
    while 1:
        for i in range(a + 10 ** 5, b + 10 ** 5):
            yield float(i / (10 ** 4 - 1))


def gen_gauss(mu=config.DEFAULT_GAUSS_MU, sigma=config.DEFAULT_GAUSS_SIGMA):
    while 1:
        v = random.gauss(mu, sigma)
        yield v


def gen_int_gauss(mu=config.DEFAULT_GAUSS_MU, sigma=config.DEFAULT_GAUSS_SIGMA):
    while 1:
        v = random.gauss(mu, sigma)
        yield int(v)


def csv_generator(csv_type):
    with open(f'./csv/{config.CSV_FILENAME}', 'r') as f:
        row = f.readline()
        while 1:
            while row:
                if csv_type == 'INT':
                    yield int(row)
                elif csv_type == 'FLOAT':
                    yield float(row)
                row = f.readline()
            f.seek(0)
            row = f.readline()


list_of_generators = [
    ('rand_seq_Int64', 'Int64', gen_rand(0, 10 ** 9)),
    ('rand_seq_Int32', 'Int32', gen_rand(0, 10 ** 9)),
    ('rand_seq_DateTime', 'DateTime', gen_rand(min_click_dt(), max_click_dt())),
    ('rand_float_seq_Float64', 'Float64', gen_rand_float()),
    ('rand_float_seq_Float32', 'Float', gen_rand_float()),

    ('const_seq_Int64', 'Int64', gen_const(0, 10 ** 9)),
    ('const_seq_Int32', 'Int32', gen_const(0, 10 ** 9)),
    ('const_seq_DateTime', 'DateTime', gen_const(min_click_dt(), max_click_dt())),
    ('const_float_seq_Float64', 'Float64', gen_const_float(0, 10 ** 9)),
    ('const_float_seq_Float32', 'Float', gen_const_float(0, 10 ** 9)),

    ('gauss_int_seq_Int64', 'Int64', gen_int_gauss()),
    ('gauss_int_seq_Int32', 'Int32', gen_int_gauss()),
    ('gauss_float_seq_Float64', 'Float64', gen_gauss()),
    ('gauss_float_seq_Float32', 'Float', gen_gauss()),

]

csv_int_generator = (f'csv_{config.CSV_DATATYPE}', f'{config.CSV_DATATYPE}', csv_generator('INT'))
csv_float_generator = (f'csv_{config.CSV_DATATYPE}', f'{config.CSV_DATATYPE}', csv_generator('FLOAT'))


class ColumnValue(TypedDict):
    name: str
    type: str
    codec: str
    is_raw: bool
    generator_value: Iterator


def get_list_of_generators() -> (List[ColumnValue]):
    _list_of_generators = list_of_generators
    gen_list = []
    if config.ONLY_CSV:
        _list_of_generators = []
    if 'int' in config.CSV_DATATYPE.lower():
        _list_of_generators.append(csv_int_generator)
    elif 'float' in config.CSV_DATATYPE.lower():
        _list_of_generators.append(csv_float_generator)
    for i in _list_of_generators:
        name = i[0]
        type_column = i[1]
        gen = i[2]
        for codec_name, codec_column, is_raw in CODEC_LIST:
            if 'Float' in type_column and codec_name == 'T64':
                continue
            if 'Float' not in type_column and codec_name == 'FPC':
                continue
            gen_list.append(ColumnValue(
                name=f'{name}_{codec_name}',
                type=type_column,
                codec=codec_column,
                is_raw=is_raw,
                generator_value=iter(gen)

            ))

    return gen_list
