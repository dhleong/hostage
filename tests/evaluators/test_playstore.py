#!/usr/bin/env py.test
#
# Playstore class tests
#

import pytest

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

import responses

from hostage import playstore

@pytest.fixture
def secrets(tmpdir, request):
    update.tmpdir = tmpdir
    oldDir = tmpdir.chdir()

    tmpdir.join('client_secrets.json').write("")

    def fin():
        oldDir.chdir()
        
    request.addfinalizer(fin)
    return tmpdir

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

    def test_track_default(self, secrets):
        playstore.Update(
                package="co.serenity",
                apk='path/to/firefly.apk',
                whatsnew=None)

    def test_track_pass(self, secrets):
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

    def test_whatsnew_pass(self, secrets):
        playstore.Update(
                package="co.serenity",
                apk='path/to/firefly.apk',
                whatsnew={
                    'en-US': "Still flyin'"
                    })

    def test_secretsNotProvided(self):
        with pytest.raises(Exception) as exc:
            playstore.Update(
                    package="co.serenity",
                    apk='path/to/firefly.apk',
                    whatsnew={
                        'en-US': "Still flyin'"
                        })

        assert 'client_secrets.json' in str(exc.value)

class MockRequest:
    def __init__(self, result):
        self.result = result

    def execute(self):
        return self.result

class MockApks:
    def __init__(self):
        self.upload = MagicMock(return_value=MockRequest({'versionCode': 404}))

class MockApkListings:
    def __init__(self):
        self.update = MagicMock(return_value=MockRequest({
            'language': 'en-US'}))

class MockTracks:
    def __init__(self):
        self.update = MagicMock(return_value=MockRequest({
            'track': 'beta',
            'versionCodes': [404]}))

class MockEdits:
    def apks(self):
        if not '_apks' in self.__dict__: 
            self._apks = MockApks()
        return self._apks

    def apklistings(self):
        if not '_apklistings' in self.__dict__: 
            self._apklistings = MockApkListings()
        return self._apklistings

    def tracks(self):
        if not '_tracks' in self.__dict__: 
            self._tracks = MockTracks()
        return self._tracks

class MockService:

    def __init__(self):
        self._edits = MockEdits()
        self._edits.commit = \
                MagicMock(return_value=\
                MockRequest({"id": "edit-id"}))
        self._edits.insert = \
                MagicMock(return_value=\
                MockRequest({"id": "edit-id"}))

    def edits(self):
        return self._edits

@pytest.fixture
def update(tmpdir, request):

    # ch eagerly and prepare the secrets.json
    oldDir = tmpdir.chdir()
    tmpdir.join('client_secrets.json').write("")

    service = MockService()
    update = playstore.Update(
            package='co.serenity',
            apk='path-to/firefly.apk',
            whatsnew={
                'en-US': "Still flyin'"
                },
            service=service)
    update.tmpdir = tmpdir

    def fin():
        oldDir.chdir()
    request.addfinalizer(fin)
    return update


class TestUpdatePublish:
    def test_verifyApk(self, update, capsys):
        assert update.publish() == None
        out, _ = capsys.readouterr()

        assert 'Could not find apk' in out

    def test_publishWithWhatsNew(self, update):
        tmpdir = update.tmpdir
        oldDir = tmpdir.chdir()
        tmpdir.mkdir("path-to").join("firefly.apk").write("")

        assert update.publish() == True

        edits = update._service.edits()
        edits.insert.assert_called_once_with(
                body={}, packageName="co.serenity")

        edits.apks().upload.assert_called_once_with(
                editId='edit-id',
                packageName='co.serenity',
                media_body='path-to/firefly.apk')

        edits.apklistings().update.assert_called_once_with(
                editId='edit-id',
                packageName='co.serenity',
                language='en-US',
                apkVersionCode=404,
                body={'recentChanges': "Still flyin'"})

        edits.tracks().update.assert_called_once_with(
                editId='edit-id',
                track='beta',
                packageName='co.serenity',
                body={'versionCodes': [404]})

        edits.commit.assert_called_once_with(\
                editId="edit-id",
                packageName="co.serenity")

    def test_publishWithoutWhatsNew(self, update):
        update.whatsnew = None

        tmpdir = update.tmpdir
        oldDir = tmpdir.chdir()
        tmpdir.mkdir("path-to").join("firefly.apk").write("")

        assert update.publish() == True

        edits = update._service.edits()
        edits.insert.assert_called_once_with(
                body={}, packageName="co.serenity")

        edits.apks().upload.assert_called_once_with(
                editId='edit-id',
                packageName='co.serenity',
                media_body='path-to/firefly.apk')

        # the only difference from above
        edits.apklistings().update.assert_not_called()

        edits.tracks().update.assert_called_once_with(
                editId='edit-id',
                track='beta',
                packageName='co.serenity',
                body={'versionCodes': [404]})

        edits.commit.assert_called_once_with(\
                editId="edit-id",
                packageName="co.serenity")
