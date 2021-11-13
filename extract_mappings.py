
'''
File to extract mappings from a 'training' dataset of infoboxes where we have
both Dutch and English available.
'''

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Optional, Set, Union

from unidecode import unidecode

from utils import *

from collections import defaultdict, Counter


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
        # TODO: maybe also add reason to this, but that could also introduce
        # unwanted duplicates -> test
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

    def translate(self, en_key: str, allow_fuzzy=False) -> Optional[List[str]]:
        if en_key not in self.map:
            return None

        # NOTE: we moeten goed opletten of we met een genormaliseerde of de
        # 'originele' key werken. Ik zit er aan te denk om de norm variant aan
        # de mapping toe te voegen, maar dat wordt misschien wat
        # onoverzichtelijk
        results = []
        for mapping in self.map[en_key]:
            option = mapping.translate(en_key, allow_fuzzy)
            if option:
                results.append(option)
        return results

    def get_mappings(self, en_key: str) -> Optional[List[Mapping]]:
        if en_key not in self.map:
            return None

        return list(self.map[en_key])

    def has_key(self, en_key: str) -> bool:
        return en_key in self.map.keys()


def normalize_str(string: str) -> str:
    # Do the basic cleaning of possibly noisy Wikipedia specific stuff
    string = clean_str(string)
    # Next try ascii folding to account for localization differences
    string = unidecode(string)

    # possible other options?

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

            for en_k, en_v in en_infoboxes[key].items():
                en_k_norm = normalize_str(en_k)

                if nl_k_norm == en_k_norm:
                    reason = 'Exact key match'
                elif nl_v == en_v:
                    reason = 'Exact value match'
                # De resultaten van deze zijn matig tot zeer poep, staat daarom
                # voor nu even uit
                # elif (nl_v in en_v) or (en_v in nl_v):
                #     reason = 'Partial value match'
                # We can add more strategies to extract mappings here, for instance:
                #   - string distance metrics (Levenstein, gap distance etc.)
                #   - translated value is (roughly) the same
                #   - ...
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
