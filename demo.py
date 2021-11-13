#!/usr/bin/env python

"""
A program to retrieve the English infobox from a given Wikipedia page title,
then either expand the existing Dutch infobox or create a new Dutch infobox.
"""

import argparse
import wptools
import requests
import sys
from utils import *
from specific_cases import *
from deep_translator import GoogleTranslator
from extract_mappings import Mapping, Mapper


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


def get_dutch_title(en_title):
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


def get_infobox(title, language='en'):
    """Use the title of a Wikipedia page to get the infobox"""
    try:
        page = wptools.page(title, lang=language,
                            silent=True, verbose=False).get_parse(show=False)
        infobox = page.data['infobox']
    except:
        infobox = False

    return infobox


def translate(value, source='en', target='nl'):
    """Translate from the source to the target language"""
    try:
        translated_val = GoogleTranslator(
            source=source, target=target).translate(value)
    except:
        return value
    return translated_val


if __name__ == "__main__":
    args = create_arg_parser()

    mapper: Mapper = load_pickle(args.mapper)

    # Get EN title and retrieve English wikipedia infobox
    en_title = args.title
    en_infobox = get_infobox(en_title)

    # If there is no EN infobox, we stop here, else we try to get the NL infobox as well
    if not en_infobox:
        print("There is no infobox available for this Wikipedia page, "
              "please try another title.", file=sys.stderr)
        exit(1)

    # Get NL title and retrieve Dutch wikipedia infobox
    nl_title = get_dutch_title(en_title)
    nl_infobox = get_infobox(nl_title, 'nl')

    # Clean the English infobox
    cleaned_en = clean_ib_dict(en_infobox)

    # todo: various steps of filling the new infobox
    # We try to generate the NL infobox
    new_infobox = dict()
    chosen_keypairs = dict()  # Here we store which EN and NL keys we picked
    for en_key in cleaned_en:
        # TODO: test if we want fuzzy here or not
        nl_key_options = mapper.translate(en_key)

        if nl_key_options:
            # TODO: find a way to rank these and pick the best one
            # (key co-occurrence maybe? On both the Dutch and English
            # training sets?)
            nl_key = nl_key_options[0]
            new_infobox[nl_key] = cleaned_en[en_key]
            chosen_keypairs[en_key] = nl_key
        # If the label is not in our mapping, simply translate the English label to a Dutch label
        else:
            nl_key = translate(en_key)
            if nl_key not in new_infobox:
                # todo: decide whether we want to just use the same value in this case
                new_infobox[nl_key] = cleaned_en[en_key]
                chosen_keypairs[en_key] = nl_key

    # We update the dictionary by handling specific cases for generating labels
    new_infobox = handle_specific_cases(cleaned_en, new_infobox, chosen_keypairs, en_title, nl_title)

    # Finally, if there is an existing NL infobox, we first use those key-value pairs and add only
    # the missing ones from our generated infobox to it.
    if nl_infobox:
        cleaned_nl = clean_ib_dict(nl_infobox)
        for key in new_infobox:
            if key not in cleaned_nl:
                cleaned_nl[key] = new_infobox[key]
    else:
        cleaned_nl = new_infobox

    # The combination of the existing infobox with our own infobox
    print(cleaned_nl)
    print(new_infobox)  # Our self created infobox so far
