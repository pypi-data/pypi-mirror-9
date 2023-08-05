# -*- coding: utf-8 -*-

import threading
import datetime
import random
import math
import logging
import sys
import time
import os
import socket
import json
import abc
from urllib.parse import urlencode

try:
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
    from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
except ImportError as ie:
    print(ie)
    sys.exit('You can install missing modules with `pip3 install [modulename]`')

import GoogleScraper.socks as socks
from GoogleScraper.proxies import Proxy
from GoogleScraper.caching import cache_results
from GoogleScraper.database import SearchEngineResultsPage, db_Proxy
from GoogleScraper.config import Config
from GoogleScraper.log import out
from GoogleScraper.output_converter import store_serp_result, end, dict_from_scraping_object
from GoogleScraper.parsing import GoogleParser, YahooParser, YandexParser, BaiduParser, BingParser, DuckduckgoParser, get_parser_by_search_engine, parse_serp

logger = logging.getLogger('GoogleScraper')


SEARCH_MODES = ('http', 'selenium', 'http-async')

class GoogleSearchError(Exception):
    pass

class InvalidNumberResultsException(GoogleSearchError):
    pass

class MaliciousRequestDetected(GoogleSearchError):
    pass

class SeleniumMisconfigurationError(Exception):
    pass

class SeleniumSearchError(Exception):
    pass

class StopScrapingException(Exception):
    pass


"""
GoogleScraper should be as robust as possible.

There are several conditions that may stop the scraping process. In such a case,
a StopScrapingException is raised with the reason.

- All proxies are detected and we cannot request further keywords => Stop.
- No internet connection => Stop.

- If the proxy is detected by the search engine we try to get another proxy from the pool and we call switch_proxy() => continue.

- If the proxy is detected by the search engine and there is no other proxy in the pool, we wait {search_engine}_proxy_detected_timeout seconds => continue.
    + If the proxy is detected again after the waiting time, we discard the proxy for the whole scrape.
"""


def get_base_search_url_by_search_engine(search_engine_name, search_mode):
    """Retrieves the search engine base url for a specific search_engine.

    This function cascades. So base urls in the SCRAPING section will
    be overwritten by search_engine urls in the specific mode sections.
    On the other side, if a search engine has no special url in it' corresponding
    mode, the default one from the SCRAPING config section will be loaded.

    Args:
        search_engine_name The name of the search engine
        search_mode: The search mode that is used

    Returns:
        The base search url.
    """
    assert search_mode in SEARCH_MODES, 'search mode "{}" is not available'.format(search_mode)

    specific_base_url = Config[search_mode.upper()].get('{}_search_url'.format(search_engine_name), None)

    if not specific_base_url:
        specific_base_url = Config['SCRAPING'].get('{}_search_url'.format(search_engine_name), None)

    ipfile = Config['SCRAPING'].get('{}_ip_file'.format(search_engine_name), '')

    if os.path.exists(ipfile):
        ips = open(ipfile, 'rt').read().split('\n')
        random_ip = random.choice(ips)
        return random_ip

    return specific_base_url

    
