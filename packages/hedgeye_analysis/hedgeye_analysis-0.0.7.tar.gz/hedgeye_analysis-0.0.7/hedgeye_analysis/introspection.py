from dill.source import getsource

def print_source(whatever):
    print(getsource(whatever))
    return whatever
