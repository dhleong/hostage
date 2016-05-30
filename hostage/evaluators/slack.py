#
# Slack utils
#

import json
import requests

from ..core import Evaluator

class Notifier(Evaluator):
    def __init__(self, url):
        super(Notifier, self).__init__(url)
        self.url = url

    def notify(self, payload):
        if isinstance(payload, basestring):
            payload = {"text": payload}
        r = requests.post(self.url, json=payload)
        return r.status_code in [200, 204]
