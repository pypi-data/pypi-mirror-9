
from types import FileType


COMMA = ','
NEWLINE = '\n'
COMMA_JOIN = "{0},{1}"
WRITEABLE = 'w'


def coroutine(func):
    """
    A decorator to start coroutines

    :param:
    
     - `func`: A coroutine function.
    """
    def wrap(*args, **kwargs):
        coroutine_func = func(*args, **kwargs)
        coroutine_func.next()
        return coroutine_func
    return wrap


@coroutine
def broadcast(targets):
    """
    A coroutine to broadcast input.
    
    :param:

     - `targets`: A list of coroutines to send output to.
    """
    while True:
        line = (yield)
        for target in targets:
            target.send(line)
    return


@coroutine
def comma_join(target, input_count):
    """
    This outputs the data in the opposite order that it's received.
    This way the source of the data pipeline is output first.
    
    :param:

     - `target`: A coroutine to send output to.
     - `input_count`: number of inputs before creating line to send.
    """
    inputs = range(input_count)
    while True:
        line = COMMA.join(reversed([(yield) for source in inputs]))
        target.send(line)
    return


@coroutine
def output(target_file):    
    """
    Writes input to the target file
    
    :param:

     - `target_file`: A file-like object to write output to.
    """
    while True:
        line = (yield)
        if not line.endswith(NEWLINE):
            line += NEWLINE
        target_file.write(line)
    return


@coroutine
def comma_append(source, target):
    """
    Joins a source stream output and incoming strings with commas

    :param:

     - `source`: iterable of strings
     - `target`: target to send joined strings
    """
    for line in source:
        line_2 = (yield)
        target.send(COMMA_JOIN.format(line.rstrip(NEWLINE), line_2))
    return


@coroutine
def file_output(file_object):
    """
    Writes strings to a file, making sure there's a newline at the end

    :param:

     - `file_object`: opened, writable file or name of file to open
    """
    if not type(file_object) is FileType:
        file_object = open(file_object, WRITEABLE)
    while True:
        line = (yield)
        line = line.rstrip(NEWLINE) + NEWLINE
        file_object.write(line)
