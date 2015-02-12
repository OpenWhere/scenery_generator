#!/usr/bin/env python2.7

from generator import Generator
from scraper import Scraper
import os

DOCS_URL = "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"
PROPERTY_TYPES_CONTENTS_PAGE = "aws-product-property-reference.html"
RESOURCE_TYPES_CONTENTS_PAGE = "aws-template-resource-type-ref.html"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    scraper = Scraper(DOCS_URL)
    property_cache_dir = None
    resource_cache_dir = None

    # Uncomment the following lines if you have cached docs you wish to use
    #property_cache_dir = os.path.join(CURRENT_DIR, 'cache/properties')
    #resource_cache_dir = os.path.join(CURRENT_DIR, 'cache/resources')

    property_doc = scraper.get_documentation_pages(PROPERTY_TYPES_CONTENTS_PAGE, property_cache_dir)
    resource_doc = scraper.get_documentation_pages(RESOURCE_TYPES_CONTENTS_PAGE, resource_cache_dir)

    property_type_map = scraper.get_type_map_from_soup(property_doc)
    resource_type_map = scraper.get_type_map_from_soup(resource_doc)

    clean_property_map = clean_property_type_names(
            property_type_map, resource_type_map)

    generator = Generator()
    generator.write_property_map('aws_properties_map.json', clean_property_map)



def clean_property_type_names(property_types, resource_types):
    """
    Accepts maps for property_types and resource_types, and creates a lookup
    table for friendly property type names by href. Then, it attemps to
    reconstruct the map with friendly names.
    Returns a propety_types map with friendly names as the key
    """
    generator = Generator()
    lookup_table, duplicate_names = generator.build_friendly_lookup_table(
            property_types, resource_types)

    # For all PROPERTY types (because we only care about beautifying these),
    # look up the friendly name from the lookup table we constructed
    clean_property_types = {}
    for key, value in property_types.iteritems():
        newKey = key.replace('-', '_')
        if not newKey in lookup_table:
            print("%s not found in lookup table" % newKey)
            clean_property_types[newKey] = value
            continue
        friendly_name = lookup_table[newKey]
        if friendly_name in duplicate_names:
            print("%s is a duplicate" % friendly_name)
            clean_property_types[newKey] = value
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

    return immaculate_property_types


if __name__ == '__main__':
    main()
