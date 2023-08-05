#!/usr/bin/env python
import argparse
import re
import sys
from phantasm import Cassettes, Utils
import logging
logging.basicConfig(level=logging.INFO)

def compare_values(a, b, method, undef_value):
    if method not in ('phantasm_cids',):
        a = float(a)
        b = float(b)

    if method == 'add':
        return a + b
    elif method == 'sub':
        return a - b
    elif method == 'mult':
        return a * b
    elif method == 'div':
        if b == 0:
            return undef_value
        else:
            return a / b
    elif method == 'dist':
        return abs(a - b)
    elif method == 'pdiff':
        return abs(a-b)/(a+b)
    elif method == 'bit_diff':
        a = abs(int(a))
        b = abs(int(b))

        return bin(a^b).count("1")
    elif method == 'phantasm_cids':
        chunked = Cassettes.revcomrot(a)
        # Compare each for levenshtein distance, return the minimum
        scores = [abs(Levenshtein.distance(x, b)) for x in chunked]
        return min(scores)
    else:
        raise NotImplementedError("Comparison method %s not available" % undef_value)
    return None

def compare_files(file_a, file_b, comparison_method, undef_value, **kwargs):

    (header_a, data_a) =  Cassettes.load_data_with_headers(file_a)
    (header_b, data_b) =  Cassettes.load_data_with_headers(file_b)

    header = ['# ID_A', 'ID_B', 'Value']
    yield header

    for row_a in data_a:
        for row_b in data_b:
            yield (row_a[0], row_b[0],
                   compare_values(row_a[1], row_b[1], comparison_method, undef_value))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate comparisons between two PHAnTASM datasets')
    parser.add_argument('file_a', type=file, help='First Tabular Dataset')
    parser.add_argument('file_b', type=file, help='Second Tabular Dataset')
    choices = ['pdiff', 'bit_diff', 'add', 'sub', 'mult', 'div', 'dist', 'phantasm_cids']
    parser.add_argument('comparison_method', choices=choices,
                        help='Method for comparison')
    parser.add_argument('undef_value', nargs='?', type=float, default=0,
                        help='Undefined value. For operations involving division, what should undefined results be set to? (e.g. 3/0 = ?).')
    parser.add_argument('--version', action='version', version='0.1')
    args = parser.parse_args()


    result_iter = iter(compare_files(**vars(args)))
    try:
        while True:
            print '\t'.join(map(str, result_iter.next()))
    except StopIteration:
        pass
