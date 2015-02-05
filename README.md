# Scenery Generator
Generates Scenery class files from the [Cloudformation Documentation](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html)

## Setup
On OSX:
```bash
brew install python3
pyvenv /path/to/scenery-generator/environment/
cd /path/to/scenery-generator/environment/
git clone ...
source /path/to/scenery-generator/environment/bin/activate
pip install beautifulsoup4
```

## Usage
This library contains two classes:
+ **Scraper:** Responsible for fetching data and parsing HTML from the AWS
  documentation. It has three functions:
    - **Constructor:** Accepts a URL of the AWS CloudFormation Documentation
    - **`get_documentation_pages`:** Accepts a string representing the table of
    contents page of the amazon docs. Returns a dict in the format:

```python
{ 'AWS::Resrouce::Type': 'url_to_page.html', ...}
```

   - **`get_properties`:** Accepts a URL of a page to a specific Resource
   (Property) Type, and parses it to find all of the types. Returns a list of
   dicts representing each property. For example:

```python
[{
  "href": null,
  "list": false,
  "name": "Description",
  "type": "String"
},
{
  "href": null,
  "list": true,
  "name": "GroupSet",
  "type": "String"
},
{
  "href": null,
  "list": false,
  "name": "PrivateIpAddress",
  "type": "String"
},
{
  "href": "aws-properties-ec2-network-interface-privateipspec.html",
  "list": true,
  "name": "PrivateIpAddresses",
  "type": "Privateipaddressspecification"
},
... ]
```

See `generate_property_map.py` for an example of how to use this class.

+ **Generator:** Responsible for generating [Scenery](https://github.com/OpenWhere/scenery)
  class files through the magic of string interpolation and the use of the Scraper
  class to fetch data from the web. The code is pretty self-explanatory -- see
  `generate_resource_types` for an example of how to use this class.

## License
This Software is licensed under the MIT license. See the LICENSE file.
