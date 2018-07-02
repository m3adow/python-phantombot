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

    def put_message(self, message):
        headers = {
            'user': self.user,
            'webauth': self.webauth,
            'message': message
        }
        return requests.put(url=self.url, headers=headers, **self.requests_kwargs)

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
        return self.put_message(req)

    def close_poll(self):
        return self.put_message('!poll close')

