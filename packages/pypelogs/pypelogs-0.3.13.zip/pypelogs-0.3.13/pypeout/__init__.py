from .json_out import JSONOut
from .mongodb import MongoDBOut
from .mysql_out import MySQLOut
from .csv_out import CSVOut
from .sql_out import SQLOut
from .text_out import TextOut
from .http import HTTP

CLASSES = {
    'csv': CSVOut,
    'json': JSONOut,
    'mongodb': MongoDBOut,
    'mysql' : MySQLOut,
    'sql': SQLOut,
    'text': TextOut,
    'http': HTTP
}


def output_for(s):
    spec_args = s.split(':', 1)
    clz = CLASSES.get(spec_args[0])
    if not clz:
        raise NoSuchOutputException(spec_args[0])
    return clz() if len(spec_args) == 1 else clz(spec_args[1])


def register(s, clz):
    CLASSES[s] = clz


class NoSuchOutputException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)