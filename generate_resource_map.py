#!/usr/bin/env python2.7

from generator import Generator
from scraper import Scraper
import os, json

DOCS_URL = "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"
PROPERTY_TYPES_CONTENTS_PAGE = "aws-product-property-reference.html"
RESOURCE_TYPES_CONTENTS_PAGE = "aws-template-resource-type-ref.html"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    scraper = Scraper(DOCS_URL)
    property_doc = scraper.get_documentation_pages(PROPERTY_TYPES_CONTENTS_PAGE)
    resource_doc = scraper.get_documentation_pages(RESOURCE_TYPES_CONTENTS_PAGE)

    property_type_map = scraper.get_type_map_from_soup(property_doc)
    resource_type_map = scraper.get_type_map_from_soup(resource_doc)

    clean_resource_map = clean_resource_property_names(
            property_type_map, resource_type_map)

    generator = Generator()
    generator.write_property_map('aws_resources_map.json', clean_resource_map)


def clean_resource_property_names(property_types, resource_types):
    generator = Generator()
    lookup_table, duplicate_names = generator.build_friendly_lookup_table(
            property_types, resource_types)

    # Change the href types to the friendly names in the lookup table
    clean_resource_types = {}
    for key, values in resource_types.iteritems():
        new_values = []
        for prop in values:
            if prop['type'] in lookup_table:
                new_type = lookup_table[prop['type']]
                if new_type not in duplicate_names:
                    print("Changing type from %s to %s" % (prop['type'], new_type))
                    prop['type'] = new_type
            new_values.append(prop)
        clean_resource_types[key] = new_values

    return clean_resource_types




if __name__ == '__main__':
    main()
