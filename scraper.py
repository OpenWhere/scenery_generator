from bs4 import BeautifulSoup
from urllib import urlopen, urlretrieve

import os, pickle, re

class Scraper(object):
    """ Class for retrieving AWS documentation """
    def __init__(self, docs_url):
        self.docs_url = docs_url


    def cache_documentation_pages(self, toc_page, output_dir):
        docs_page = urlopen('%s/%s' % (self.docs_url, toc_page))
        soup = BeautifulSoup(docs_page)
        links = soup.find('div', { 'class' : 'highlights' }).findAll('a')

        # Parse the list of all classes to get names and URLS
        table_of_contents = {}
        for link in links:
            if not link.getText():
                continue

            filename = os.path.join(output_dir, link['href'])
            print("Caching file %s" % filename)
            urlretrieve("%s/%s" % (self.docs_url, link['href']), filename)

            soup = self.get_soup(link['href'])
            if not soup:
                continue

            friendly_name = self.get_type_title_and_reference(link)
            table_of_contents[friendly_name] = filename

        # Save the table of contents
        toc_filepath = os.path.join(output_dir, 'toc.pickle')
        with open(toc_filepath, 'wb') as toc_file:
            pickle.dump(table_of_contents, toc_file)


    def get_documentation_pages(self, toc_page, cache_dir=None):
        """ Given a URL representing the table of contents, find every link
        on the page map its text to it's href
        Returns a dictionary in the format { "link text": docs_page_soup, ...}
        """
        pages = {}
        if cache_dir:
            # Get soup objects from the cached documentation
            with open(os.path.join(cache_dir, 'toc.pickle'), 'r') as toc_file:
                pages = pickle.load(toc_file)

            for name, path in pages.iteritems():
                print("Reading %s from the cache" % name)
                soup = BeautifulSoup(open(path))
                pages[name] = soup
        else:
            # Get soup objects from online documentation
            docs_page = urlopen('%s/%s' % (self.docs_url, toc_page))
            soup = BeautifulSoup(docs_page)
            links = soup.find('div', { 'class' : 'highlights' }).findAll('a')

            for link in links:
                if not link.getText():
                    continue

                soup = self.get_soup(link['href'])
                if not soup:
                    continue

                friendly_name = self.get_type_title_and_reference(link)
                pages[friendly_name] = soup

        return pages


    def get_type_map_from_soup(self, docs_page_dict):
        """
        For the given docs page dict ({'href': soup, ...}), generate a type map
        of all property/resource types in the docs_page_dict
        """
        type_map = {}
        for key, value in docs_page_dict.iteritems():
            properties = self.get_properties(value)
            if properties:
                type_map[key] = properties
            else:
                # TODO: Fix these hard-coded edge cases and find an elegant solution
                if key == 'aws-properties-stack-parameters':
                    type_map[key] = [{'name': 'properties', 'type': 'object', 'list': False}]
                elif key == 'aws-properties-ec2-port-range':
                    type_map[key] = [
                            { 'name': 'from', 'type': 'number', 'list': False },
                            { 'name': 'to', 'type': 'number', 'list': False },
                    ]
                elif key == 'aws-properties-ec2-icmp':
                    type_map[key] = [
                            { 'name': 'code', 'type': 'number', 'list': False },
                            { 'name': 'type', 'type': 'number', 'list': False },
                    ]
                else:
                    print("No properties found for %s" % key)

        return type_map


    def get_soup(self, page_url):
        print('Fetching: %s' % page_url)
        class_page = urlopen('%s/%s' % (self.docs_url, page_url))

        if not class_page:
            return None
        try:
            return BeautifulSoup(class_page)
        except:
            print('Failed to soupify %s' % page_url)
            return None


    def get_type_title_and_reference(self, link):
        title = link.getText().replace('\n', '').replace(' ', '')
        href = link['href'].replace('.html', '').strip()

        # For Resource Types, we need the pretty name
        if ':' in title:
            return title

        return href


    def get_properties(self, soup):
        property_types = []
        try:
            properties_list = soup.find('div', { 'class' : 'variablelist' }).findAll('dt')
            properties_info = soup.find('div', { 'class' : 'variablelist' }).findAll('dd')
        except:
            return None

        for i in xrange(len(properties_list)):
            name = properties_list[i].getText()
            property_dict = {
                'list': False,
                'name': name,
                'type': 'string'
            }
            ps = properties_info[i].findAll('p')
            for p in ps:
                text_contents = p.getText()
                if not "Type" in text_contents:
                    continue
                clean_text = re.sub(' +', '', text_contents)\
                            .replace('Type', '')\
                            .replace('.', '')\
                            .replace(':', '')\
                            .replace('\n', '').strip()
                if 'list' in clean_text.lower():
                    property_dict['list'] = True
                    lower_text = clean_text.lower()
                    clean_text = re.sub('a*\s*list\s*(of)*', '', clean_text)\
                                .strip().title()
                if p.a:
                    clean_text = p.a.get('href')\
                                .replace('.html','')\
                                .replace('-', '_')\
                                .replace('aws_properties_', '')\
                                .replace('aws_property_', '')\
                                .replace('as_', '')\
                                .strip()

                clean_type = self._get_type(clean_text)
                if self._is_string_type(clean_type):
                    property_dict['type'] = 'string'
                elif self._is_object_type(clean_type):
                    property_dict['type'] = 'object'
                else:
                    property_dict['type'] = clean_type

                # Field-specific types
                if 'Attributes' in name:
                    property_dict['list'] = False
                    property_dict['type'] = 'object'

            property_types.append(property_dict)
        return property_types


    def _clean_name(self, name_string):
        """ Removes spaces and parenthetical statements from names """
        clean_name = re.sub('\(.*', '', name_string)
        clean_name = re.sub('\s', '', clean_name)
        return clean_name


    def _is_object_type(self, type_string):
        """
        Handle edge-case types that should be objects
        """
        exceptional_strings = [
            'Attribute',
            'aws_properties_name',
            'RefID',
            'Aamazonsnstopicsarns',
            'LoginProfiletype',
            'ExampleNetbiosNode2',
        ]
        for es in exceptional_strings:
            if es in type_string:
                return True

        return False


    def _is_string_type(self, type_string):
        """
        Handle edge-case types that should be strings
        """
        exceptional_strings = [
            'Youcannotcreate',
            'anemptymap',
            'curitygroup',
            'referencestoawsiamroles',
            'Timestamp',
            'Listofroutetableids',
            'Listofusers',
        ]
        for es in exceptional_strings:
            if es in type_string:
                return True

        return False


    def _get_type(self, type_string):
        string = type_string.lower()
        if 'string' in string:
            return 'string'
        if 'number' in string or 'integer' in string:
            return 'number'
        if 'boolean' in string:
            return 'boolean'
        if 'json' in string:
            return 'object'
        return type_string
