#!/usr/bin/env python2.7

from generator import Generator
from scraper import Scraper
import collections, json, os
import inflect

DOCS_URL = "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"
PROPERTY_TYPES_CONTENTS_PAGE = "aws-product-property-reference.html"
RESOURCE_TYPES_CONTENTS_PAGE = "aws-template-resource-type-ref.html"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    generator = Generator()
    scraper = Scraper(DOCS_URL)
    property_doc = scraper.get_documentation_pages(PROPERTY_TYPES_CONTENTS_PAGE)
    resource_doc = scraper.get_documentation_pages(RESOURCE_TYPES_CONTENTS_PAGE)

    property_type_map = scraper.get_type_map_from_soup(property_doc)
    resource_type_map = scraper.get_type_map_from_soup(resource_doc)

    clean_property_map = clean_property_type_names(property_type_map, resource_type_map)
    write_property_map(clean_property_map)



def clean_property_type_names(property_types, resource_types):
    """
    Accepts maps for property_types and resource_types, and creates a lookup
    table for friendly property type names by href. Then, it attemps to
    reconstruct the map with friendly names.
    Returns a propety_types map with friendly names as the key
    """
    all_types = dict(property_types.items() + resource_types.items())

    # Create a lookup table of friendly names for all property types,
    # converting plural nouns to their singular form
    lookup_table = {}
    p = inflect.engine()
    for key, values in all_types.iteritems():
        for prop in values:
            if '-' in prop['type']:
                friendly_name = p.singular_noun(prop['name'])
                if not friendly_name:
                    friendly_name = prop['name']
                lookup_table[prop['type']] = friendly_name

    friendly_names = lookup_table.values()
    duplicate_names = [x for x, y in collections.Counter(friendly_names).items() if y > 1]

    # For all PROPERTY types (because we only care about beautifying these),
    # look up the friendly name from the lookup table we constructed
    clean_property_types = {}
    for key, value in property_types.iteritems():
        if not key in lookup_table:
            print("%s not found in lookup table" % key)
            clean_property_types[key] = value
            continue
        friendly_name = lookup_table[key]
        if friendly_name in duplicate_names:
            print("%s is a duplicate" % friendly_name)
            clean_property_types[key] = value
        else:
            clean_property_types[friendly_name] = value

    # Finally, we need to scan every single value and change the href types
    # to the (singular) friendly names in the lookup table
    immaculate_property_types = {}
    for key, values in clean_property_types.iteritems():
        new_values = []
        for prop in values:
            if prop['type'] in lookup_table:
                new_type = lookup_table[prop['type']]
                if new_type not in duplicate_names:
                    print("Changing type from %s to %s" % (prop['type'], new_type))
                    prop['type'] = new_type
            new_values.append(prop)
        immaculate_property_types[key] = new_values

    return clean_property_types


def write_property_map(property_types):
    """
    Accepts a property_types map and outputs it as JSON
    """
    file_path = os.path.join(CURRENT_DIR, "aws_properties_map.json")
    with open(file_path, "w") as output_file:
        json.dump(property_types, output_file, sort_keys=True, indent=2)


if __name__ == '__main__':
    main()
