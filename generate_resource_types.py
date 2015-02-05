#!/usr/bin/env python3

from generator import Generator
from scraper import Scraper
import os, pprint

DOCS_URL = "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"
CONTENTS_PAGE = "aws-template-resource-type-ref.html"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    generator = Generator()
    scraper = Scraper(DOCS_URL)
    classes = scraper.get_documentation_pages(CONTENTS_PAGE)
    template_file = os.path.join(CURRENT_DIR,
            'templates', 'resource_type_template.js')

    # For each AWS Type, retrieve the list of properties and generate class file
    for key, value in classes.items():
        properties = scraper.get_properties(value)
        if properties:
            try:
                property_map = { p['name']: p['type'] for p in properties }
                generator.create_class_file(template_file, key, property_map)
            except:
                print("Failed to generate file for %s: %s" % (key, properties))


if __name__ == '__main__':
    main()