class SearchEngineScrape(metaclass=abc.ABCMeta):
    """Abstract base class that represents a search engine scrape.
    
    Each subclass that derives from SearchEngineScrape needs to 
    implement some common functionality like setting a proxy, 
    returning the found results, caching results and pushing scraped
    data to a storage like a database or an output file.
    
    The derivation is divided in two hierarchies: First we divide child
    classes in different Transport mechanisms. Scraping can happen over 
    different communication channels like Raw HTTP, doing it with the 
    selenium framework or using the an asynchronous HTTP client.
    
    The next layer is the concrete implementation of the search functionality
    of the specific search engines. This is not done in a extra derivation
    hierarchy (otherwise there would be a lot of base classes for each
    search engine and thus quite some boilerplate overhead), 
    instead we determine our search engine over the internal state
    (An attribute name self.search_engine) and handle the different search
    engines in the search function.
    
    Each must behave similarly: It can only scape at one search engine at the same time,
    but it may search for multiple search keywords. The initial start number may be
    set by the configuration. The number of pages that should be scraped for each
    keyword may be also set.
    
    It may be possible to apply all the above rules dynamically for each
    search query. This means that the search page offset, the number of
    consecutive search pages may be provided for all keywords uniquely instead
    that they are the same for all keywords. But this requires also a
    sophisticated input format and some more tricky engineering.
    """


    malicious_request_needles = {
        'google': {
            'inurl': '/sorry/',
            'inhtml': 'detected unusual traffic'
        },
        'bing': {},
        'yahoo': {},
        'baidu': {},
        'yandex': {},
        'ask': {},
        'blekko': {}
    }

    def __init__(self, keywords=None, scraper_search=None, session=None, db_lock=None, cache_lock=None,
                 start_page_pos=1, search_engine=None, search_type=None, proxy=None, progress_queue=None):
        """Instantiate an SearchEngineScrape object.

        Args:
            TODO
        """
        self.search_engine = search_engine
        assert self.search_engine, 'You need to specify an search_engine'

        self.search_engine = self.search_engine.lower()

        if not search_type:
            self.search_type = Config['SCRAPING'].get('search_type', 'normal')
        else:
            self.search_type = search_type
            
        # The number of pages to scrape for each keyword
        self.num_pages_per_keyword = Config['SCRAPING'].getint('num_pages_for_keyword', 1)
        
        # The keywords that need to be scraped
        # If a SearchEngineScrape receives explicitly keywords,
        # scrape them. otherwise scrape the ones specified in the Config.
        if keywords:
            self.keywords = keywords
        else:
            self.keywords = Config['SCRAPING'].get('keywords', [])

        self.keywords = list(set(self.keywords))

        # the keywords that couldn't be scraped by this worker
        self.missed_keywords = set()

        # the number of keywords
        self.num_keywords = len(self.keywords)
        
        # The actual keyword that is to be scraped next
        self.current_keyword = self.keywords[0]

        # The number that shows how many searches have been done by the worker
        self.search_number = 1

        # The parser that should be used to parse the search engine results
        self.parser = get_parser_by_search_engine(self.search_engine)()
        
        # The number of results per page
        self.num_results_per_page = Config['SCRAPING'].getint('num_results_per_page', 10)

        # The page where to start scraping. By default the starting page is 1.
        if start_page_pos:
            self.start_page_pos = 1 if start_page_pos < 1 else start_page_pos
        else:
            self.start_page_pos = Config['SCRAPING'].getint('search_offset', 1)

        # The page where we are right now
        self.current_page = self.start_page_pos
        
        # Install the proxy if one was provided
        self.proxy = proxy
        if isinstance(proxy, Proxy):
            self.set_proxy()
            self.ip = self.proxy.host + ':' + self.proxy.port
        else:
            self.ip = 'localhost'

        # the scraper_search object
        self.scraper_search = scraper_search
        
        # the scrape mode
        # to be set by subclasses
        self.scrapemethod = ''
        
        # Whether the instance is ready to run
        self.startable = True

        # set the database lock
        self.db_lock = db_lock

        # init the cache lock
        self.cache_lock = cache_lock

        # a queue to put an element in whenever a new keyword is scraped.
        # to visualize the progress
        self.progress_queue = progress_queue

        # set the session
        self.session = session

        # the current request time
        self.current_request_time = None

        # How long to sleep (in seconds) after every n-th request
        self.sleeping_ranges = dict()
        for line in Config['GLOBAL'].get('sleeping_ranges').split('\n'):
            assert line.count(':') == 1, 'Invalid sleep range format.'
            key, value = line.split(':')
            self.sleeping_ranges[int(key)] = tuple([int(offset.strip()) for offset in value.split(',')])


        # the default timeout
        self.timeout = 5



    @abc.abstractmethod
    def search(self, *args, **kwargs):
        """Send the search request(s) over the transport."""


    def blocking_search(self, callback, *args, **kwargs):
        """Similar transports have the same search loop layout.

        The SelScrape and HttpScrape classes have the same search loops. Just
        the transport mechanism is quite different (In HttpScrape class we replace
        the browsers functionality with our own for example).

        Args:
            callback: A callable with the search functionality.
            args: Arguments for the callback
            kwargs: Keyword arguments for the callback.
        """
        for i, self.current_keyword in enumerate(self.keywords):

            self.current_page = self.start_page_pos

            for self.current_page in range(1, self.num_pages_per_keyword + 1):

                # set the actual search code in the derived class
                try:

                    if not callback(*args, **kwargs):
                        self.missed_keywords.add(self.current_keyword)

                except StopScrapingException as e:
                    # Leave search when search engines detected us
                    # add the rest of the keywords as missed one
                    logger.critical(e)
                    self.missed_keywords.extend(self.keywords[i:])
                    return

    @abc.abstractmethod
    def set_proxy(self):
        """Install a proxy on the communication channel."""
        
    @abc.abstractmethod
    def switch_proxy(self, proxy):
        """Switch the proxy on the communication channel."""


    @abc.abstractmethod
    def proxy_check(self, proxy):
        """Check whether the assigned proxy works correctly and react"""


    @abc.abstractmethod
    def handle_request_denied(self, status_code):
        """Generic behaviour when search engines detect our scraping.

        Args:
            status_code: The status code of the http response.
        """
        logger.warning('Malicious request detected: {}'.format(status_code))

        # cascade
        timeout = Config['PROXY_POLICY'].getint('{search_engine}_proxy_detected_timeout'.format(
            search_engine=self.search_engine), Config['PROXY_POLICY'].getint('proxy_detected_timeout'))
        time.sleep(timeout)

    def store(self):
        """Store the parsed data in the sqlalchemy scoped session."""
        assert self.session, 'No database session. Turning down.'

        with self.db_lock:
            serp = SearchEngineResultsPage(
                search_engine_name=self.search_engine,
                scrapemethod=self.scrapemethod,
                page_number=self.current_page,
                requested_at=self.current_request_time,
                requested_by=self.ip,
                query=self.current_keyword,
                num_results_for_keyword=self.parser.search_results['num_results'],
            )
            self.scraper_search.serps.append(serp)

            serp, parser = parse_serp(serp=serp, parser=self.parser)

            if serp.num_results > 0:
                self.session.add(serp)
                self.session.commit()
            else:
                return False

            store_serp_result(dict_from_scraping_object(self), self.parser)

            return True

    def next_page(self):
        """Increment the page. The next search request will request the next page."""
        self.start_page_pos += 1

    def keyword_info(self):
        """Print a short summary where we are in the scrape and what's the next keyword."""
        out('[{thread_name}][{ip}][{search_engine}]Keyword: "{keyword}" with {num_pages} pages, slept {delay} seconds before scraping. {done}/{all} already scraped.'.format(
            thread_name=self.name,
            search_engine=self.search_engine,
            ip=self.ip,
            keyword=self.current_keyword,
            num_pages=self.num_pages_per_keyword,
            delay=self.current_delay,
            done=self.search_number,
            all=self.num_keywords
        ), lvl=2)

    def instance_creation_info(self, scraper_name):
        """Debug message whenever a scraping worker is created"""
        out('[+] {}[{}][search-type:{}][{}] using search engine "{}". Num keywords ={}, num pages for keyword={}'.format(
            scraper_name, self.ip, self.search_type, self.base_search_url, self.search_engine, len(self.keywords), self.num_pages_per_keyword), lvl=1)


    def cache_results(self):
        """Caches the html for the current request."""
        if Config['GLOBAL'].getboolean('do_caching', False):
            with self.cache_lock:
                cache_results(self.parser.cleaned_html, self.current_keyword, self.search_engine, self.scrapemethod)


    def _largest_sleep_range(self, search_number):
        """Sleep a given amount of time dependent on the number of searches done.

        Args:
            search_number: How many searches the worker has done yet.

        Returns:
            A range tuple which defines in which range the worker should sleep.
        """

        assert search_number >= 0
        if search_number != 0:
            s = sorted(self.sleeping_ranges.keys(), reverse=True)
            for n in s:
                if search_number % n == 0:
                    return self.sleeping_ranges[n]
        # sleep one second
        return (1, 2)

    def detection_prevention_sleep(self):
        # match the largest sleep range
        self.current_delay = random.randrange(*self._largest_sleep_range(self.search_number))
        time.sleep(self.current_delay)

    def after_search(self):
        """Store the results and parse em.

        Notify the progress queue if necessary.
        """
        self.parser.parse(self.html)
        self.search_number += 1

        if not self.store():
            logger.error('No results to store, skip current keyword: "{0}"'.format(self.current_keyword))
            return

        if self.progress_queue:
            self.progress_queue.put(1)
        self.cache_results()

    def before_search(self):
        """Things that need to happen before entering the search loop."""

        # check proxies first before anything
        if Config['SCRAPING'].getboolean('check_proxies', True) and self.proxy:
            if not self.proxy_check():
                self.startable = False


    def update_proxy_status(self, status, ipinfo={}, online=True):
        """Sets the proxy status with the results of ipinfo.io

        Args:
            status: A string the describes the status of the proxy.
            ipinfo: The json results from ipinfo.io
            online: Whether the proxy is usable or not.
        """

        with self.db_lock:

            proxy = self.session.query(db_Proxy).filter(self.proxy.host == db_Proxy.ip).first()
            if proxy:
                for key in ipinfo.keys():
                    setattr(proxy, key, ipinfo[key])

                proxy.checked_at = datetime.datetime.utcnow()
                proxy.status = status
                proxy.online = online

                self.session.add(proxy)
                self.session.commit()

    def __del__(self):
        """Close the json array if necessary."""
        end()


