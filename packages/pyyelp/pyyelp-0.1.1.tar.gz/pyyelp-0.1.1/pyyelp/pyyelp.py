#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from django.conf import settings

import json
import urllib
import urllib2
import os

import oauth2


API_HOST = 'api.yelp.com'
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'
PHONE_PATH = '/v2/phone_search/'

CONSUMER_KEY = os.environ.get('YELP_API_CONSUMER_KEY') or settings.YELP_CONSUMER_KEY
CONSUMER_SECRET = os.environ.get('YELP_API_CONSUMER_SECRET') or settings.YELP_CONSUMER_SECRET
TOKEN = os.environ.get('YELP_API_TOKEN') or settings.YELP_API_TOKEN
TOKEN_SECRET = os.environ.get('YELP_API_TOKEN_SECRET') or settings.YELP_API_SECRET


class Yelp(object):
    """
    Example:

        yelp = Yelp()
        yelp.search(term='moo')
    """

    def __init__(self, **config):
        return

    def request(self, host, path, url_params=None):
        """
        Prepares the OAuth authentication and send the request to the Yelp API

        :param host: Yelp API Host e.g. api.yelp.com
        :param path: Yelp API path to a specific API e.g. Search or Business
        :param url_params: Parameters required for a certain API
        :return: JSON response from the request
        """
        url_params = url_params or {}
        url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

        consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
        oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

        oauth_request.update(
            {
                'oauth_nonce': oauth2.generate_nonce(),
                'oauth_timestamp': oauth2.generate_timestamp(),
                'oauth_token': TOKEN,
                'oauth_consumer_key': CONSUMER_KEY
            }
        )
        token = oauth2.Token(TOKEN, TOKEN_SECRET)
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
        signed_url = oauth_request.to_url()

        print u'Querying {0} ...'.format(url)

        conn = urllib2.urlopen(signed_url, None)
        try:
            response = json.loads(conn.read())
        finally:
            conn.close()

        return response

    def search(self, term=None, location=None, latitude=None, longitude=None, offset=None, sort=0, category_filter=None,
               radius_filter=None, deals_filter=False, search_limit=20):
        """
        Search method that uses Yelp's Search API to retrieve releavant businesses

        For current details, refer to: https://www.yelp.com/developers/documentation/v2/search_api

        :param term: The search term(s)
        :param location: required string that has address, neighborhood, city, state or zip, optional country
        :param latitude: double geo latitude
        :param longitude: double geo longitude
        :param offset: Offset the results by this amount
        :param sort: Int sort by 0=Best matched (default), 1=Distance, 2=Highest Rated,
        :param category_filter: See https://www.yelp.com/developers/documentation/v2/all_category_list
        :param radius_filter: Int Search radius in meters
        :param deals_filter: boolean to exclusively search for businesses with deals
        :param search_limit: Int number of results to return
        :return: JSON response
        """

        url_params = {
            'limit': search_limit
        }

        if term is not None:
            url_params['term'] = term.replace(' ', '+')

        if location is not None:
            url_params['location'] = location.replace(' ', '+')

        if latitude is not None and longitude is not None and latitude is int and longitude is int:
            url_params['cll'] = '{0},{1}'.format(latitude, longitude)

        if offset is not None:
            url_params['offset'] = offset

        if sort is 1 or sort is 2:
            url_params['sort'] = sort

        if category_filter is not None:
            url_params['category_filter'] = category_filter

        if radius_filter is not None:
            url_params['radius_filter'] = radius_filter

        if deals_filter:
            url_params['deals_filter'] = deals_filter

        return self.request(API_HOST, SEARCH_PATH, url_params=url_params)

    def get_business_by_id(self, business_id):
        """

        :param business_id:
        :return:
        """
        business_path = BUSINESS_PATH + business_id

        return self.request(API_HOST, business_path)

    def search_by_phone_number(self, phone_number, cc='US', category=None):
        """

        :param phone_number:
        :param cc: string country code by ISO 3166-1 alpha-2 country code e.g. GB for United Kingdom
            refer to: http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
        :param category:
        :return: JSON response
        """
        url_params = {
            'phone': phone_number
        }

        if cc is not 'US' and cc is str:
            url_params['cc'] = cc

        if category and category is str:
            url_params['category'] = category

        phone_path = PHONE_PATH + phone_number

        return self.request(API_HOST, phone_path, url_params=url_params)

    def _set_api_host(self):
        if settings.YELP_API_HOST is not None:
            API_HOST = settings.YELP_API_HOST
        else:
            API_HOST = 'api.yelp.com'

