#!/usr/bin/env python

"""
...
remember to:
pip install wptools
"""

import argparse
import wptools
import requests
import pickle

def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--titles_file", default='data/titlesAE.txt',
                        help="Input txt file containing book titles on each line")

    args = parser.parse_args()
    return args


def get_dutch_title(en_title):
    """Use the english title of a Wikipedia page to get the Dutch title"""
    try:
        URL = "https://en.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "query",
            "titles": title,
            "prop": "langlinks",
            "lllang": "nl",
            "format": "json"
        }

        results = requests.get(url=URL, params=PARAMS).json()
        pages = [p for p in results['query']['pages']]
        for p in pages:  # There is probably only one page
            dutch_title = results['query']['pages'][p]['langlinks'][0]['*']
    except:
        dutch_title = en_title

    return dutch_title


def get_infobox(title, language='en'):
    """Use the title of a Wikipedia page to get the infobox"""
    try:
        page = wptools.page(title, lang=language, silent=True).get_parse(show=False)
        infobox = page.data['infobox']
    except:
        infobox = False

    return infobox


def create_dict_pickle(dict, filename):
    with open(filename, 'wb') as handle:
        pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    args = create_arg_parser()

    # Get list of wikipedia page titles from txt file:
    titles = []
    with open(args.titles_file, 'r') as f:
        for line in f:
            titles.append(line.strip())
    print(len(titles))

    # Create {title: infobox} dictionary
    en_infoboxes = dict()
    nl_infoboxes = dict()
    both_infoboxes_titles = []  # List to store titles that actually contain both EN and NL infoboxes
    only_en = 0

    for title in titles:
        # First: try to get dutch title
        dutch_title = get_dutch_title(title)
        #print("ENGLISH TITLE: {} \t DUTCH TITLE: {}".format(title, dutch_title))

        # Get English infobox:
        en_infobox = get_infobox(title)

        if en_infobox:
            en_infoboxes[title] = en_infobox
            # Get dutch infobox
            nl_infobox = get_infobox(dutch_title, 'nl')
            if nl_infobox:
                nl_infoboxes[title] = nl_infobox
                both_infoboxes_titles.append(title)
            else:
                nl_infoboxes[title] = "NA"
                only_en += 1
    # Write full dictionary to pickle file:
    create_dict_pickle(en_infoboxes, 'all_en_infoboxesAE.pickle')
    create_dict_pickle(nl_infoboxes, 'all_nl_infoboxesAE.pickle')

    print("number of titles: ", len(titles))
    print("number of titles containing only EN infoboxes: ", only_en)
    print("number of titles containing both infoboxes: ", len(both_infoboxes_titles))



