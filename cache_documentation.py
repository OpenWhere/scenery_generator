#!/usr/bin/env python2.7

from scraper import Scraper
import os

DOCS_URL = "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"
PROPERTY_TYPES_CONTENTS_PAGE = "aws-product-property-reference.html"
RESOURCE_TYPES_CONTENTS_PAGE = "aws-template-resource-type-ref.html"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    # Fetch the documentation from the internet
    scraper = Scraper(DOCS_URL)
    cache_dir = os.path.join(CURRENT_DIR, 'cache')
    properties_dir = os.path.join(cache_dir, 'properties')
    resources_dir = os.path.join(cache_dir, 'resources')

    for path in [cache_dir, properties_dir, resources_dir]:
        if not os.path.exists(path):
            os.makedirs(path)

    scraper.cache_documentation_pages(PROPERTY_TYPES_CONTENTS_PAGE, properties_dir)
    scraper.cache_documentation_pages(RESOURCE_TYPES_CONTENTS_PAGE, resources_dir)


if __name__ == '__main__':
    main()
