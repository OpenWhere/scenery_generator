#!/usr/bin/env python3

from generator import Generator
from scraper import Scraper
import os, pprint

DOCS_URL = "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"
CONTENTS_PAGE = "aws-template-resource-type-ref.html"


def main():
    generator = Generator()
    scraper = Scraper(DOCS_URL)
    classes = scraper.get_documentation_pages(CONTENTS_PAGE)

    # For each AWS Type, retrieve the list of properties and generate class file
    for key, value in classes.items():
        properties = scraper.get_properties(value)
        if properties:
            try:
                property_map = { p['name']: p['type'] for p in properties }
                generator.create_class_file('./resource_type_template.js',
                                            key, property_map)
            except:
                print("Failed to generate file for %s: %s" % (key, properties))


if __name__ == '__main__':
    main()
