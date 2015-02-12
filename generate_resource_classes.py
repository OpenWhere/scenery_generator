#!/usr/bin/env python2.7

from generator import Generator
from scraper import Scraper
import os, pprint

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    generator = Generator()
    template_file = os.path.join(CURRENT_DIR,
            'templates', 'resource_type_template.js')

    resource_type_map = os.path.join(CURRENT_DIR, 'aws_resources_map.json')
    resource_type_dict = generator.read_property_map(resource_type_map)

    # For each AWS Type, retrieve the list of properties and generate class file
    for key, value in resource_type_dict.iteritems():
        try:
            property_map = { p['name']: p['type'] for p in value }
            generator.create_resource_class_file(template_file, key, property_map)
        except Exception as exc:
            print("Failed to generate file for %s: %s" % (key, exc))

if __name__ == '__main__':
    main()
