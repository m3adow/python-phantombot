import logging
import requests
import attr


logger = logging.getLogger(__name__)


@attr.s
class PhantomBotRestAPI(object):
    url = attr.ib()
    user = attr.ib()
    webauth = attr.ib()
    requests_kwargs = attr.ib(default={})

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

    # Polling stuff
    def open_poll(self, question, options, duration=None, min_votes=None):
        if not min_votes:
            min_votes = ''
        if not duration:
            duration = ''

        req = '!poll open "{question}" "{options}" {duration} {min_votes}'.format(
            question=question, options=', '.join(str(option) for option in options), duration=duration,
            min_votes=min_votes
        )
        logger.debug(req)
        return self.api_put(req)

    def close_poll(self):
        return self.api_put('!poll close')

    def get_poll_result(self):
        poll_title = self.api_query_db(payload={'table': 'pollPanel', 'getData': 'title'})['value']
        poll_status = self.db_get_data(table='pollPanel', key='isActive')
        poll_result = self.db_get_table_data(table='pollVotes')

        return {'title': poll_title, 'active': poll_status, 'result': poll_result}



