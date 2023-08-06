#!/usr/bin/env python3
from itertools import islice, chain


def chunk(iterable, chunk_size, pad_chunk=False, fill_value=None):
    """ Split an iterable into equal size chunks """
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, chunk_size))
        if len(chunk) != chunk_size:
            if pad_chunk:
                yield tuple(chain(chunk, (fill_value,) * (chunk_size - len(chunk))))
            raise StopIteration('Done')
        yield chunk
