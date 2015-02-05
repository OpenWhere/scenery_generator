#!/usr/bin/env python3

from scraper import Scraper
import os, pprint

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_URL = "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"
CONTENTS_PAGE = "aws-template-resource-type-ref.html"


def main():
    scraper = Scraper(DOCS_URL)
    classes = scraper.get_documentation_pages(CONTENTS_PAGE)

    # For each class, retrieve the list of properties and generate class file
    for key, value in classes.items():
        properties = scraper.get_property_list(value)
        if properties:
            property_map = scraper.clean_property_map(properties)
            create_class_file(key, property_map)


def create_class_file(class_name, property_map):
    class_array = class_name.split('::')
    if len(class_array) < 2:
        return None

    formatted_pm = pprint.pformat(property_map, indent=4, width=100).replace( \
            '{', '{\n ').replace( \
            '}', '\n}')

    with open ("./resource_type_template.js", "r") as template_file:
        # Read in the template, plugging in our values for the class
        template = template_file.read()
        class_file_contents = template % (formatted_pm, class_name)

        output_dir = os.path.join(CURRENT_DIR, 'output', class_array[1])
        file_path = os.path.join(output_dir, class_array[2] + ".js")

        # Check to see if the destination directory exists; if not, create it
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Output the file
        with open(file_path, "w") as output_file:
            output_file.write(class_file_contents)


if __name__ == '__main__':
    main()
