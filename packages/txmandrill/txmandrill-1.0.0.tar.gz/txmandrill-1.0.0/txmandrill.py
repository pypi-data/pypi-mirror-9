"""The Mandrill Python client with Deferreds."""

import time
import json

from twisted.internet.defer import inlineCallbacks, returnValue
from mandrill import Mandrill, ROOT
import treq


HEADERS = {
    'content-type': 'application/json',
    'user-agent': 'Mandrill-Python/1.0.57'
}


class TXMandrill(Mandrill):

    """Override the base class to return Deferreds where appropriate."""

    def __init__(self, *args, **kwargs):
        """
        Init.

        None-ify the session, so the Requests library doesn't get involved.
        """
        super(TXMandrill, self).__init__(*args, **kwargs)
        self.session = None

    @inlineCallbacks
    def call(self, url, params=None):
        """Override Mandrill's call method to return a deferred."""
        params = params or {}
        params['key'] = self.apikey

        self.log('POST to %s%s.json: %s' % (ROOT, url, params))

        start = time.time()
        full_url = '{}{}.json'.format(ROOT, url)
        response = yield treq.post(
            full_url, data=json.dumps(params), headers=HEADERS)
        result = yield response.json()
        complete_time = time.time() - start

        self.log('Received {} in {}ms: {}'.format(
            response.code, complete_time * 1000, result))

        self.last_request = dict(
            url=url, request_body=params, response_body=result,
            response=response, time=complete_time
        )

        if response.code >= 400:
            raise self.cast_error(result)

        returnValue(result)
