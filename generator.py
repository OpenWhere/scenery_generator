import collections, inflect
import json, os, pprint

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class Generator(object):
    def __init__(self):
        self.property_types = self.read_property_map(
                os.path.join(CURRENT_DIR, 'aws_properties_map.json'))
        self.resource_types = self.read_property_map(
                os.path.join(CURRENT_DIR, 'aws_resources_map.json'))


    def build_friendly_lookup_table(self, property_types, resource_types):
        """
        Takes the property_types map and the resource_types map and builds a
        lookup table of friendly names, keeping track of the duplicates.
        Returns two objects:
        + Dict of lookup table in format {'aws-href': 'Friendly Name', ...}
        + List of friendly names known to be duplicates
        """
        all_types = dict(property_types.items() + resource_types.items())

        # Create a lookup table of friendly names for all property types,
        # converting plural nouns to their singular form
        lookup_table = {}
        p = inflect.engine()
        for key, values in all_types.iteritems():
            for prop in values:
                if '-' in prop['type']:
                    prop['type'] = prop['type'].replace('-', '_')
                if '_' in prop['type']:
                    camelCaseType = self.to_camel_case(prop['type'])
                    friendly_name = p.singular_noun(camelCaseType)
                    if not friendly_name:
                        friendly_name = camelCaseType
                    lookup_table[prop['type']] = friendly_name

        friendly_names = lookup_table.values()
        duplicate_names = [x for x, y in collections.Counter(friendly_names).items() if y > 1]
        return (self.encode_dict_in_ascii(lookup_table), duplicate_names)


    def write_property_map(self, filename, property_types):
        """
        Accepts a property_types map and outputs it as JSON
        """
        file_path = os.path.join(CURRENT_DIR, filename)
        with open(file_path, "w") as output_file:
            json.dump(property_types, output_file, sort_keys=True, indent=2)


    def read_property_map(self, filename):
        """
        Accepts a file path to a JSON file
        Parses the file and returns the resulting dict
        """
        file_path = os.path.join(CURRENT_DIR, filename)
        with open(file_path, "r") as output_file:
            data = json.load(output_file, object_hook=self.encode_dict_in_ascii)
            return data


    def encode_dict_in_ascii(self, data):
        ascii_encode = lambda x: x.encode('ascii') \
                if isinstance(x, unicode) else x
        return dict(map(ascii_encode, pair) for pair in data.items())


    def create_resource_class_file(self, template, class_name, property_map):
        """ Generates a scenery resource class file.
        template: file path to the scenery class template file
        class_name: AWS class name in the format AWS::DynamoDB::Table
        property_map: Dict represneting property types of the above class """
        class_array = class_name.split('::')
        if len(class_array) < 3:
            return None

        simple_class_name = class_array[2]
        output_dir = os.path.join(CURRENT_DIR, 'output', class_array[1])
        file_path = os.path.join(output_dir, simple_class_name + ".js")

        parent_class = 'Taggable' if 'Tags' in property_map.keys() else 'Resource'
        return self.create_and_write_template( class_name, property_map,
                template, output_dir, file_path, parent_class)


    def create_property_class_file(self, template, class_name, property_map):
        output_dir = os.path.join(CURRENT_DIR, 'output', 'properties')
        file_path = os.path.join(output_dir, class_name + ".js")
        return self.create_and_write_template(
                class_name, property_map, template, output_dir, file_path)


    def create_and_write_template(self, class_name, property_map, template_path, output_dir, file_path, parent_class=None):

        # Check to see if output directory exists; create it if not
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate the require statements
        require_statements, non_primitives = self.get_require_statements(\
                property_map)

        # Generate the formatted property map
        formatted_pm = pprint.pformat(property_map, indent=4, width=100)\
                .replace("   '", "'")\
                .replace('True', 'true')\
                .replace('False', 'false')

        # All non-primitives need to have quotes removed from around them
        for np in non_primitives:
            formatted_pm = formatted_pm.replace(": '%s'" % np, ": %s" % np)

        with open (template_path, "r") as template_file:
            # Read in the template, plugging in our values for the class
            template = template_file.read()

            if not parent_class:
                class_file_contents = template % (require_statements,
                        formatted_pm, class_name)
            else:
                class_file_contents = template % (parent_class, parent_class,
                        require_statements, formatted_pm,
                        parent_class, class_name, parent_class)

            # Write the file to the output directory
            with open(file_path, "w") as output_file:
                output_file.write(class_file_contents)

    def get_require_statements(self, property_map):
        primitives = ['string', 'number', 'boolean', 'object']
        statement = "var {0} = require('../properties/{0}.js');"
        resource_statement = "var {0} = require('../{1}/{0}.js');"
        non_primitives = []
        require_statements = []
        for value in property_map.values():
            clean_value = value['type'].replace('"', '').strip()
            if clean_value not in primitives:
                if clean_value not in self.property_types.keys():
                    resource_refs = [ k for k in self.resource_types.keys() \
                                      if clean_value in k ]

                    if not resource_refs:
                        print("%s does not exist in properties or resources" % clean_value)
                        """ TODO: The following documentation edge cases are causing errors:

                        Listofroutetableids does not exist in properties or resources
                        Listofusers does not exist in properties or resources
                        LoginProfiletype does not exist in properties or resources
                        ExampleNetbiosNode2 does not exist in properties or resources
                        """
                        continue

                    # TODO: Handle multiple references? No issues with this yet!
                    aws, directory, resource = resource_refs[0].split("::")
                    print("Found %s in the resources dict: %s" % (resource, directory))
                    non_primitives.append(resource)
                    require_statement = resource_statement.format(resource, directory)
                    require_statements.append(require_statement)
                else:
                    non_primitives.append(clean_value)
                    require_statement = statement.format(clean_value)
                    require_statements.append(require_statement)

        if non_primitives:
            require_statements = "\n".join(require_statements)
            return require_statements, non_primitives
        else:
            return '', non_primitives

    def to_camel_case(self, snake_str):
        components = snake_str.split('_')
        # Capitalize the first letter of each component and join them together.
        return "".join([x.title() for x in components])
