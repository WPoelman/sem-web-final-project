#!/usr/bin/env python

"""
Filename:   utils.py
Date:       14-11-2021
Authors:    Frank van den Berg, Esther Ploeger, Wessel Poelman
Description:
    Utility functions used in various places.
"""

import contextlib
import io
import json
import pickle
import re
from typing import Any, Dict, Optional

import requests
import wptools
from deep_translator import GoogleTranslator

WHITESPACE_PATTERN = re.compile(r'\W+')
TAG_PATTERN = re.compile(r'<[^>]+>')
TRANSLATION = str.maketrans({'[': ' ', ']': ' ', '{': ' ', '}': ' ', '|': ' '})

InfoBox = Dict[str, Any]


def load_pickle(filename: str) -> Any:
    with open(filename, 'rb') as handle:
        dict = pickle.load(handle)
    return dict


def clean_str(string: str) -> str:
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
    elif (len(item) > 0 and
            all(type(a) not in (list, tuple, set) for a in item)):
        return item

    return unpack_iterables(item[0])


def clean_ib_dict(ib_dict: InfoBox) -> InfoBox:
    """Takes an infobox dicionary as input, cleans all the
     values and returns the cleaned infobox dictionary"""
    cleaned_dict = dict()
    for k, v in ib_dict.items():
        cleaned_dict[k] = unpack_iterables(v)
    return cleaned_dict


def get_dutch_title(en_title: str) -> str:
    """Use the English title of a Wikipedia page to get the Dutch title"""
    try:
        URL = "https://en.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "query",
            "titles": en_title,
            "prop": "langlinks",
            "lllang": "nl",
            "format": "json"
        }

        results = requests.get(url=URL, params=PARAMS).json()
        pages = [p for p in results['query']['pages']]
        for p in pages:  # There is probably only one page
            dutch_title = results['query']['pages'][p]['langlinks'][0]['*']
    except:
        # Return the English title instead
        return en_title

    return dutch_title


def get_infobox(title: str, language: str = 'en') -> Optional[InfoBox]:
    """Use the title of a Wikipedia page to get the infobox"""
    # For some reason this library prints a lot of garbage even though we tell
    # it three (!) times to be quiet. This is a known problem:
    # https://github.com/siznax/wptools/issues/167
    # https://github.com/siznax/wptools/issues/158
    # That is why we silence stderr and stdout alltogether.

    with contextlib.redirect_stderr(io.StringIO()), \
            contextlib.redirect_stdout(io.StringIO()):
        try:
            page = wptools.page(title,
                                lang=language,
                                silent=True,
                                verbose=False).get_parse(show=False)
            infobox = page.data['infobox']
        except:
            infobox = None

    return infobox


def rnd(n: float, ndigits: int = 3) -> float:
    ''' Helper for consistent rounding'''
    return round(n, ndigits)


def translate(value: str, source: str = 'en', target: str = 'nl') -> str:
    """Translate from the source to the target language"""
    try:
        translated_val = GoogleTranslator(source=source,
                                          target=target).translate(value)
    except:
        return value
    return translated_val


def format_dict_str(dictionary: dict) -> str:
    ''' Formats a dict as a readable json string'''
    return json.dumps(dictionary, indent=4)
