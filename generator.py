#!/usr/bin/env python3

from bs4 import BeautifulSoup
from urllib.request import urlopen

import re

DOCS_URL = "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"
CONTENTS_URL = "%s/%s" % (DOCS_URL, "aws-template-resource-type-ref.html")

def main():
    # Get the list of all classes
    docs_page = urlopen(CONTENTS_URL)
    soup = BeautifulSoup(docs_page)
    links = soup.find_all('a')

    # Parse the list of all classes to get names and URLS
    classes = {}
    for link in links:
        if not link.getText() or 'AWS' not in link.getText():
            continue
        classes[link.getText()] = link['href']

    # For each class, retrieve the list of properties
    for key, value in classes.items():
        properties = get_property_list(value)
        if properties:
            property_map = get_property_map(properties)
            classes[key] = property_map

    print(classes)


def get_property_list(page_url):
    if 'aws' not in page_url or 'cfn' in page_url or '.html' not in page_url:
    	return None

    print("Fetching: %s" % page_url)
    class_page = urlopen("%s/%s" % (DOCS_URL, page_url))
    if class_page:
        soup = BeautifulSoup(class_page)
        properties = soup.find_all('pre')
        if len(properties) > 0:
            return properties[0].getText()
        else:
            return None
    return None


def get_property_map(json_string):
    lines = json_string.split("\n")

    # Throw away the lines that arne't properties
    property_lines = [l.strip() for l in lines \
            if ':' in l \
            and '::' not in l \
            and 'Properties' not in l]

    # Create a dict of the properties
    property_map = {}
    for l in property_lines:
        properties = l.split(':')
        key = properties[0].replace('"', '')
        value = properties[1].strip()

        # Identify property types
        if '}' in value:
            property_map[key] = "Object"
        elif ']' in value:
            property_map[key] = "Array"
        elif 'Integer' in value or 'Number' in value:
            property_map[key] = "Number"
        elif 'Boolean' in value:
            property_map[key] = "Boolean"
        else:
            property_map[key] = "String"

    return property_map


if __name__ == '__main__':
    main()
