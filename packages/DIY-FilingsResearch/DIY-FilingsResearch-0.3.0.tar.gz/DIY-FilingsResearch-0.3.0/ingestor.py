#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, print_function

import xml.etree.ElementTree as ET
from lxml import etree
import concurrent.futures
import requests
import requests.utils
from threading import Timer
from selenium import webdriver
import selenium
import datetime
import sys
import os
import re

try:
    import httplib
except ImportError:
    import http.client as httplib

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class Ingestor():

    __HTML_decode = [
        ('%3A', '_'),
        ('%5C', '_')
    ]

    def file_downloader(self, urls, directory):
        """
        file_downloader asynchronously downloads all required
        documents using threads. By default the max number of
        threads running asynchronously is 5, but you can
        adjust this for your own system.
        """

        if urls is None or len(urls) == 0:
            return

        def load_url(url, timeout):
            if url['type'] == "GET":
                request = requests.get(url['url'], headers=url['headers'],
                    stream=True, timeout=timeout)
            elif url['type'] == "POST":
                request = requests.post(url['url'], headers=url['headers'],
                    cookies=url['cookies'], stream=True, timeout=timeout)
            return request

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = \
                {executor.submit(load_url, url, 60): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()

                    if data.status_code == requests.codes.ok:

                        local_filename = url['url'].split('/')[-1]

                        # clean up gross filenames
                        for k, v in self.__HTML_decode:
                            local_filename = local_filename.replace(k, v)

                        with open(directory + "/" + local_filename,
                         'wb') as handle:
                            for block in data.iter_content(chunk_size=1024):
                                if not block:
                                    break
                                handle.write(block)
                            handle.close()

                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))


class IngestorException(Exception):
    pass


class Sedar():
    """
    SEDAR is document filing and retrieval system used by the CSA (Canada)
    """

    __cookies = {'initial': None,
                 'download': None}

    __headers = {
        'User-Agent': 'DIY-FilingsResearch 0.1'
    }

    def __init__(self, doc_type=None, start_date=None, end_date=None):
        self.org_root = "http://www.sedar.com"

        # error will occur if you use a start_date prior to 1/1/1997
        if start_date is None:
            self.start_date = datetime.datetime(1997, 1, 1, 0, 0)
        else:
            self.start_date = datetime.datetime.strptime(start_date,
                "%Y-%d-%m")

            if self.start_date <= datetime.datetime(1997, 1, 1, 0, 0):
                raise IngestorException('use a start_date after 1/1/1997')

        self.start_month = self.start_date.month
        self.start_day = self.start_date.day
        self.start_year = self.start_date.year

        if end_date is None:
            self.end_date = datetime.datetime.now().date()
        else:
            self.end_date = datetime.datetime.strptime(end_date, "%Y-%d-%m")

        self.end_month = self.end_date.month
        self.end_day = self.end_date.day
        self.end_year = self.end_date.year

        if doc_type == "html":
            self.doc_type = 5
        else:
            self.doc_type = 26

    def restart(self):
        os.execv(__file__, sys.argv)

    @staticmethod
    def return_link(needle, endpoint, headers, cookies,
     params=None, index_offset=0):
        """
        return_link finds a needle link in a haystack of links on an html page
        """

        feed = requests.post(Sedar().org_root + endpoint, params=params,
            headers=headers, cookies=cookies)

        output = StringIO(feed.text.encode('utf-8'))
        tree = etree.parse(output, etree.HTMLParser())
        links = list(tree.iter("a"))

        for l in range(0, len(links)):
            if needle in links[l].attrib['href']:
                return links[l - index_offset].attrib['href']
                break

    def ingest_stock(self, ticker):
        """
        ingest_stock essentially scrapes the site for the actual documents
        we need to download. It uses a ticker or keyword.
        """

        to_parse = []

        initial_params = {
            'lang': 'EN',
            'page_no': 1,
            'company_search': ticker,
            'document_selection': int(self.doc_type),
            'industry_group': 'A',
            'FromMonth': int(self.start_month),
            'FromDate': int(self.start_day),
            'FromYear': int(self.start_year),
            'ToMonth': int(self.end_month),
            'ToDate': int(self.end_day),
            'ToYear': int(self.end_year),
            'Variable': 'Issuer',
            'Search': 'Search'
        }

        session = requests.session()

        initial_request = session.post(self.org_root + "/\
        FindCompanyDocuments.do", params=initial_params)
        processed = initial_request.text.encode('utf-8')
        self.__cookies['initial'] = \
            requests.utils.dict_from_cookiejar(initial_request.cookies)
        link = Sedar().return_link("DisplayProfile",
            Sedar().return_link("DisplayCompanyDocuments",
            Sedar().return_link("AcceptTermsOfUse", "/FindCompanyDocuments.do",
            self.__headers,
            self.__cookies['initial'],
            initial_params,
            1), self.__headers,
            self.__cookies['initial']),
            self.__headers,
            self.__cookies['initial'])

        driver = selenium.webdriver.Firefox()
        driver.get(self.org_root + link)
        accept_cookies = None
        print("once you accept you can close the window")

        while True:

            if accept_cookies is None:
                accept_cookies = driver.get_cookies()
            try:
                driver.get_cookies()
            except selenium.common.exceptions.NoSuchWindowException:
                break
            except httplib.BadStatusLine:
                break

        Timer(accept_cookies[0]['expiry'], self.restart, ()).start()
        self.__cookies['download'] = \
            {cookie['name']: cookie['value'] for cookie in accept_cookies}
        feed = session.post(self.org_root + "/\
         FindCompanyDocuments.do", params=initial_params,
            headers=self.__headers, cookies=self.__cookies['download'])

        output = StringIO(feed.text.encode('utf-8'))
        tree = etree.parse(output, etree.HTMLParser())
        links = list(tree.iter("form"))

        urls = [self.org_root + link.attrib['action'] for link in links]

        for url in urls:
            to_parse.append({'url': url,
                             'type': 'POST',
                             'headers': self.__headers,
                             'cookies': self.__cookies['download']})
        return to_parse


