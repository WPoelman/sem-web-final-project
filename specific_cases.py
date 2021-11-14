#!/usr/bin/env python


#!/usr/bin/env python

"""
Filename:   specific_cases.py
Date:       14-11-2021
Authors:    Frank van den Berg, Esther Ploeger, Wessel Poelman
Description:
	Program to handle several specific cases in generating the Dutch infoboxes.
"""

from utils import get_dutch_title, translate


def handle_specific_cases(en_ib, nl_ib, key_pairs, en_title, nl_title):
    """Takes the English and currently generated Dutch infobox, to replace
    or add values for certain very specific cases"""

    # If NL title differs from the EN title, we say it is a translated book
    if 'name' in en_ib:
        if nl_title != en_title:
            nl_ib.pop(key_pairs['name'], None)
            # clean the en_title and nl_title
            nl_title = nl_title.replace(" (boek)", "")
            nl_title = nl_title.replace(" (roman)", "")
            en_title = en_title.replace(" (novel)", "")
            en_title = en_title.replace(" (book)", "")
            nl_ib['orig titel'] = en_title
            nl_ib['naam'] = nl_title

    # If it is translated, add the original language
    if 'orig titel' in nl_ib and 'language' in en_ib:
        nl_ib['originele taal'] = translate(en_ib['language'])

    # If a book is part of a series, we try to find the EN and NL wikipedia
	# pages for it
    if 'series' in en_ib:
        dutch_series = get_dutch_title(en_ib['series'])
        nl_ib.pop(key_pairs['series'], None)
        nl_ib['reeks'] = dutch_series

    # The country is always translated to Dutch
    if 'country' in en_ib:
        used_nl_key = key_pairs['country']
        nl_ib[used_nl_key] = translate(en_ib['country'])

    # The caption is also always translated
    if 'caption' in en_ib:
        used_nl_key = key_pairs['caption']
        nl_ib[used_nl_key] = translate(en_ib['caption'])

    # The genre label has some dubious exceptions when translating to Dutch
    if 'genre' in en_ib:
        genre = en_ib['genre']
        if genre == 'Science fiction':
            nl_ib['genre'] = 'Sciencefiction'
        elif genre == 'Fantasy':
            nl_ib['genre'] = 'Fantasy genre Fantasy'
        else:
            nl_ib['genre'] = translate(genre)

    return nl_ib
