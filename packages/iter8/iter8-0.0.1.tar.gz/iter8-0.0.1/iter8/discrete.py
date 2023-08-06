import itertools


def discrete(seq, n):
    '''
    take consecutive n-long of items from iterable
    '''
    iterable = iter(seq)
    while True:
        group = list(itertools.islice(iterable, n))
        if len(group) > 0:
            yield group
        if len(group) < n:
            break
