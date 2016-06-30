#
# Google Play Store publishing, etc.
#

import os

from apiclient import sample_tools
from oauth2client import client

from .base import File
from ..core import Evaluator

_SCOPE = 'https://www.googleapis.com/auth/androidpublisher'

class Update(Evaluator):

    """Represents an update to a Playstore listing"""

    def __init__(self, package, apk, whatsnew, track='beta',\
            secrets_json="client_secrets.json",\
            log=True, service=None):
        super(Update, self).__init__(package, apk, whatsnew, track, log)

        self.package = package
        self.apk = apk
        self.whatsnew = whatsnew
        self.track = track
        self.secretsJson = secrets_json
        self._verifyParams()

        if log:
            self._log = lambda *args: None
        else:
            def _log(*args):
                print(args)
            self._log = _log

        if service:
            self._service = service
        else:
            self._service = None

    def publish(self):
        service = self._getService()
        if not service: return

        if not File(self.apk).exists():
            print("Could not find apk: %s" % self.apk)
            return

        try:
            self._log("Preparing changeset...")
            editRequest = service.edits().insert(
                    body={}, packageName=self.package)
            result = editRequest.execute()
            editId = result['id']
            self._log("Got edit_id=%s; uploading %s..." \
                    % (editId, self.apk))

            apkResponse = service.edits().apks().upload(
                    editId=editId,
                    packageName=self.package,
                    media_body=self.apk).execute()
            versionCode = apkResponse['versionCode']
            self._log(apkResponse)
            self._log("Version code %d has been uploaded" % versionCode)

            if self.whatsnew:
                for lang, msg in self.whatsnew.iteritems():
                    self._log("Updating `what's new` for %s..." % lang)

                    whatsnewResponse = service.edits().apklistings().update(
                            editId=editId,
                            packageName=self.package,
                            language=lang,
                            apkVersionCode=versionCode,
                            body={'recentChanges': msg}).execute()
                    self._log('Updated "whats new" for %s' \
                            % (whatsnewResponse['language']))
            
            self._log('Moving to track `%s`...' % self.track)
            trackResponse = service.edits().tracks().update(
                editId=editId,
                track=self.track,
                packageName=self.package,
                body={u'versionCodes': [versionCode]}).execute()

            self._log('Track %s is set for version code(s) %s; committing changes...' \
                    % (trackResponse['track'], str(trackResponse['versionCodes'])))

            commitRequest = service.edits().commit(
                editId=editId, packageName=self.package).execute()

            self._log('Edit "%s" has been committed!' % (commitRequest['id']))
            return True

        except client.AccessTokenRefreshError:
            print('The credentials have been revoked or expired')
            return None

    def _getService(self):
        if self._service: return self._service

        # Authenticate and construct service.
        service, _ = sample_tools.init(
              ["playstore"],
              'androidpublisher',
              'v2',
              __doc__,
              os.path.join(os.getcwd(), "any"), # it looks in the dir of this file for creds.json
              scope=_SCOPE)

        self._service = service
        return service

    def _verifyParams(self):
        if self.package is None:
            raise Exception("Must provide `package`")

        if self.apk is None:
            raise Exception("Must provide `apk` path")

        if not self.track in ['alpha', 'beta', 'production']:
            raise Exception("`%s` is not a valid track")

        if self.whatsnew and type(self.whatsnew) is not dict:
            raise Exception("`whatsnew` must be a dict of lang -> notes")

        elif self.whatsnew:
            for (lang, msg) in self.whatsnew.iteritems():
                if len(msg) > 500:
                    raise Exception("`whatsnew` for `%s` is > 500 chars" % lang)

        secretsJsonFile = File(self.secretsJson)
        if not secretsJsonFile.exists():
            raise Exception("Must create `%s` file with information from the Play Store account settings" % os.path.realpath(secretsJsonFile.path))
