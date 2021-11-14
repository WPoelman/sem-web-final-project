#!/usr/bin/env python

"""
Filename:   demo.py
Date:       14-11-2021
Authors:    Frank van den Berg, Esther Ploeger, Wessel Poelman
Description:
    A program that retrieves an English infobox from a given Wikipedia page
    title, then it either expands the existing Dutch infobox or creates a new
    Dutch infobox.
"""

import argparse
import json
import sys

from extract_mappings import Mapper, Mapping
from specific_cases import *
from utils import *


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",
                        "--title",
                        default='The Very Hungry Caterpillar',
                        type=str,
                        help=("Title of the English wikipedia page (default: "
                              " 'The Very Hungry Caterpillar')"))
    parser.add_argument("-m",
                        "--mapper",
                        default='data/mapper.pickle',
                        type=str,
                        help="Path to a trained mapper object.")
    args = parser.parse_args()
    return args


def evaluate(true_infobox, gen_infobox, chosen_top3):
    item_count_true = len(true_infobox.keys())
    item_count_gen = len(gen_infobox.keys())

    correct_k = len(true_infobox.keys() & gen_infobox.keys())
    correct_v = len(set(true_infobox.values()) & set(gen_infobox.values()))

    pairs_true = {(k, v) for k, v in true_infobox.items()}
    pairs_gen = {(k, v) for k, v in gen_infobox.items()}

    correct_pairs = len(pairs_gen & pairs_true)

    frac_correct_k = rnd(correct_k / item_count_gen)
    frac_correct_v = rnd(correct_v / item_count_gen)
    frac_correct_pairs = rnd(correct_pairs / len(pairs_gen))

    close_keys = []
    for k, v in true_infobox.items():
        for k1, v1 in chosen_top3.items():
            if k != k1 and k in v1:
                # We don't have the correct key, but it is in the top 3.
                # This does include some overlap, but that gives us more
                # insight into the generally wrong/close keys we have.
                close_keys.append(
                    f'Actual: {(k, v)} predicted: {k1} options: {v1}'
                )

    close_keys_results = '\n'.join(close_keys)

    print(f'''
    --- true infobox ---
    {json.dumps(true_infobox, indent=4)}

    --- generated infobox ---
    {json.dumps(gen_infobox, indent=4)}

    --- stats ---
    items in true infobox:      {item_count_true}
    items in genreated infobox: {item_count_gen}

    --- exact matches ---
    correct keys:          {frac_correct_k} ({correct_k} / {item_count_gen})
    correct values:        {frac_correct_v} ({correct_v} / {item_count_gen})
    correct key AND value: {frac_correct_pairs} ({correct_pairs} / {item_count_gen})

    --- wrong key but in top 3 ---
    {close_keys_results}
    ''')


def main():
    args = create_arg_parser()

    mapper: Mapper = load_pickle(args.mapper)

    # Get EN title and retrieve English wikipedia infobox
    en_title = args.title
    en_infobox = get_infobox(en_title)

    # If there is no EN infobox, we stop here, else we try to get
    # the NL infobox as well
    if not en_infobox:
        print("There is no infobox available for this Wikipedia page, "
              "please try another title.", file=sys.stderr)
        exit(1)

    # Get NL title and retrieve Dutch wikipedia infobox
    nl_title = get_dutch_title(en_title)
    nl_infobox = get_infobox(nl_title, 'nl')
    if nl_infobox:
        nl_infobox_clean = clean_ib_dict(nl_infobox)

    # Clean the English infobox
    en_infobox_clean = clean_ib_dict(en_infobox)

    # We try to generate the NL infobox
    nl_new_infobox = dict()
    chosen_keypairs = dict()  # Here we store which EN and NL keys we picked
    chosen_top3 = dict()

    for en_key in en_infobox_clean:
        nl_key_options = mapper.translate(en_key, allow_fuzzy=False)

        if nl_key_options:
            nl_key = nl_key_options[0]
            nl_new_infobox[nl_key] = en_infobox_clean[en_key]
            chosen_keypairs[en_key] = nl_key
            chosen_top3[nl_key] = nl_key_options[:3]
        # If the label is not in our mapping, simply translate the English
        # label to a Dutch label
        else:
            nl_key = translate(en_key)
            if nl_key not in nl_new_infobox:
                # TODO: decide whether we want to just use the same value
                # in this case
                nl_new_infobox[nl_key] = en_infobox_clean[en_key]
                chosen_keypairs[en_key] = nl_key

    # We update the dictionary by handling specific cases for generating labels
    nl_new_infobox = handle_specific_cases(en_infobox_clean,
                                           nl_new_infobox,
                                           chosen_keypairs,
                                           en_title,
                                           nl_title)

    # TODO: this is disabled for the moment since we don't have a way of
    # validating the process of adding to an existing box yet
    # Finally, if there is an existing NL infobox, we first use those
    # key-value pairs and add only the missing ones from our generated
    # infobox to it.
    # if nl_infobox:
    #     cleaned_nl = clean_ib_dict(nl_infobox)
    #     for key in nl_new_infobox:
    #         if key not in cleaned_nl:
    #             cleaned_nl[key] = nl_new_infobox[key]
    # else:
    #     cleaned_nl = nl_new_infobox

    if nl_infobox_clean:
        evaluate(nl_infobox_clean, nl_new_infobox, chosen_top3)
    else:
        print(
            f'Cannot evaluate {en_title} since there is no Dutch infobox')

    # The combination of the existing infobox with our own infobox
    # print(cleaned_nl)
    # print(nl_new_infobox)  # Our self created infobox so far


if __name__ == "__main__":
    main()
