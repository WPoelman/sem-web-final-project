#!/usr/bin/env python

"""
"""

import argparse
from utils import *

def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--titles_file", default='data/titles.txt',
                        help="Input txt file containing book titles on each line")
    parser.add_argument("-ep", "--en_pickle", default='data/en_infoboxes.pickle',
                        help="Input pickle dictionary containing English infoboxes")
    parser.add_argument("-np", "--nl_pickle", default='data/nl_infoboxes.pickle',
                        help="Input pickle dictionary containing Dutch infoboxes")

    args = parser.parse_args()
    return args



def get_key(val, dict):
    for key, value in dict.items():
        if val == value:
            return key

    return False

if __name__ == "__main__":
    args = create_arg_parser()

    # Open english and dutch infobox dictionaries:
    nl_infoboxes = load_pickle(args.nl_pickle)  # 556 out of 2908 are actually infoboxes, other say "NA"
    en_infoboxes = load_pickle(args.en_pickle)  # 2908 infoboxes

    # Print example of how key value pair looks:
    first_title = list(en_infoboxes.keys())[0]
    print("key:\n{} \nvalue:\n{}".format(first_title, en_infoboxes[first_title]))

    # For every title, check whether both dictionary contain the infobox:
    all_titles = list(en_infoboxes.keys())
    for title in all_titles:
        if nl_infoboxes[title] != "NA":  # Then both dictionaries contain an infobox
            # Now we check whether there are values that are the same in both infoboxes
            en_ib = en_infoboxes[title]
            nl_ib = nl_infoboxes[title]
            for en_key, en_val in en_ib.items():
                nl_key = get_key(en_val, nl_infoboxes[title])
                # UNCOMMENT DEZE TWEE LINES OM TE ZIEN WELKE ENGELSE EN NL KEYS DEZELFDE WAARDE DELEN:
                #if nl_key:
                #    print(en_key, nl_key)

            # Idea: count how many times these keys have the same values
            # and also try how many times these keys do not have the same value  (If 'author' in EN  and 'auteur' in NL: are values the same?)




