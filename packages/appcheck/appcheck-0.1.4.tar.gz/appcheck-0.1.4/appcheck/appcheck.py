# Copyright (c) 2015 Codenomicon Ltd.
# License: MIT

from __future__ import absolute_import, division, print_function

import logging
import time
import os.path
from appcheck import exceptions
from appcheck.utils import TimeoutHTTPAdapter, file_sha1

import re
import requests
import requests.exceptions
import requests.adapters

logger = logging.getLogger(__name__)

# Default to Codenomicon online service
DEFAULT_APPCHECK_HOST = 'https://appcheck.codenomicon.com'
MAX_HTTP_RETRIES = 3  # attempts
HTTP_TIMEOUT = 60  # seconds

# From Appcheck API documentation
# https://appcheck.codenomicon.com/help/appcheck-api/
API_URL_MAP = {'upload': '{host}/appcheck/api/upload/{filename}',
               'result': '{host}/appcheck/api/app/{id_or_sha1}',
               'groups': '{host}/appcheck/api/groups/',
               'apps': '{host}/appcheck/api/apps/',
               'apps-group': '{host}/appcheck/api/apps/{group}'}


class Appcheck(object):
    """Appcheck HTTP API client"""

    STATUS_READY = 'R'

    def __init__(self, creds, host=None):
        """

        :param creds: Tuple (username, password)
        :param host: URI to appliance ('https://appliance.example.com'
                     [optional]
        """
        super(Appcheck, self).__init__()
        if not host:
            host = DEFAULT_APPCHECK_HOST
        self.host = host
        self.creds = creds
        self.session = requests.Session()

        # Set timeout for session
        adapter = TimeoutHTTPAdapter()
        adapter.timeout = HTTP_TIMEOUT
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _uri(self, target, **params):
        """Resolve URI
        :param target: Endpoint for which to get URI (internal)
        :param params: Endpoint specific parameters
        """
        route = API_URL_MAP[target]
        params.setdefault('host', self.host)
        return route.format(**params)

    def _retry_request(self, func, args=[], kwargs={},
                       max_retries=MAX_HTTP_RETRIES):
        """Upload with retry on failure

        Calls func(*args, **kwargs) and returns its output.

        If function returns an error we can retry, call function again,
        up to max_retries times.
        :param func: Function that sends HTTP request with requests
        :param args: arguments for func
        :param kwargs: keyword arguments for func
        :param max_retries: number of retries before exception
        """
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.HTTPError,
                    requests.exceptions.Timeout) as e:
                logger.info(("Connection error {0!r}, retrying "
                             "upload.").format(e))
                retry_delay = min(30, pow(2, attempt))
                time.sleep(retry_delay)
        else:  # No more retries
            error = "Data upload failed, out of retry attempts"
            logger.critical(error)
            raise exceptions.AppcheckException(error)

    def upload_file(self, file_path, display_name=None, group=None):
        """Upload file to Appcheck

        :param file_path: File to upload
        :param display_name: Name of uploaded file [optional]
        """
        if not display_name:
            display_name = os.path.basename(file_path)
        display_name = re.sub("[^\w._-]", "_", display_name)
        uri = self._uri('upload', filename=display_name)
        headers = {}
        if group:
            headers['Group-Appcheck'] = group

        def _upload_file():
            """Upload file to Appcheck, implementation"""
            with open(file_path, 'rb') as file_fd:
                return self.session.put(uri, data=file_fd, auth=self.creds,
                                        headers=headers)

        # Check if file already scanned by SHA1 - don't upload duplicates
        try:
            scanned_sha1 = file_sha1(file_path)
            result = self.get_result(id_or_sha1=scanned_sha1)
        except exceptions.ResultNotFound:  # upload as new
            r = self._retry_request(_upload_file)
            assert isinstance(r, requests.Response)
            self._raise_for_status(r)
            result = r.json()
        return result

    def get_result(self, id_or_sha1):
        """Get Appcheck scan result

        :param id_or_sha1: Appcheck scan ID or SHA1 checksum (hex string)
        """
        uri = self._uri('result', id_or_sha1=id_or_sha1)
        r = self._retry_request(self.session.get, [uri], {'auth': self.creds})
        assert isinstance(r, requests.Response)
        self._raise_for_status(r)
        return r.json()

    def delete(self, id_or_sha1):
        """Delete Appcheck scan result and scanned file

        :param id_or_sha1: Appcheck scan ID or SHA1 checksum (hex string)
        """
        uri = self._uri('result', id_or_sha1=id_or_sha1)
        r = self._retry_request(self.session.delete, [uri], {'auth': self.creds})
        self._raise_for_status(r)
        return r.json()

    def list_groups(self):
        """List groups"""
        uri = self._uri('groups')
        r = self._retry_request(self.session.get, [uri], {'auth': self.creds})
        self._raise_for_status(r)
        return r.json()

    def list_apps(self, group=None):
        """List apps, optionally by group
        :param group: Group name filter [optional]
        """
        if not group:
            uri = self._uri('apps')
        else:
            uri = self._uri('apps-group', group=group)

        r = self._retry_request(self.session.get, [uri], {'auth': self.creds})
        self._raise_for_status(r)
        return r.json()

    def _raise_for_status(self, response):
        """Check status code and raise error if not success
        :param response: Requests response object
        """
        if response.status_code == 200:
            pass
        elif response.status_code in [401, 403]:
            raise exceptions.InvalidLoginError("Access forbidden")
        elif response.status_code == 404:
            raise exceptions.ResultNotFound("Object was not found")
        else:
            raise exceptions.AppcheckException("Unhandled status code")
