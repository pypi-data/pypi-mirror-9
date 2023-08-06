#!/usr/bin/env python3
import unittest
from chunk import chunk


class TestChunk(unittest.TestCase):
    def test_chunk_optimal_case(self):
        """ Test turning an iterable into chunks """
        items = [1,2,3,4,5,6,7,8,9,10]
        self.assertEqual(
            list(chunk(items, chunk_size=2)),
            [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)])
        self.assertEqual(
            list(chunk(items, chunk_size=5)),
            [(1, 2, 3, 4, 5), (6, 7, 8, 9, 10)])

    def test_dropping_last_chunk(self):
        """ Test that chunk will drop the last incomplete chunk """
        items = (1,2,3,4,5,6,7,8,9,10)
        self.assertEqual(
            list(chunk(items, chunk_size=3)),
            [(1, 2, 3), (4, 5, 6), (7, 8, 9)])
        self.assertEqual(
            list(chunk(items, chunk_size=4)),
            [(1, 2, 3, 4), (5, 6, 7, 8)])

    def test_padding_last_chunk(self):
        """ Test that chunk can pad the last incomplete chunk """
        items = '1234567890'
        self.assertEqual(
            list(chunk(items, chunk_size=3, pad_chunk=True)),
            [('1', '2', '3'), ('4', '5', '6'), ('7', '8', '9'), ('0', None, None)])
        self.assertEqual(
            list(chunk(items, chunk_size=4, pad_chunk=True)),
            [('1', '2', '3', '4'), ('5', '6', '7', '8'), ('9', '0', None, None)])

    def test_fill_padding_last_chunk(self):
        """ Test that chunk can pad the last incomplete chunk with a default value """
        fill_value = 'something'
        items = dict(zip([1,2,3,4,5,6,7,8,9,10], [None]*10))
        self.assertEqual(
            list(chunk(items, chunk_size=3, pad_chunk=True, fill_value=fill_value)),
            [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, fill_value, fill_value)])
        self.assertEqual(
            list(chunk(items, chunk_size=4, pad_chunk=True, fill_value=fill_value)),
            [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, fill_value, fill_value)])


if __name__ == '__main__':
    unittest.main()
