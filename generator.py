from scraper import Scraper
import os, pprint

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class Generator(object):
    def __init__(self):
        pass

    def create_class_file(self, template, class_name, property_map):
        """ Generates a scenery class file.
        template: file path to the scenery class template file
        class_name: AWS class name in the format AWS::DynamoDB::Table
        property_map: Dict represneting property types of the above class """

        class_array = class_name.split('::')
        if len(class_array) < 2:
            return None

        # Check to see if output directory exists; create it if not
        output_dir = os.path.join(CURRENT_DIR, 'output', class_array[1])
        file_path = os.path.join(output_dir, class_array[2] + ".js")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate the class file
        formatted_pm = pprint.pformat(property_map, indent=4, width=100).replace( \
                '{', '{\n ').replace( \
                '}', '\n}')

        with open (template, "r") as template_file:
            # Read in the template, plugging in our values for the class
            template = template_file.read()
            class_file_contents = template % (formatted_pm, class_name)

            # Write the file to the output directory
            with open(file_path, "w") as output_file:
                output_file.write(class_file_contents)
