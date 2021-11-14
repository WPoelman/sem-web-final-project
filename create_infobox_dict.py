#!/usr/bin/env python

"""
Filename:   create_infobox_dict.py
Date:       14-11-2021
Authors:    Frank van den Berg, Esther Ploeger, Wessel Poelman
Description:
    A program that creates a dataset of English and Dutch infoboxes from a 
    given list of Wikipedia titles.
"""

import argparse
import concurrent.futures
import pickle
from typing import Any, Dict

from utils import *


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--titles_file", default='data/train/titles.txt',
                        help="Input txt file containing book titles on each line.")
    parser.add_argument("-w", "--max_workers", default=32,
                        help="Max concurrent workers used to fetch the infoboxes.")

    args = parser.parse_args()
    return args


def get_data(en_title: str):
    en_infobox = get_infobox(en_title)
    nl_title = get_dutch_title(en_title)
    nl_infobox = get_infobox(nl_title, 'nl')
    return en_title, en_infobox, nl_title, nl_infobox


def create_dict_pickle(dict: Dict[Any, Any], filename: str):
    with open(filename, 'wb') as handle:
        pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


def main():
    args = create_arg_parser()

    # Get list of wikipedia page titles from txt file:
    with open(args.titles_file, 'r') as f:
        titles = [line.strip() for line in f]

    # Create {title: infobox} dictionary
    en_infoboxes = dict()
    nl_infoboxes = dict()

    # List to store titles that actually contain both EN and NL infoboxes
    both_infoboxes_titles = []
    only_en = 0

    print(f'Fetching {len(titles)} titles with {args.max_workers} workers...')

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = [executor.submit(get_data, title) for title in titles]
        all_data = [
            r.result()
            for r in concurrent.futures.as_completed(futures)
        ]

    for en_title, en_infobox, nl_title, nl_infobox in all_data:
        if en_infobox:
            en_infoboxes[en_title] = en_infobox
            if nl_infobox:
                nl_infoboxes[en_title] = nl_infobox
                both_infoboxes_titles.append(en_title)
            else:
                nl_infoboxes[en_title] = None
                only_en += 1

    # Write full dictionary to pickle file:
    create_dict_pickle(en_infoboxes, 'all_en_infoboxes.pickle')
    create_dict_pickle(nl_infoboxes, 'all_nl_infoboxes.pickle')

    print("Number of titles: ", len(titles))
    print("Number of titles containing only EN infoboxes: ", only_en)
    print("Number of titles containing both infoboxes: ",
          len(both_infoboxes_titles))


if __name__ == "__main__":
    main()