class Edgar():
    """
    EDGAR is document filing and retrieval system used by the SEC (US)
    """

    __headers = {
        'User-Agent': 'DIY-FilingsResearch 0.1'
    }

    filing_types = ['10-K', '10-Q']

    doc_types = {
        'html': ["Document Format Files", ".htm", filing_types],
        'xbrl': ["Data Files", ".xml", "XBRL INSTANCE DOCUMENT"]}

    def __init__(self, doc_type=None, start_date=None, end_date=None):
        self.org_root = "http://www.sec.gov"

        if start_date is None:
            self.start_date = datetime.datetime(1970, 1, 1, 0, 0)
        else:
            self.start_date = datetime.datetime.strptime(start_date,
                "%Y-%d-%m")

        if end_date is None:
            self.end_date = datetime.datetime.now().date()
        else:
            self.end_date = datetime.datetime.strptime(end_date, "%Y-%d-%m")

        if doc_type == "html":
            self.doc_type = Edgar.doc_types['html']
        else:
            self.doc_type = Edgar.doc_types['xbrl']

    def page_search(self, tree, types):
        """
        page_search finds the document url in the document listing file links.
        """

        grab_next = False
        tables = list(tree.iter("table"))

        try:
            for table in tables:
                if table.attrib['summary'] == self.doc_type[0]:
                    for row in table.findall('tr'):
                        for column in row.findall('td'):
                            if grab_next:
                                links = list(column.iter("a"))
                                for link in links:
                                    return link.attrib['href']
                                    break
                                grab_next = False
                            if column.text in self.doc_type[2]:
                                grab_next = True
        except UnicodeEncodeError:
            pass

    def ingest_stock(self, ticker):
        """
        ingest_stock essentially scrapes the site for the actual
        documents we need to download. It uses a ticker or keyword.
        """

        to_parse = []

        for types in self.doc_type[2]:
            feed = requests.get(self.org_root + '/cgi-bin/browse-edgar',
                params={'action': 'getcompany', 'CIK': ticker, 'type': types,
                'dateb': str(self.start_date.strftime("%Y-%d-%m")),
                'count': 200, 'output': 'atom'})

            try:
                ticker_feed = ET.fromstring(feed.text.encode('utf-8'))
            except Exception as e:
                break

            for item in ticker_feed.findall('{http://www.w3.org/2005/Atom' + \
                 '}entry'):
                html_url = item[1].find('{http://www.w3.org/2005/Atom}fi' + \
                 'ling-href').text.encode('ascii', 'ignore')

                output = StringIO(requests.get(html_url).text.encode('ascii',
                 'ignore').decode('utf-8'))
                tree = etree.parse(output, etree.HTMLParser())
                output = self.page_search(tree, types)
                if output and self.doc_type[1] in output:
                    to_parse.append({'url': self.org_root + output,
                                     'type': 'GET',
                                     'headers': self.__headers})
        return to_parse
