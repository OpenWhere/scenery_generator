# Scenery Generator
Generates Scenery class files from the [Cloudformation Documentation](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html)

## License
This Software is licensed under the Apache 2.0 license. See the LICENSE file for
details.

## Setup
On OSX:
```bash
brew install python
pip install virtualenv
virtualenv /path/to/scenery-generator/environment/
cd /path/to/scenery-generator/environment/
git clone ...
source /path/to/scenery-generator/environment/bin/activate
pip install beautifulsoup4
pip install -e git+https://github.com/pwdyson/inflect.py#egg=inflect
```

## Type Classification
There are two type classifications available in the [AWS Cloudformation Documentation](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html):

1. Resource Types
2. Property Types

**Resource Types** are classes that correspond to an AWS Resource.

**Property Types** are classes that are used to help define and create Resource
Types.

Resource types will contain key-value pairs of properties. Some of these
properties are primitives (including `String`, `Number`, `Boolean`, and `Object`).
If a resource's property is not of a primitive Javascript type, it will be a
Property Type object.

Property types can sometimes contain other property types in their definitions.

## Usage
Scenery Generator offers two types of output:

1. Property Maps
2. Scenery Classes

Property Maps are JSON files containing a definition of every AWS CloudFormation
object as scraped from the documentation.

Scenery Classes are Javascript files that are generated based on the Property
Maps.

There are four commands you can run. If running all four commands, run them
in the following order:

```
./generate_property_map.py
./generate_resource_map.py
./generate_property_classes.py
./generate_resource_classes.py
```

The Scenery classes are output into the the `output` folder.
