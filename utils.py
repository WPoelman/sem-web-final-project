#!/usr/bin/env python

"""
Utility functions
"""

import re
import pickle

WHITESPACE_PATTERN = re.compile(r'\W+')
TAG_PATTERN = re.compile(r'<[^>]+>')
TRANSLATION = str.maketrans({'[': ' ', ']': ' ', '{': ' ', '}': ' ', '|': ' '})

def load_dict_pickle(filename):
    with open(filename, 'rb') as handle:
        dict = pickle.load(handle)
    return dict

def clean_str(string):
    # remove brackets
    string = string.translate(TRANSLATION)
    # remove html tags
    string = re.sub(TAG_PATTERN, ' ', string)
    # Collapse whitespace
    string = re.sub(WHITESPACE_PATTERN, ' ', string)
    return string.strip()


def unpack_iterables(item):
    if type(item) in (int, float):
        return item
    elif type(item) == str:
        return clean_str(item)
    elif len(item) > 0 and all(type(a) not in (list, tuple, set) for a in item):
        return item

    return unpack_iterables(item[0])


def clean_ib_dict(ib_dict):
    """Takes an infobox dicionary as input, cleans all the
     values and returns the cleaned infobox dictionary"""
    cleaned_dict = dict()
    for k, v in ib_dict.items():
        cleaned_dict[k] = unpack_iterables(v)
    return cleaned_dict
