#!/usr/bin/env python3
import csv
from functools import partial
import datetime

import requests
import vlermv
import lxml.html

url = 'http://nic.io/cgi-bin/whois'

@vlermv.cache('~/.io-whois/other')
def get_other(url):
    return requests.get(url)

@vlermv.cache('~/.io-whois/whois')
def get(domain):
    'Get a WHOIS record.'
    return requests.get(url, params = {'query': domain})

def _query_html(html, key, raise_error = True):
    'Query the body of a WHOIS record.'
    nodes = html.xpath('//td[text() = "%s"]/following-sibling::td' % key)
    if len(nodes) == 1:
        return str(nodes[0].text_content())
    elif raise_error:
        raise KeyError('"%s"' % key)

def parse(response):
    'Parse a whois response.'
    if 'The results are shown below.' in response.text:
        html = lxml.html.fromstring(response.text)
        query = partial(_query_html, html)
        date = datetime.datetime.strptime(query('First Registered :'), '%Y-%m-%d').date()
        return {
            'domain-name': query('Domain Name :'),
            'first-registered': date,
        }

def _most_popular():
    'List the most popular .io domains, based on someone\'s idea of popularity.'
    response = get_other('http://hack.ly/articles/the-most-popular-dot-io-domains/')
    html = lxml.html.fromstring(response.text)
    domains_and_more = html.xpath('//div[@class="entry-content"]/descendant::a/text()')
    return sorted(set(map(str, filter(lambda x: '.' in x, domains_and_more))))

def domain_registrations(most_popular = _most_popular, get = get, parse = parse):
    for domain in most_popular():
        response = get(domain)
        if not response.ok:
            raise ValueError('Error downloading "%s"\n' % domain)

        try:
            data = parse(response)
        except Exception as e:
            e.args = ('%s (%s)' % (e.args[0], domain),) + e.args[1:]
            raise e

        if data != None:
            yield data

def main():
    import sys
    writer = csv.DictWriter(sys.stdout, ('domain-name', 'first-registered'))
    for row in domain_registrations():
        writer.writerow(row)

if __name__ == '__main__':
    main()
