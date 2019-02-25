import logging

import attr
import requests

logger = logging.getLogger(__name__)


@attr.s
class PhantomBotRestAPI(object):
    url = attr.ib()
    user = attr.ib()
    webauth = attr.ib()
    requests_kwargs = attr.ib(factory=dict)

    _req_default_header = attr.ib()

    @_req_default_header.default
    def set_default_header(self):
        return {
            'user': self.user,
            'webauth': self.webauth
        }

    def api_put(self, message, api_path=''):
        headers = self._req_default_header.copy()
        headers['message'] = message
        return requests.put(url=self.url + api_path, headers=headers, **self.requests_kwargs)

    def api_get(self, payload, api_path=''):
        return requests.get(url='{url}/{path}'.format(url=self.url, path=api_path),
                            headers=self._req_default_header, params=payload)

    def api_query_db(self, payload):
        return self.api_get(api_path='dbquery', payload=payload).json()['table']

    def db_get_keys(self, table):
        return [keylist['key'] for keylist in self.api_query_db(payload={'table': table, 'getKeys': True})['keylist']]

    def db_get_data(self, table, key):
        return self.api_query_db(payload={'table': table, 'getData': key})['value']

    def db_get_table_data(self, table):
        table_data = {}
        for key in self.db_get_keys(table=table):
            table_data[key] = self.db_get_data(table=table, key=key)
        return table_data


@attr.s
class PhantomBotAPI(object):
    url = attr.ib()
    user = attr.ib()
    webauth = attr.ib()
    requests_kwargs = attr.ib(default=attr.Factory(dict))

    pbrest = attr.ib()

    @pbrest.default
    def initialize_pbrest(self):
        return PhantomBotRestAPI(
            url=self.url, user=self.user, webauth=self.webauth, requests_kwargs=self.requests_kwargs
        )

    # Polling stuff
    def open_poll(self, title, options, duration=None, min_votes=None):
        # Refactor min_votes or duration being 0 or False
        if not min_votes:
            min_votes = ''
        if not duration:
            duration = ''

        return self.pbrest.api_put(message='!poll open "{question}" "{options}" {duration} {min_votes}'.format(
            question=title, options=', '.join(str(option) for option in options), duration=duration,
            min_votes=min_votes))

    def close_poll(self):
        return self.pbrest.api_put('!poll close')

    def get_poll_result(self):
        poll_title = self.pbrest.api_query_db(payload={'table': 'pollPanel', 'getData': 'title'})['value']
        poll_status = self.pbrest.db_get_data(table='pollPanel', key='isActive')
        poll_result = {key: int(value) for key, value in self.pbrest.db_get_table_data(table='pollVotes').items()}

        return {'title': poll_title, 'active': poll_status, 'result': poll_result}

    # Stream title stuff
    def get_stream_title(self):
        return self.pbrest.db_get_data('streamInfo', 'title')

    def set_stream_title(self, title):
        return self.pbrest.api_put('!settitle {title}'.format(title=title))

    # Twitter stuff
    def post_twitter_message(self, message):
        return self.pbrest.api_put('!twitter post {msg}'.format(msg=message))

