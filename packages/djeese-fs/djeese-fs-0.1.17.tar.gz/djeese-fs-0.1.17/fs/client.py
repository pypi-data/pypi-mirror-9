# -*- coding: utf-8 -*-
import hashlib
import json
import os
import urllib
import urllib2

from django.utils.encoding import smart_str

from fs.security import sign


class DjeeseFSClientException(Exception):
    pass


class FancyRequest(urllib2.Request):
    """
    Simple subclass of urllib2.Request that allows you to set HTTP method
    """
    def __init__(self, url, method="GET", data=None, headers=None,
                 origin_req_host=None, unverifiable=False):
        urllib2.Request.__init__(self, url, data=data, headers=headers or {},
                                 origin_req_host=origin_req_host, unverifiable=unverifiable)
        self.method = method

    def get_method(self):
        return self.method


class FancyResponse(object):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def raise_for_status(self):
        if not self.status_code == 200:
            raise DjeeseFSClientException(u"HTTP %s: %s" % (self.status_code, self.content))

    @property
    def ok(self):
        return self.status_code == 200


class SyncClient(object):
    '''
    Synchronouse (blocking) client
    '''
    def __init__(self, access_id, access_key, host):
        self.access_id = str(access_id)
        self.access_key = str(access_key)
        self.host = host
        self._opener = urllib2.build_opener()
        self._opener.addheaders = [
            ('djeesefs-access-id', self.access_id),
            ('User-agent', 'djeese-fs-client')
        ]

    def _sign(self, data, keys=None):
        if keys is not None:
            data = dict((k, v) for k, v in data.items() if k in keys)
        return sign(self.access_key, data)

    def _get_url(self, method):
        return '/'.join([self.host.rstrip('/'), method.lstrip('/')])

    def _request(self, method, url, data=None, headers=None):
        headers = headers or {}
        data_urlencoded = urllib.urlencode(data) if data else None
        request = FancyRequest(url, method, data=data_urlencoded, headers=headers)
        try:
            response = self._opener.open(request)
        except urllib2.HTTPError as e:
            return FancyResponse(e.code, e.read())
        return FancyResponse(response.getcode(), response.read())

    def _post(self, method, data, keys=None):
        headers = {
            'djeesefs-signature': self._sign(data, keys),
        }
        url = self._get_url(method)
        return self._request("POST", url, data=data, headers=headers)

    def _get(self, method, params, keys=None):
        headers = {
            'djeesefs-signature': self._sign(params, keys),
        }
        url = self._get_url(method)
        if params:
            url = '%s?%s' % (url, urllib.urlencode(params))
        return self._request("GET", url, headers=headers)

    def delete(self, name):
        data = {'name': name}
        response = self._post('delete', data)
        return response.ok

    def exists(self, name):
        params = {'name': name}
        response = self._get('exists', params)
        return response.ok

    def listdir(self, path):
        params = {'name': path}
        response = self._get('listdir', params)
        response.raise_for_status()
        return json.loads(response.content)

    def size(self, name):
        params = {'name': name}
        response = self._get('size', params)
        response.raise_for_status()
        return int(response.content)

    def url(self, name):
        params = {'name': name}
        response = self._get('url', params)
        if not response.ok:
            return ''
        return response.content

    def get_content(self, name):
        url = self.url(name)
        response = self._request("GET", url)
        if not response.ok:
            return ''
        return response.content

    def save(self, name, fileobj):
        fileobj.seek(0)
        data = {'name': name}
        response = self._post('save', data)
        response.raise_for_status()
        info = json.loads(response.content)
        key, chunk_size = info['key'], info['chunk_size']
        while True:
            data = {'key': key}
            chunk = fileobj.read(chunk_size)
            if chunk:
                data['chunk'] = chunk
                response = self._post('upload', data, keys=['key'])
                response.raise_for_status()
            else:
                response = self._post('finish', data)
                response.raise_for_status()
                break
        fileobj.seek(0)
        return True

    def get_valid_name(self, name):
        name, ext = os.path.splitext(name)
        return '%s%s' % (hashlib.md5(smart_str(name)).hexdigest(), ext)

    def get_available_name(self, name):
        params = {'name': name}
        response = self._get('available-name', params)
        response.raise_for_status()
        return response.content

    def copy_container(self, source_access_id, source_access_key):
        """
        Copies the contents of another container into this one.
        Warning: Deletes EVERYTHING inside the current container!

        Requires the access credentials of the source container.
        """
        # we additionally sign our source container data with
        # the source container secret. The server can then
        # check both signatures to verify that the caller has
        # knowledge of the secrets for both containers.
        data = {'source_id': source_access_id}
        data['source_signature'] = sign(source_access_key, data)
        response = self._post('copy-container', data)
        response.raise_for_status()
        return response.ok

    def get_container_archive(self, fobj):
        """
        Returns an archive containing a backup of this container.
        """
        data = {}
        response = self._post('get-container-archive', data)
        response.raise_for_status()
        fobj.write(response.content)
        return True

    def restore_container_archive(self, content):
        """
        Uploads an archive containing a backup of this container and
        restores it.
        WARNING: current container will be locally moved to a backup directory.
        """
        data = {'content': content}
        response = self._post('restore-container-archive', data)
        response.raise_for_status()
        return True
