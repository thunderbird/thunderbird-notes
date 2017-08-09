import urllib2
import argparse
import yaml
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(
    description="""
    """, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("url", help="url to fetch")

args = parser.parse_args()

page = urllib2.urlopen(args.url).read()
s = BeautifulSoup(page, "lxml")

notes = []

for ul in s.findAll('ul', {'class': 'section-items'}):
    for child in ul.findChildren('li'):
        try:
            tag = child.find('b').text.lower()
        except AttributeError:
            tag = ''

        try:
            text = child.find('p').text
        except AttributeError:
            text = ''
        if 'Various security fixes' in text:
            text = child.find('p').find(text=True) + str(child.find('p').find('a'))

        notes.append({'note': text, 'tag': tag})

title = s.title.string
version = title[title.find("(")+1:title.find(")")]

bug_search_url = s.find('header', {'class': 'notes-head'}).findChildren('p')[0].findChildren('a')[2]
bug_search_url = str(bug_search_url['href'])

release = {'bug_search_url': bug_search_url}
notesfile = [{'release': release}, {'notes': notes}]

notes = ''
for n in notesfile:
    notes += yaml.safe_dump(n, default_flow_style=False)

with open(u"release/"+version+u".yml", "wb") as f:
    f.write(notes.encode('utf8'))
