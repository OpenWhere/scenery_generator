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
(Work in progress)
```
$ ./generator.py
```

Scans all the online documentation and generates a property map, like so:
```python
{
    'AWS::CloudFormation::Stack': {
        'NotificationARNs ': 'Array',
        'TimeoutInMinutes ': 'String',
        'Parameters ': 'Object',
        'TemplateURL ': 'String'
    },
    'AWS::CloudFront::Distribution': {
        'DistributionConfig ': 'String'
    },
    'AWS::Route53::RecordSetGroup': {
        'RecordSets ': 'Array',
        'Comment ': 'String',
        'HostedZoneId ': 'String',
        'HostedZoneName ': 'String'
    },
    ...
}
```

TODO: Complete documentation

## License
This Software is licensed under the MIT license. See the LICENSE file.
