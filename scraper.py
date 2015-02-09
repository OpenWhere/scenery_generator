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
        if class_page:
            property_types = []
            soup = BeautifulSoup(class_page)
            try:
                properties_list = soup.dl.contents
            except:
                print('No docs for page %s' % page_url)
                return None

            # Break the docs up into sections by property
            sections = []
            section = []
            for item in properties_list:
                if item.name == 'dt':
                    if len(section) > 0:
                        sections.append(section)
                    section = []

                section.append(item)

            # Create a dictionary for each property type
            for s in sections:
                property_dict = {
                    'list': False,
                    'name': s[0].getText(),
                    'type': 'String'
                }
                dds = s[1:]
                for dd in dds:
                    ps = dd.findAll('p')
                    for p in ps:
                        text_contents = p.getText()
                        if not "Type:" in text_contents:
                            continue
                        clean_text = re.sub(' +', '', text_contents)\
                                .replace('Type:', '')\
                                .replace('.', '')\
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

        return None


    def _get_type(self, type_string):
        string = type_string.lower()
        if 'string' in string:
            return 'String'
        if 'number' in string or 'integer' in string:
            return 'Number'
        if 'boolean' in string:
            return 'Boolean'
        return type_string
