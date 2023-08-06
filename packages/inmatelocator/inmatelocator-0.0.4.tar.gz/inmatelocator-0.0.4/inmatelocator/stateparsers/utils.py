import os
import re
import json

def fuzzy_lookup(dct, name):
    """
    Look up ``name`` as a fuzzy key of ``dct``.
    """
    pass

def normalize_name(name):
    name = re.sub("[^-a-z ]", "", name.lower()).strip()
    name = re.sub("-", " ", name)
    name = re.sub("\s+", " ", name)
    return name

def make_facility_lookup(state_name, normalize_func=None):
    normalize_func = normalize_func or normalize_name
    filename = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "{}.json".format(state_name))
    with open(filename) as fh:
        data = json.load(fh)

    facilities = {}
    for result in data:
        facilities[normalize_name(result['name'])] = result

    def lookup(term):
        term = normalize_func(term)
        return facilities.get(term)

    return lookup
