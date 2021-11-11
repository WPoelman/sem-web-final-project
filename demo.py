#!/usr/bin/env python

"""
A program to retrieve the English infobox from a given Wikipedia page title,
then either expand the existing Dutch infobox or create a new Dutch infobox.
"""

import argparse
import wptools
import requests
import sys
import clean
from deep_translator import GoogleTranslator


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--title", default='The Very Hungry Caterpillar', type=str,
                        help="Title of the English wikipedia page (default: 'The Very Hungry Caterpillar')")

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
        translated_val = GoogleTranslator(source=source, target=target).translate(value)
    except:
        return value
    return translated_val


if __name__ == "__main__":
    args = create_arg_parser()

    # Get EN title and retrieve English wikipedia infobox
    en_title = args.title
    en_infobox = get_infobox(en_title)

    # If there is no EN infobox, we stop here, else we try to get the NL infobox as well
    if not en_infobox:
        print("There is no infobox available for this Wikipedia page, "
              "please try another title.", file=sys.stderr)
    else:
        # Get NL title and retrieve Dutch wikipedia infobox
        nl_title = get_dutch_title(en_title)
        nl_infobox = get_infobox(nl_title, 'nl')

        # Clean the English infobox
        cleaned_en = clean.clean_ib_dict(en_infobox)

        # todo: get the mappings
        mapping = "PUT METHOD TO GET MAPPINGS HERE"

        # Either expand the existing NL infobox or generate a new one
        if nl_infobox:
            cleaned_nl = clean.clean_ib_dict(nl_infobox)
            # todo: expand the NL infobox with keys that are not in there
            # todo: Maybe we should just check for each label that we generate whether it is already in the infobox
        else:
            # todo: generate new infobox
            for en_label in cleaned_en:
                # todo: Retrieve dutch label from mapping
                nl_label = "GET LABEL FROM MAPPING"

                if en_label not in mapping:
                    # Simply translate the English label to a Dutch label
                    nl_label = translate(en_label)






