#!/usr/bin/env python3

from generator import Generator
from scraper import Scraper
import os, pprint

DOCS_URL = "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"
CONTENTS_PAGE = "aws-resource-ec2-network-interface.html"


def main():
    generator = Generator()
    scraper = Scraper(DOCS_URL)
    types = scraper.get_properties(CONTENTS_PAGE)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(types)

    
if __name__ == '__main__':
    main()