class HttpScrape(SearchEngineScrape, threading.Timer):
    """Offers a fast way to query any search engine using raw HTTP requests.

    Overrides the run() method of the superclass threading.Timer.
    Each thread represents a crawl for one Search Engine SERP page. Inheriting
    from threading.Timer allows the deriving class to delay execution of the run()
    method.

    This is a base class, Any supported search engine needs to subclass HttpScrape to
    implement this specific scrape type.

    Attributes:
        results: Returns the found results.
    """

    # Several different User-Agents to diversify the requests.
    # Keep the User-Agents updated. Last update: 13th November 2014
    # Get them here: http://techblog.willshouse.com/2012/01/03/most-common-user-agents/
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B411 Safari/600.1.4',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'
    ]

    def __init__(self, *args, time_offset=0.0, **kwargs):
        """Initialize an HttScrape object to scrape over blocking http.

        HttpScrape inherits from SearchEngineScrape
        and from threading.Timer.
        """
        threading.Timer.__init__(self, time_offset, self.search)
        SearchEngineScrape.__init__(self, *args, **kwargs)
        
        # Bind the requests module to this instance such that each 
        # instance may have an own proxy
        self.requests = __import__('requests')
        
        # initialize the GET parameters for the search request
        self.search_params = {}

        # initialize the HTTP headers of the search request
        # to some base values that mozilla uses with requests.
        # the Host and User-Agent field need to be set additionally.
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        # the mode
        self.scrapemethod = 'http'

        # get the base search url based on the search engine.
        self.base_search_url = get_base_search_url_by_search_engine(self.search_engine, self.scrapemethod)

        super().instance_creation_info(self.__class__.__name__)


    def set_proxy(self):
        """Setup a socks connection for the socks module bound to this instance.

        Args:
            proxy: Namedtuple, Proxy to use for this thread.
        """
        def create_connection(address, timeout=None, source_address=None):
            sock = socks.socksocket()
            sock.connect(address)
            return sock

        pmapping = {
            'socks4': 1,
            'socks5': 2,
            'http': 3
        }
        # Patch the socket module
        # rdns is by default on true. Never use rnds=False with TOR, otherwise you are screwed!
        socks.setdefaultproxy(pmapping.get(self.proxy.proto), self.proxy.host, int(self.proxy.port), rdns=True)
        socks.wrap_module(socket)
        socket.create_connection = create_connection

    def switch_proxy(self, proxy):
        super().switch_proxy()

    def proxy_check(self):
        assert self.proxy and self.requests, 'ScraperWorker needs valid proxy instance and requests library to make the proxy check.'

        online = False
        status = 'Proxy check failed: {host}:{port} is not used while requesting'.format(**self.proxy.__dict__)
        ipinfo = {}

        try:
            text = self.requests.get(Config['GLOBAL'].get('proxy_info_url')).text
            try:
                ipinfo = json.loads(text)
            except ValueError as v:
                pass
        except self.requests.ConnectionError as e:
            status = 'No connection to proxy server possible, aborting: {}'.format(e)
        except self.requests.Timeout as e:
            status = 'Timeout while connecting to proxy server: {}'.format(e)
        except self.requests.exceptions.RequestException as e:
            status = 'Unknown exception: {}'.format(e)

        if 'ip' in ipinfo and self.proxy.host == ipinfo['ip']:
            online = True
            status = 'Proxy is working.'
        else:
            logger.warning(status)

        super().update_proxy_status(status, ipinfo, online)

        return online


    def handle_request_denied(self, status_code):
        """Handle request denied by the search engine.

        This is the perfect place to distinguish the different responses
        if search engine detect exhaustive searching.

        Args:
            status_code: The status code of the HTTP response.

        Returns:
        """
        super().handle_request_denied(status_code)

    def build_search(self):
        """Build the headers and params for the search request for the search engine."""
        
        self.search_params = {}

        # Don't set the offset parameter explicitly if the default search (no offset) is correct.
        start_search_position = None if self.current_page == 1 else str(int(self.num_results_per_page) * int(self.current_page))
        
        if self.search_engine == 'google':
            self.parser = GoogleParser()
            self.search_params['q'] = self.current_keyword
            self.search_params['num'] = str(self.num_results_per_page)
            self.search_params['start'] = start_search_position

            if self.search_type == 'image':
                self.search_params.update({
                    'oq': self.current_keyword,
                    'site': 'imghp',
                    'tbm': 'isch',
                    'source': 'hp',
                    #'sa': 'X',
                    'biw': 1920,
                    'bih': 881
                }) 
            elif self.search_type == 'video':
                self.search_params.update({
                    'tbm': 'vid',
                    'source': 'lnms',
                    'sa': 'X',
                    'biw': 1920,
                    'bih': 881
                })
            elif self.search_type == 'news':
                self.search_params.update({
                    'tbm': 'nws',
                    'source': 'lnms',
                    'sa': 'X'
                })

        elif self.search_engine == 'yandex':
            self.parser = YandexParser()
            self.search_params['text'] = self.current_keyword
            self.search_params['p'] = start_search_position

            if self.search_type == 'image':
                self.base_search_url = 'http://yandex.ru/images/search?'
        
        elif self.search_engine == 'bing':
            self.parser = BingParser()
            self.search_params['q'] = self.current_keyword
            self.search_params['first'] = start_search_position
            
        elif self.search_engine == 'yahoo':
            self.parser = YahooParser()
            self.search_params['p'] = self.current_keyword
            self.search_params['b'] = start_search_position
            self.search_params['ei'] = 'UTF-8'
            
        elif self.search_engine == 'baidu':
            self.parser = BaiduParser()
            self.search_params['wd'] = self.current_keyword
            self.search_params['pn'] = start_search_position
            self.search_params['ie'] = 'utf-8'
        elif self.search_engine == 'duckduckgo':
            self.parser = DuckduckgoParser()
            self.search_params['q'] = self.current_keyword
        elif self.search_engine == 'ask':
            self.search_params['q'] = self.current_keyword
            self.search_params['qsrc'] = '0'
            self.search_params['l'] = 'dir'
            self.search_params['qo'] = 'homepageSearchBox'
        elif self.search_engine == 'blekko':
            self.search_params['q'] = self.current_keyword
            
    def search(self, *args, rand=False, **kwargs):
        """The actual search for the search engine.

        When raising StopScrapingException, the scraper will stop.

        When return False, the scraper tries to continue with next keyword.
        """

        self.build_search()

        if rand:
            self.headers['User-Agent'] = random.choice(self.user_agents)

        try:
            super().detection_prevention_sleep()
            super().keyword_info()

            request = self.requests.get(self.base_search_url + urlencode(self.search_params), headers=self.headers, timeout=5)

            self.current_request_time = datetime.datetime.utcnow()
            self.html = request.text

            out('[HTTP - {url}, headers={headers}, params={params}'.format(
                url=request.url,
                headers=self.headers,
                params=self.search_params),
            lvl=3)

        except self.requests.ConnectionError as ce:
            reason = 'Network problem occurred {}'.format(ce)
            raise StopScrapingException('Stopping scraping because {}'.format(reason))
        except self.requests.Timeout as te:
            reason = 'Connection timeout {}'.format(te)
            raise StopScrapingException('Stopping scraping because {}'.format(reason))
        except self.requests.exceptions.RequestException as e:
            # In case of any http networking exception that wasn't caught
            # in the actual request, just end the worker.
            raise StopScrapingException('Stopping scraping because {}'.format(e))

        if not request.ok:
            self.handle_request_denied(request.status_code)
            return False

        super().after_search()

        return True

    def run(self):
        super().before_search()

        if self.startable:
            args = []
            kwargs = {}
            kwargs['rand'] = False
            SearchEngineScrape.blocking_search(self, self.search, *args, **kwargs)


