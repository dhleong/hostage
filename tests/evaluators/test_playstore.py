#!/usr/bin/env py.test
#
# Playstore class tests
#

import pytest

import responses

from hostage import playstore

class TestUpdateVerify:

    def test_package(self):
        with pytest.raises(Exception) as exc:
            playstore.Update(
                    package=None,
                    apk=None,
                    whatsnew=None)

        assert 'package' in str(exc.value)

    def test_apk(self):
        with pytest.raises(Exception) as exc:
            playstore.Update(
                    package="co.serenity",
                    apk=None,
                    whatsnew=None)

        assert 'apk' in str(exc.value)

    def test_track_raise(self):
        with pytest.raises(Exception) as exc:
            playstore.Update(
                    package="co.serenity",
                    apk='path/to/firefly.apk',
                    track='alliance',
                    whatsnew=None)

        assert 'track' in str(exc.value)

    def test_track_default(self):
        playstore.Update(
                package="co.serenity",
                apk='path/to/firefly.apk',
                whatsnew=None)

    def test_track_pass(self):
        playstore.Update(
                package="co.serenity",
                apk='path/to/firefly.apk',
                track='production',
                whatsnew=None)

    def test_whatsnewIsDict(self):
        with pytest.raises(Exception) as exc:
            playstore.Update(
                    package="co.serenity",
                    apk='path/to/firefly.apk',
                    whatsnew="Still flyin'")

        assert 'whatsnew' in str(exc.value)

    def test_whatsnew_pass(self):
        playstore.Update(
                package="co.serenity",
                apk='path/to/firefly.apk',
                whatsnew={
                    'en-US': "Still flyin'"
                    })

class MockService:
    pass

@pytest.fixture
def update():
    service = MockService()
    return playstore.Update(
            package='co.serenity',
            apk='path/to/firefly.apk',
            whatsnew={
                'en-US': "Still flyin'"
                },
            service=service)


class TestUpdatePublish:
    def test_verifyApk(self, update, capsys):
        assert update.publish() == None
        out, _ = capsys.readouterr()

        assert 'Could not find apk' in out

    # TODO verify behavior with mocks
