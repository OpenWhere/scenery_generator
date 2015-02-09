from bs4 import BeautifulSoup
from urllib import urlopen

import os, pprint, re

class Scraper(object):
    """ Class for retrieving AWS documentation """
    def __init__(self, docs_url):
        self.docs_url = docs_url


    def get_documentation_pages(self, toc_page):
        """ Given a URL representing the table of contents, find every link
        on the page map its text to it's href
        Returns a dictionary in the format { "link text": docs_page_soup, ...}
        """
        docs_page = urlopen('%s/%s' % (self.docs_url, toc_page))
        soup = BeautifulSoup(docs_page)
        links = soup.find('div', { 'class' : 'highlights' }).findAll('a')

        # Parse the list of all classes to get names and URLS
        pages = {}
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
        for key, value in docs_page_dict.items():
            properties = self.get_properties(value)
            if properties:
                type_map[key] = properties

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
        href = link['href'].replace('.html', '').strip()
        return href
        #title = link.getText().replace('\n', '').replace(' ', '')
        #clean_key = "%s (%s)" % (title, href)
        #return clean_key


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
                'type': 'String'
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
                    clean_text = p.a.get('href').replace('.html','').strip()
                property_dict['type'] = self._get_type(clean_text)

            property_types.append(property_dict)
        return property_types


    def _get_type(self, type_string):
        string = type_string.lower()
        if 'string' in string:
            return 'String'
        if 'number' in string or 'integer' in string:
            return 'Number'
        if 'boolean' in string:
            return 'Boolean'
        return type_string