class SelScrape(SearchEngineScrape, threading.Thread):
    """Instances of this class make use of selenium browser objects to query the search engines on a high level.
    """

    next_page_selectors = {
        'google': '#pnnext',
        'yandex': '.pager__button_kind_next',
        'bing': '.sb_pagN',
        'yahoo': '#pg-next',
        'baidu': '.n',
        'ask': '#paging div a.txt3.l_nu'
    }

    input_field_selectors = {
        'google': (By.NAME, 'q'),
        'yandex': (By.NAME, 'text'),
        'bing': (By.NAME, 'q'),
        'yahoo': (By.NAME, 'p'),
        'baidu': (By.NAME, 'wd'),
        'duckduckgo': (By.NAME, 'q'),
        'ask': (By.NAME, 'q'),
        'blekko': (By.NAME, 'q'),
    }

    normal_search_locations = {
        'google': 'https://www.google.com/',
        'yandex': 'http://www.yandex.ru/',
        'bing': 'http://www.bing.com/',
        'yahoo': 'https://yahoo.com/',
        'baidu': 'http://baidu.com/',
        'duckduckgo': 'https://duckduckgo.com/',
        'ask': 'http://ask.com/',
        'blekko': 'http://blekko.com/'
    }

    image_search_locations = {
        'google': 'https://www.google.com/imghp',
        'yandex': 'http://yandex.ru/images/',
        'bing': 'https://www.bing.com/?scope=images',
        'yahoo': 'http://images.yahoo.com/',
        'baidu': 'http://image.baidu.com/',
        'duckduckgo': None, # duckduckgo doesnt't support direct image search
        'ask': 'http://www.ask.com/pictures/',
        'blekko': None,
    }

    def __init__(self, *args, captcha_lock=None, browser_num=1, **kwargs):
        """Create a new SelScraper thread Instance.

        Args:
            captcha_lock: To sync captcha solving (stdin)
            proxy: Optional, if set, use the proxy to route all scrapign through it.
            browser_num: A unique, semantic number for each thread.
        """
        self.search_input = None

        threading.Thread.__init__(self)
        SearchEngineScrape.__init__(self, *args, **kwargs)

        self.browser_type = Config['SELENIUM'].get('sel_browser', 'chrome').lower()
        self.browser_num = browser_num
        self.captcha_lock = captcha_lock
        self.scrapemethod = 'selenium'

        # get the base search url based on the search engine.
        self.base_search_url = get_base_search_url_by_search_engine(self.search_engine, self.scrapemethod)
        super().instance_creation_info(self.__class__.__name__)

    def set_proxy(self):
        """Install a proxy on the communication channel."""

    def switch_proxy(self, proxy):
        """Switch the proxy on the communication channel."""

    def proxy_check(self):
        assert self.proxy and self.webdriver, 'Scraper instance needs valid webdriver and proxy instance to make the proxy check'

        online = False
        status = 'Proxy check failed: {host}:{port} is not used while requesting'.format(**self.proxy.__dict__)
        ipinfo = {}

        try:
            self.webdriver.get(Config['GLOBAL'].get('proxy_info_url'))
            try:
                ipinfo = json.loads(self.webdriver.page_source)
            except ValueError as v:
                pass
        except Exception as e:
            status = str(e)

        if 'ip' in ipinfo and self.proxy.host == ipinfo['ip']:
            online = True
            status = 'Proxy is working.'
        else:
            logger.warning(status)

        super().update_proxy_status(status, ipinfo, online)

        return online

    def _get_webdriver(self):
        """Return a webdriver instance and set it up with the according profile/ proxies.

        Chrome is quite fast, but not as stealthy as PhantomJS.

        Returns:
            The appropriate webdriver mode according to self.browser_type. If no webdriver mode
            could be found, return False.
        """
        if self.browser_type == 'chrome':
            return self._get_Chrome()
        elif self.browser_type == 'firefox':
            return self._get_Firefox()
        elif self.browser_type == 'phantomjs':
            return self._get_PhantomJS()

        return False

    def _get_Chrome(self):
        try:
            if self.proxy:
                chrome_ops = webdriver.ChromeOptions()
                chrome_ops.add_argument('--proxy-server={}://{}:{}'.format(self.proxy.proto, self.proxy.host, self.proxy.port))
                self.webdriver = webdriver.Chrome(chrome_options=chrome_ops)
            else:
                self.webdriver = webdriver.Chrome()
            return True
        except WebDriverException as e:
            # we dont have a chrome executable or a chrome webdriver installed
            logger.error(e)
        return False

    def _get_Firefox(self):
        try:
            if self.proxy:
                profile = webdriver.FirefoxProfile()
                profile.set_preference("network.proxy.type", 1) # this means that the proxy is user set, regardless of the type
                if self.proxy.proto.lower().startswith('socks'):
                    profile.set_preference("network.proxy.socks", self.proxy.host)
                    profile.set_preference("network.proxy.socks_port", self.proxy.port)
                    profile.set_preference("network.proxy.socks_version", 5 if self.proxy.proto[-1] == '5' else 4)
                    profile.update_preferences()
                elif self.proxy.proto == 'http':
                    profile.set_preference("network.proxy.http", self.proxy.host)
                    profile.set_preference("network.proxy.http_port", self.proxy.port)
                else:
                    raise ValueError('Invalid protocol given in proxyfile.')
                profile.update_preferences()
                self.webdriver = webdriver.Firefox(firefox_profile=profile)
            else:
                self.webdriver = webdriver.Firefox()
            return True
        except WebDriverException as e:
            # reaching here is bad, since we have no available webdriver instance.
            logger.error(e)
        return False

    def _get_PhantomJS(self):
        try:
            service_args = []

            if self.proxy:
                service_args.extend([
                    '--proxy={}:{}'.format(self.proxy.host, self.proxy.port),
                    '--proxy-type={}'.format(self.proxy.proto),
                ])

                if self.proxy.username and self.proxy.password:
                    service_args.append(
                        '--proxy-auth={}:{}'.format(self.proxy.username, self.proxy.password)
                    )

            self.webdriver = webdriver.PhantomJS(service_args=service_args)
            return True
        except WebDriverException as e:
            logger.error(e)
        return False

    def handle_request_denied(self):
        """Checks whether Google detected a potentially harmful request.

        Whenever such potential abuse is detected, Google shows an captcha.
        This method just blocks as long as someone entered the captcha in the browser window.
        When the window is not visible (For example when using PhantomJS), this method
        makes a png from the html code and shows it to the user, which should enter it in a command
        line.

        Returns:
            The search input field.

        Raises:
            MaliciousRequestDetected when there was not way to stp Google From denying our requests.
        """
        needles = self.malicious_request_needles[self.search_engine]

        if needles and needles['inurl'] in self.webdriver.current_url and needles['inhtml'] in self.webdriver.page_source:

            if Config['SELENIUM'].getboolean('manual_captcha_solving', False):
                with self.captcha_lock:
                    import tempfile
                    tf = tempfile.NamedTemporaryFile('wb')
                    tf.write(self.webdriver.get_screenshot_as_png())
                    import webbrowser
                    webbrowser.open('file://{}'.format(tf.name))
                    solution = input('enter the captcha please...')
                    self.webdriver.find_element_by_name('submit').send_keys(solution + Keys.ENTER)
                    try:
                        self.search_input = WebDriverWait(self.webdriver, 5).until(
                                EC.visibility_of_element_located(self._get_search_input_field()))
                    except TimeoutException as e:
                        raise MaliciousRequestDetected('Requesting with this ip is not possible at the moment.')
                    tf.close()

            else:
                # Just wait until the user solves the captcha in the browser window
                # 10 hours if needed :D
                out('Waiting for user to solve captcha', lvl=1)
                return self._wait_until_search_input_field_appears(10*60*60)

        elif 'is not an HTTP Proxy' in self.webdriver.page_source:
            raise GoogleSearchError('Inavlid TOR usage. Specify the proxy protocol as socks5')

    def build_search(self):
        """Build the search for SelScrapers"""
        assert self.webdriver, 'Webdriver needs to be ready to build the search'

        self.starting_point = None

        if Config['SCRAPING'].get('search_type', 'normal') == 'image':
            self.starting_point = self.image_search_locations[self.search_engine]
        else:
            self.starting_point = self.base_search_url

        self.webdriver.get(self.starting_point)


    def _get_search_input_field(self):
        """Get the search input field for the current search_engine.

        Returns:
            A tuple to locate the search field as used by seleniums function presence_of_element_located()
        """
        return self.input_field_selectors[self.search_engine]

    def _wait_until_search_input_field_appears(self, max_wait=5):
        """Waits until the search input field can be located for the current search engine

        Args:
            max_wait: How long to wait maximally before returning False.

        Returns: False if the search input field could not be located within the time
                or the handle to the search input field.
        """
        try:
            search_input = WebDriverWait(self.webdriver, max_wait).until(
                EC.visibility_of_element_located(self._get_search_input_field()))
            return search_input
        except TimeoutException as e:
            return False

    def _goto_next_page(self):
        """Finds the url that locates the next page for any search_engine.

        Returns:
            The href attribute of the next_url for further results.
        """
        if self.search_type == 'normal':
            selector = self.next_page_selectors[self.search_engine]
            try:
                # wait until the next page link emerges
                WebDriverWait(self.webdriver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                element = self.webdriver.find_element_by_css_selector(selector)
                next_url = element.get_attribute('href')
                element.click()
                return next_url
            except TimeoutException as te:
                logger.warning('Cannot locate next page element: {}'.format(te))
                return False
            except WebDriverException as e:
                logger.warning('Cannot locate next page element: {}'.format(e))
                return False

        elif self.search_type == 'image':
            self.page_down()
            return True

    def wait_until_serp_loaded(self):
        # Waiting until the keyword appears in the title may
        # not be enough. The content may still be from the old page.
        try:
            WebDriverWait(self.webdriver, 5).until(EC.title_contains(self.current_keyword))
        except TimeoutException as e:
            logger.error(SeleniumSearchError('Keyword "{}" not found in title: {}'.format(self.current_keyword, self.webdriver.title)))

    def search(self):
        """Search with webdriver.

        Fills out the search form of the search engine for each keyword.
        Clicks the next link while num_pages_per_keyword is not reached.
        """
        for self.current_keyword in self.keywords:

            self.search_input = self._wait_until_search_input_field_appears()

            if self.search_input is False:
                self.search_input = self.handle_request_denied()

            if self.search_input:
                self.search_input.clear()
                time.sleep(.25)
                self.search_input.send_keys(self.current_keyword + Keys.ENTER)
                self.current_request_time = datetime.datetime.utcnow()
            else:
                logger.warning('Cannot get handle to the input form for keyword {}.'.format(self.current_keyword))
                continue

            super().detection_prevention_sleep()
            super().keyword_info()

            for self.current_page in range(1, self.num_pages_per_keyword + 1):

                self.wait_until_serp_loaded()

                try:
                    self.html = self.webdriver.execute_script('return document.body.innerHTML;')
                except WebDriverException as e:
                    self.html = self.webdriver.page_source

                super().after_search()

                # Click the next page link not when leaving the loop
                # in the next iteration.
                if self.current_page < self.num_pages_per_keyword:
                    self.next_url = self._goto_next_page()
                    self.current_request_time = datetime.datetime.utcnow()
                    
                    if not self.next_url:
                        break

    def page_down(self):
        """Scrolls down a page with javascript.

        Used for next page in image search mode or when the 
        next results are obtained by scrolling down a page.
        """
        js = '''
        var w = window,
            d = document,
            e = d.documentElement,
            g = d.getElementsByTagName('body')[0],
            y = w.innerHeight|| e.clientHeight|| g.clientHeight;

        window.scrollBy(0,y);
        return y;
        '''

        self.webdriver.execute_script(js)

    def run(self):
        """Run the SelScraper."""

        if not self._get_webdriver():
            raise SeleniumMisconfigurationError('Aborting due to no available selenium webdriver.')

        try:
            self.webdriver.set_window_size(400, 400)
            self.webdriver.set_window_position(400*(self.browser_num % 4), 400*(math.floor(self.browser_num//4)))
        except WebDriverException as e:
            logger.error(e)

        super().before_search()

        if self.startable:
            self.build_search()
            self.search()

        if self.webdriver:
            self.webdriver.close()


"""
For most search engines, the normal SelScrape works perfectly, but sometimes
the scraping logic is different for other search engines.

Duckduckgo loads new results on the fly (via ajax) and doesn't support any "next page"
link. Other search engines like gekko.com have a completely different SERP page format.

That's why we need to inherit from SelScrape for specific logic that only applies for the given
search engine.

The following functionality may differ in particular:

    - _goto_next_page()
    - _get_search_input()
    - _wait_until_search_input_field_appears()
    - _handle_request_denied()
    - wait_until_serp_loaded()
"""

class DuckduckgoSelScrape(SelScrape):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.largest_id = 0

    def _goto_next_page(self):
        super().page_down()
        return 'No more results' not in self.html
    
    def wait_until_serp_loaded(self):
        def new_results(driver):
            try:
                elements = driver.find_elements_by_css_selector('[id*="r1-"]')
                if elements:
                    i = sorted([int(e.get_attribute('id')[3:]) for e in elements])[-1]
                    return i > self.largest_id
                else:
                    return False
            except WebDriverException:
                pass

        try:
            WebDriverWait(self.webdriver, 5).until(new_results)
        except TimeoutException as e:
            pass

        elements = self.webdriver.find_elements_by_css_selector('[id*="r1-"]')
        try:
            self.largest_id = sorted([int(e.get_attribute('id')[3:]) for e in elements])[-1]
        except:
            self.largest_id = 0
        

class BlekkoSelScrape(SelScrape):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def _goto_next_page(self):
        pass

class AskSelScrape(SelScrape):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def wait_until_serp_loaded(self):
        
        def wait_until_keyword_in_url(driver):
            try:
                return self.current_keyword in driver.current_url
            except WebDriverException as e:
                pass
            
        WebDriverWait(self.webdriver, 5).until(wait_until_keyword_in_url)


def get_selenium_scraper_by_search_engine_name(search_engine_name, *args, **kwargs):
    """Get the appropriate selenium scraper for the given search engine name.

    Args:
        search_engine_name: The search engine name.
        args: The arguments for the target search engine instance creation.
        kwargs: The keyword arguments for the target search engine instance creation.
    Returns;
        Either a concrete SelScrape instance specific for the given search engine or the abstract SelScrape object.
    """
    class_name = search_engine_name[0].upper() + search_engine_name[1:].lower() + 'SelScrape'
    ns = globals()
    if class_name in ns:
        return ns[class_name](*args, **kwargs)

    return SelScrape(*args, **kwargs)


class AsyncHttpScrape(SearchEngineScrape):
    pass
