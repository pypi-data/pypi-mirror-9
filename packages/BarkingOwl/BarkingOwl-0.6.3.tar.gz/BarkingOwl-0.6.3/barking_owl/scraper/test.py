import datetime
from barking_owl import Scraper

"""
if (not 'target_url' in url_data) or  \
                (not 'doc_types' in url_data) or \
                (not 'title' in url_data) or \
                (not 'description' in url_data) or \
                (not 'max_link_level' in url_data) or \
                (not 'creation_datetime' in url_data) or \
                (not 'allowed_domains' in url_data):
"""

url = {
    'target_url': "http://timduffy.me/",
    'doc_types': [
        'application/pdf',
    ],
    'title': "TimDuffy.Me",
    'description': "Tim Duffy's Personal Website",
    'max_link_level': 1,
    'creation_datetime': str(datetime.datetime.now()),
    'allowed_domains': [
    ],
}

s = Scraper()
s.set_url_data(url)
data = s.start()
print data
