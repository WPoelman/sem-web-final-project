
#!/usr/bin/env python

"""
Filename:   extract_mappings.py
Date:       14-11-2021
Authors:    Frank van den Berg, Esther Ploeger, Wessel Poelman
Description:
    A program that extracts mappings from a 'training' dataset of infoboxes
    where both Dutch and English infoboxes available for the same subject.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import List, Optional

import Levenshtein
from unidecode import unidecode

from utils import *


@dataclass
class Mapping:
    en_key: str
    nl_key: str
    train_count: int = 0  # How many times this mapping is seen in training
    reason: str = None  # Explanation of how this mapping came to be

    def translate(self, en_key: str, allow_fuzzy=True) -> str:
        if en_key == self.en_key:
            return self.nl_key

        if allow_fuzzy and ((self.en_key in en_key) or (en_key in self.en_key)):
            return self.nl_key

        return None

    def set_counter(self, count: int) -> Mapping:
        self.train_count = count
        return self

    def __hash__(self):
        return hash((self.en_key, self.nl_key))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.en_key == other.en_key and self.nl_key == other.nl_key


class Mapper:
    def __init__(self, mappings: List[Mapping]) -> None:
        self.map = self.__create_map(mappings)

    @staticmethod
    def __create_map(mappings):
        map = defaultdict(set)
        # First add all mappings we know
        for map1 in mappings:
            map[map1.en_key].add(map1)

        # Next try to group mappings based on their English key
        for map1 in mappings[1:]:
            for map2 in mappings[:-1]:
                # Group the keys so we have access to similar alternative keys.
                # NOTE: this is very dependent on training data!!!
                if map1.en_key == map2.en_key:
                    # We have to add both since we have no idea which key we
                    # will encounter first during translation. A graph-like
                    # structure is more suitable here (we have pairs of edges),
                    # but this did not work out that well.
                    map[map1.en_key].update([map1, map2])
                    map[map2.en_key].update([map1, map2])

        return map

    @staticmethod
    def __most_frequent(mappings: List[Mapping]) -> List[Mapping]:
        return sorted(mappings, key=lambda x: x.train_count, reverse=True)

    def translate(
        self,
        en_key: str,
        allow_fuzzy=False,
        rank_strategy='most_frequent'
    ) -> Optional[List[str]]:
        if en_key not in self.map:
            return None

        # NOTE: be careful if you are using a normalized key or not
        mapping_options = self.map[en_key]

        if rank_strategy == 'most_frequent':
            mapping_options = self.__most_frequent(mapping_options)

        results = []
        for mapping in mapping_options:
            option = mapping.translate(en_key, allow_fuzzy)
            if option:
                results.append(option)
        return results

    def get_mappings(
        self,
        en_key: str,
        rank_strategy='most_frequent'
    ) -> Optional[List[Mapping]]:
        if en_key not in self.map:
            return None

        mappings = list(self.map[en_key])

        if rank_strategy == 'most_frequent':
            mappings = self.__most_frequent(mappings)

        return mappings

    def has_key(self, en_key: str) -> bool:
        return en_key in self.map.keys()


def normalize_str(string: str) -> str:
    # Do the basic cleaning of possibly noisy Wikipedia specific stuff
    string = clean_str(string)
    # Next try ascii folding to account for localization differences
    string = unidecode(string)

    return string


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--en_path",
                        default='data/train/en_infoboxes_clean.pickle',
                        type=str,
                        help="Path to cleaned English infoboxes train set")
    parser.add_argument("-n", "--nl_path",
                        default='data/train/nl_infoboxes_clean.pickle',
                        type=str,
                        help="Path to cleaned Dutch infoboxes train set")
    parser.add_argument("-t", "--threshold",
                        default=0.8,
                        type=float,
                        help=("Levenshtein similarity ratio threshold for "
                              "infobox values, bigger or equal to the "
                              "threshold counts as a match)"))
    args = parser.parse_args()
    return args


def main():
    args = create_arg_parser()
    en_infoboxes = load_pickle(args.en_path)
    nl_infoboxes = load_pickle(args.nl_path)

    # This makes sure we always have both boxes available, might put a warning
    # here later if we want to work with 'exact' training sets...
    both_available = en_infoboxes.keys() & nl_infoboxes.keys()

    # Expect normalized en_keys as the original keys here
    mappings = Counter()

    for key in both_available:
        for nl_k, nl_v in nl_infoboxes[key].items():
            nl_k_norm = normalize_str(nl_k)
            nl_v_norm = normalize_str(nl_v)

            for en_k, en_v in en_infoboxes[key].items():
                en_k_norm = normalize_str(en_k)
                en_v_norm = normalize_str(en_v)

                if nl_k == en_k:
                    reason = 'Exact key match'
                elif nl_k_norm == en_k_norm:
                    reason = 'Normalized key match'
                elif nl_v == en_v:
                    reason = 'Exact value match'
                elif nl_v_norm == en_v_norm:
                    reason = 'Normalized value match'
                elif Levenshtein.ratio(nl_v_norm, en_v_norm) >= args.threshold:
                    reason = 'Normalized value Levenshtein match'
                else:
                    reason = None

                if reason:
                    mappings.update([Mapping(en_k, nl_k, reason=reason)])

    mappings = [m.set_counter(count) for m, count in mappings.items()]
    mapper = Mapper(mappings)

    with open('data/mappings.pickle', 'wb') as f:
        pickle.dump(mappings, f)

    with open('data/mapper.pickle', 'wb') as f:
        pickle.dump(mapper, f)


if __name__ == '__main__':
    main()
