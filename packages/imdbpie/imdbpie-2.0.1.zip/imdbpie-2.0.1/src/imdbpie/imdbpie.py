from __future__ import absolute_import, unicode_literals

import os
import re
import json
import time
import random
import hashlib
import logging
import datetime

import requests
from six.moves import html_parser
from six.moves.urllib.parse import urlencode

from imdbpie.objects import Image, Title, Person, Review
from imdbpie.constants import BASE_URI, SHA1_KEY, USER_AGENTS

logger = logging.getLogger(__name__)


class Imdb(object):

    def __init__(self, api_key=None, locale=None, anonymize=None,
                 exclude_episodes=None, user_agent=None, cache=None,
                 cache_dir=None, proxy_uri=None):
        self.api_key = api_key or SHA1_KEY
        self.timestamp = time.mktime(datetime.date.today().timetuple())
        self.user_agent = user_agent or random.choice(USER_AGENTS)
        self.locale = locale or 'en_US'
        self.exclude_episodes = True if exclude_episodes is True else False
        self.caching_enabled = True if cache is True else False
        self.cache_dir = cache_dir or '/tmp/imdbpiecache'
        proxy_uri = proxy_uri or ('aniscartujo.com/webproxy/default.aspx?'
                                  'prx=https://{0}')
        base_uri_proxied = proxy_uri.format(BASE_URI)
        self.base_uri = base_uri_proxied if anonymize is True else BASE_URI

    def get_person_by_id(self, imdb_id):
        url = self._build_url('/name/maindetails', {'nconst': imdb_id})
        response = self._get(url)

        if response is None or self._is_redirection_result(response):
            return None

        person = Person(response["data"])
        return person

    def get_title_by_id(self, imdb_id):
        url = self._build_url('/title/maindetails', {'tconst': imdb_id})
        response = self._get(url)

        if response is None or self._is_redirection_result(response):
            return None

        # get the full cast information, add key if not present
        response['data']['credits'] = self._get_credits_data(imdb_id)
        response['data']['plots'] = self.get_title_plots(imdb_id)

        if (
            self.exclude_episodes is True and
            response['data'].get('type') == 'tv_episode'
        ):
            return None

        title = Title(data=response['data'])
        return title

    def get_title_plots(self, imdb_id):
        url = self._build_url('/title/plot', {'tconst': imdb_id})
        response = self._get(url)

        if response['data']['tconst'] != imdb_id:  # pragma: no cover
            return []

        plots = response['data'].get('plots', [])
        return [plot.get('text') for plot in plots]

    def title_exists(self, imdb_id):
        titles = self.get_title_by_id(imdb_id)
        return True if titles else False

    def search_for_person(self, name):
        search_params = {
            'json': '1',
            'nr': 1,
            'nn': 'on',
            'q': name
        }
        query_params = urlencode(search_params)
        search_results = self._get(
            'http://www.imdb.com/xml/find?{0}'.format(query_params))

        target_result_keys = (
            'name_popular', 'name_exact', 'name_approx', 'name_substring')
        person_results = []

        html_unescaped = html_parser.HTMLParser().unescape

        # Loop through all search_results and build a list
        # with popular matches first
        for key in target_result_keys:

            if key not in search_results.keys():
                continue

            for result in search_results[key]:
                result_item = {
                    'name': html_unescaped(result['name']),
                    'imdb_id': result['id']
                }
                person_results.append(result_item)
        return person_results

    def search_for_title(self, title):
        default_search_for_title_params = {
            'json': '1',
            'nr': 1,
            'tt': 'on',
            'q': title
        }
        query_params = urlencode(default_search_for_title_params)
        search_results = self._get(
            'http://www.imdb.com/xml/find?{0}'.format(query_params)
        )

        target_result_keys = (
            'title_popular', 'title_exact', 'title_approx', 'title_substring')
        title_results = []

        html_unescaped = html_parser.HTMLParser().unescape

        # Loop through all search_results and build a list
        # with popular matches first
        for key in target_result_keys:

            if key not in search_results.keys():
                continue

            for result in search_results[key]:
                year_match = re.search(r'(\d{4})', result['title_description'])
                year = year_match.group(0) if year_match else None

                result_item = {
                    'title': html_unescaped(result['title']),
                    'year': year,
                    'imdb_id': result['id']
                }
                title_results.append(result_item)

        return title_results

    def top_250(self):
        url = self._build_url('/chart/top', {})
        response = self._get(url)
        return response['data']['list']['list']

    def popular_shows(self):
        url = self._build_url('/chart/tv', {})
        response = self._get(url)
        return response['data']['list']

    def get_title_images(self, imdb_id):
        url = self._build_url('/title/photos', {'tconst': imdb_id})
        response = self._get(url)
        return self._get_images(response)

    def get_title_reviews(self, imdb_id):
        """
        Retrieves reviews for a title ordered by 'Best' descending
        """
        user_comments = self._get_reviews_data(imdb_id)

        if not user_comments:
            return None

        title_reviews = []

        for review_data in user_comments:
            title_reviews.append(Review(review_data))
        return title_reviews

    def get_person_images(self, imdb_id):
        url = self._build_url('/name/photos', {'nconst': imdb_id})
        response = self._get(url)
        return self._get_images(response)

    def _get_credits_data(self, imdb_id):
        url = self._build_url('/title/fullcredits', {'tconst': imdb_id})
        response = self._get(url)

        if response is None:
            return None

        return response.get('data').get('credits')

    def _get_reviews_data(self, imdb_id):
        url = self._build_url('/title/usercomments', {'tconst': imdb_id})
        response = self._get(url)

        if response is None:
            return None

        return response.get('data').get('user_comments')

    def _get_images(self, response):
        images = []

        for image_data in response.get('data').get('photos', []):
            images.append(Image(image_data))

        return images

    def _get_cache_item_path(self, url):
        """
        Generates a cache location for a given api call.
        Returns a file path
        """
        cache_dir = self.cache_dir
        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        cache_key = m.hexdigest()

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        return os.path.join(cache_dir, cache_key + '.cache')

    def _get_cached_response(self, file_path):
        """ Retrieves response from cache """
        if os.path.exists(file_path):
            logger.info('retrieving from cache: %s', file_path)

            with open(file_path, 'r+') as resp_data:
                cached_resp = json.load(resp_data)

            if cached_resp.get('exp') > self.timestamp:
                return cached_resp
            else:  # pragma: no cover
                logger.info('cached expired, removing: %s', file_path)
                os.remove(file_path)
        return None

    @staticmethod
    def _cache_response(file_path, resp):
        with open(file_path, 'w+') as f:
            json.dump(resp, f)

    def _get(self, url):
        if self.caching_enabled:
            cached_item_path = self._get_cache_item_path(url)
            cached_resp = self._get_cached_response(cached_item_path)
            if cached_resp:
                return cached_resp

        r = requests.get(url, headers={'User-Agent': self.user_agent})
        response = json.loads(r.content.decode('utf-8'))

        if self.caching_enabled:
            self._cache_response(cached_item_path, response)

        if response.get('error'):
            return None

        return response

    def _build_url(self, path, params):
        default_params = {
            'api': 'v1',
            'appid': 'iphone1_1',
            'apiPolicy': 'app1_1',
            'apiKey': self.api_key,
            'locale': self.locale,
            'timestamp': self.timestamp
        }

        query_params = dict(
            list(default_params.items()) + list(params.items())
        )
        query_params = urlencode(query_params)
        url = 'https://{0}{1}?{2}'.format(self.base_uri, path, query_params)
        return url

    @staticmethod
    def _is_redirection_result(response):
        """
        Returns True if response is that of a redirection else False
        Redirection results have no information of use.
        """
        imdb_id = response['data'].get('tconst')
        if (
            imdb_id and
            imdb_id != response['data'].get('news', {}).get('channel')
        ):
            return True
        return False
