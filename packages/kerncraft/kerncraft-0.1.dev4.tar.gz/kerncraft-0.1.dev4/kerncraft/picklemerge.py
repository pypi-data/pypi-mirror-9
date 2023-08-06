#!/usr/bin/env python

from __future__ import print_function

import argparse
import ast
import sys
import os.path
import pickle
import collections


def update(d, u):
    '''
    Updated dictionary recursivly
    Origin:
    http://stackoverflow.com/a/3233356/2754040
    '''
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def main():
    parser = argparse.ArgumentParser(
        description='Recursively merges two or more pickle files. Only supports pickles consisting '
        'of a single dictionary object.')
    parser.add_argument('destination', type=argparse.FileType('r+'),
                        help='File to write to and include in resulting pickle. (WILL BE CHANGED)')
    parser.add_argument('source', type=argparse.FileType('r'), nargs='+',
                        help='File to include in resulting pickle.')

    args = parser.parse_args()

    result = pickle.load(args.destination)
    assert isinstance(result, collections.Mapping), "only Mapping types can be handled."
    
    for s in args.source:
        data = pickle.load(s)
        assert isinstance(data, collections.Mapping), "only Mapping types can be handled."
        
        
        update(result, data)
    
    args.destination.seek(0)
    args.destination.truncate()
    pickle.dump(result, args.destination)


if __name__ == '__main__':
    main()