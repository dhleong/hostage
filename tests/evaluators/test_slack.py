#!/usr/bin/env py.test
#
# Slack class tests
#

import responses

from hostage import slack

URL = "https://hooks.slack.com/"

@responses.activate
def test_Notifier_notify():
    responses.add(responses.POST, URL, \
            status=204)
    mySlack = slack.Notifier(URL)
    res = mySlack.notify("Foo")
    assert res == True

    sent = responses.calls[0].request.body
    assert sent == '{"text": "Foo"}'

