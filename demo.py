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
import concurrent.futures
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
    parser.add_argument("-ts",
                        "--titles",
                        type=str,
                        help="List of titles to evaluate")
    parser.add_argument("-m",
                        "--mapper",
                        default='data/mapper.pickle',
                        type=str,
                        help="Path to a trained mapper object.")
    parser.add_argument("-w", "--max_workers", default=32,
                        help="Max concurrent workers used to create the infoboxes.")
    args = parser.parse_args()
    return args


def evaluate_infobox(true_infobox, gen_infobox, chosen_top3):
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

    report = f'''
    --- true infobox ---
    {format_dict_str(true_infobox)}

    --- generated infobox ---
    {format_dict_str(gen_infobox)}

    --- stats ---
    items in true infobox:      {item_count_true}
    items in genreated infobox: {item_count_gen}

    --- exact matches ---
    correct keys:          {frac_correct_k} ({correct_k} / {item_count_gen})
    correct values:        {frac_correct_v} ({correct_v} / {item_count_gen})
    correct key AND value: {frac_correct_pairs} ({correct_pairs} / {item_count_gen})

    --- wrong key but in top 3 ---
    {close_keys_results}
    '''

    return report


class InfoBoxGenerator:
    def __init__(self, mapper: Mapper, output_folder='data/reports/') -> None:
        self.mapper = mapper
        self.output_folder = output_folder

    def generate_infobox(
        self,
        en_title,
        expand_existing=False,
        evaluate=True,
        verbose=False
    ):
        ''' Creates a Dutch infobox for a given English Wikipedia article title.

            expand_existing:    When an existing Dutch infobox is found, controls
                                wether or not to expand that one, or to leave it
                                as is.

            evaluate:           Controls wether to create an evaluation report or
                                not. These reports are stored in data/reports
                                and have the English article name as filename.

            verbose:            Print evaluation output as it is created.

        '''
        # Get EN title and retrieve English wikipedia infobox
        en_infobox = get_infobox(en_title)

        # If there is no EN infobox, we stop here, else we try to get
        # the NL infobox as well
        if not en_infobox:
            print(
                f"There is no English infobox available for {en_title}, skipping.",
                file=sys.stderr
            )
            return None

        # Get NL title and retrieve Dutch wikipedia infobox
        nl_title = get_dutch_title(en_title)
        nl_infobox = get_infobox(nl_title, 'nl')
        if nl_infobox:
            nl_infobox_clean = clean_ib_dict(nl_infobox)
        else:
            nl_infobox_clean = None

        # Clean the English infobox
        en_infobox_clean = clean_ib_dict(en_infobox)

        # We try to generate the NL infobox
        nl_new_infobox = dict()
        chosen_keypairs = dict()  # Here we store which EN and NL keys we picked
        chosen_top3 = dict()

        for en_key in en_infobox_clean:
            nl_key_options = self.mapper.translate(en_key, allow_fuzzy=False)

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

        if evaluate and nl_infobox_clean:
            report = evaluate_infobox(
                nl_infobox_clean,
                nl_new_infobox,
                chosen_top3
            )
        else:
            report = f'Cannot evaluate {en_title} since there is no Dutch infobox'

        # Finally, if there is an existing NL infobox, we first use those
        # key-value pairs and add only the missing ones from our generated
        # infobox to it.
        if expand_existing and nl_infobox_clean:
            expanded = nl_infobox_clean
            for key in nl_new_infobox:
                if key not in expanded:
                    expanded[key] = nl_new_infobox[key]
        else:
            expanded = None

        if evaluate:
            with open(f'{self.output_folder}{en_title}.txt', 'w') as f:
                f.write(report)

            if verbose:
                print(report)

        if expanded:
            with open(f'{self.output_folder}{en_title}_expanded.txt', 'w') as f:
                f.write(
                    f'Original: \n{format_dict_str(nl_infobox)}\n'
                    f'------------------------------------------\n'
                    f'Expanded: \n{format_dict_str(expanded) }'
                )


def main():
    args = create_arg_parser()

    mapper: Mapper = load_pickle(args.mapper)

    generator = InfoBoxGenerator(mapper)

    if args.title:
        generator.generate_infobox(args.title)

    if args.titles:
        with open(args.titles, 'r') as f:
            titles = [t.strip() for t in f]

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = [
            executor.submit(generator.generate_infobox, title)
            for title in titles
        ]
        for _ in concurrent.futures.as_completed(futures):
            pass


if __name__ == "__main__":
    main()
