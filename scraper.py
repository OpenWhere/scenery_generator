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
        Returns a dictionary in the format { "link text": "docs_page.html", ...}
        """
        docs_page = urlopen('%s/%s' % (self.docs_url, toc_page))
        soup = BeautifulSoup(docs_page)
        links = soup.find('div', { 'class' : 'highlights' }).findAll('a')

        # Parse the list of all classes to get names and URLS
        pages = {}
        for link in links:
            if not link.getText():
                continue
            title = link.getText().replace('\n', '').replace(' ', '')
            href = link['href'].replace('.html', '').strip()
            clean_key = "%s (%s)" % (title, href)
            pages[clean_key] = link['href']

        return pages


    def get_properties(self, page_url):
        print('Fetching: %s' % page_url)
        class_page = urlopen('%s/%s' % (self.docs_url, page_url))

        if not class_page:
            return None

        property_types = []
        soup = BeautifulSoup(class_page)
        try:
            properties_list = soup.find('div', { 'class' : 'variablelist' }).findAll('dt')
            properties_info = soup.find('div', { 'class' : 'variablelist' }).findAll('dd')
        except:
            print('No docs for page %s' % page_url)
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
