# -*- coding: utf-8 -*-
from StringIO import StringIO
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import tarfile
import time
import urllib

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python import log
from twisted.web.client import getPage
from twisted.web.error import Error
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.static import File

from .utils import safemembers


class Action(Resource):
    isLeaf = True
    needs_auth = True

    def __init__(self, site):
        assert hasattr(self, 'action_method')
        self.site = site
        if self.needs_auth:
            setattr(self, 'render_%s' % self.action_method, self.auth_wrapper)
        else:
            setattr(self, 'render_%s' %
                    self.action_method, self.noauth_wrapper)
        Resource.__init__(self)

    def noauth_wrapper(self, request):
        data = self.get_data_for_signature(request)
        data['access_id'] = request.getHeader('djeesefs-access-id')
        self.action_handler(request, **data)
        return NOT_DONE_YET

    def auth_wrapper(self, request):
        data = self.get_data_for_signature(request)
        deferred = self.verify_signature(request, data)

        def callback(success):
            if success:
                data['access_id'] = request.getHeader('djeesefs-access-id')
                self.action_handler(request, **data)
            else:
                request.setResponseCode(403)
                request.finish()

        def errback(reason):
            if isinstance(reason, Error):
                request.setResponseCode(reason.status)
            else:
                request.setResponseCode(400)
            request.finish()
            return reason
        deferred.addCallback(callback)
        deferred.addErrback(errback)
        return NOT_DONE_YET

    def verify_signature(self, request, data):
        return self.site.verify_signature(
            request.getHeader('djeesefs-access-id'),
            request.getHeader('djeesefs-signature'),
            data
        )

    def get_data_for_signature(self, request):
        return {'name': request.args['name'][0]}

    def action_handler(self, request, **kargs):
        raise NotImplementedError


class Delete(Action):
    action_method = 'POST'

    def action_handler(self, request, access_id, name):
        path = self.site.path(access_id, name)
        if os.path.exists(path):
            os.remove(path)
        else:
            request.setResponseCode(404)
        request.finish()


class Exists(Action):
    action_method = 'GET'
    needs_auth = False

    def action_handler(self, request, access_id, name):
        path = self.site.path(access_id, name)
        if os.path.exists(path):
            request.finish()
        else:
            request.setResponseCode(404)
            request.finish()


class Listdir(Action):
    action_method = 'GET'

    def action_handler(self, request, access_id, name):
        path = self.site.path(access_id, name)
        if os.path.exists(path):
            entries = os.listdir(path)
            files, directories = [], []
            for thing in entries:
                if os.path.isfile(os.path.join(path, thing)):
                    files.append(thing)
                else:
                    directories.append(thing)
            data = json.dumps([directories, files])
            request.write(data)
            request.finish()
        else:
            request.setResponseCode(404)
            request.finish()


class Size(Action):
    action_method = 'GET'
    needs_auth = False

    def action_handler(self, request, access_id, name):
        path = self.site.path(access_id, name)
        if os.path.exists(path):
            size = os.path.getsize(path)
            request.write(str(size))
            request.finish()
        else:
            request.setResponseCode(404)
            request.finish()


class Url(Action):
    action_method = 'GET'
    needs_auth = False

    def action_handler(self, request, access_id, name):
        path = self.site.path(access_id, name)
        if os.path.exists(path):
            request.write(self.site.url(access_id, name))
            request.finish()
        else:
            request.setResponseCode(404)
            request.finish()


class Save(Action):
    action_method = 'POST'
    chunk_size = 1 * 1024 * 1024  # 1MB

    def action_handler(self, request, access_id, name):
        if self.site.check_quota(access_id):
            path = self.site.path(access_id, name)
            parent = os.path.dirname(path)
            if not os.path.exists(parent):
                os.makedirs(parent)
            key = self.site.file_saver.new(access_id=access_id, path=path)
            data = {'chunk_size': self.chunk_size, 'key': key}
            request.write(json.dumps(data))
            request.finish()
        else:
            request.setResponseCode(400)
            request.finish()


class Upload(Action):
    action_method = 'POST'

    def get_data_for_signature(self, request):
        return {'key': request.args['key'][0]}

    def action_handler(self, request, access_id, key):
        chunk = request.args['chunk'][0]
        if not self.site.file_saver.contribute(access_id, key, chunk):
            request.setResponseCode(400)
        request.finish()


class Finish(Upload):

    def action_handler(self, request, access_id, key):
        self.site.file_saver.finish(access_id, key)
        request.finish()


class AvailableName(Action):
    action_method = 'GET'
    needs_auth = False

    def action_handler(self, request, access_id, name):
        path = self.site.path(access_id, name)
        base, ext = os.path.splitext(os.path.basename(path))
        parent = os.path.dirname(path)
        counter = 0
        while os.path.exists(path):
            counter += 1
            path = os.path.join(parent, '%s_%s%s' % (base, counter, ext))
        path = self.site.relpath(access_id, path)
        request.write(path)
        request.finish()


class CopyContainer(Action):
    """
    Makes a backup of this container.
    Removes all files currently inside this container.
    Copies the whole source container into this one.
    """
    action_method = 'POST'

    def get_data_for_signature(self, request):
        # the signed payload for the main verification request is both
        # the id of the source container and signature signed using the
        # source container secret.
        return {
            'source_id': request.args['source_id'][0],
            'source_signature': request.args['source_signature'][0],
        }

    def action_handler(self, request, access_id, source_id, source_signature):
        # The regular signature verification has already happened.
        # Now check if the signature for the source container is valid as well.
        source_data = {'source_id': source_id}
        deferred = self.site.verify_signature(
            source_id,
            source_signature,
            source_data
        )

        def callback(success):
            if success:
                # copy the container
                # blocking. I know :-(
                self.copy_container(
                    source_id=source_id,
                    destination_id=access_id)
                request.setResponseCode(200)
            else:
                request.setResponseCode(403)
            request.finish()

        def errback(reason):
            if isinstance(reason, Error):
                request.setResponseCode(reason.status)
            else:
                request.setResponseCode(400)
            request.finish()
            return reason
        deferred.addCallback(callback)
        deferred.addErrback(errback)
        return NOT_DONE_YET

    def copy_container(self, source_id, destination_id, make_backup=True):
        """
        Does the actual clone. Unfortunately this is a blocking operation.
        """
        # remove trailing slashes
        source_path = os.path.dirname(self.site.path(source_id, ''))
        destination_path = os.path.dirname(self.site.path(destination_id, ''))
        if os.path.exists(destination_path):
            if make_backup:
                backup_path = destination_path
                while os.path.exists(backup_path):
                    timestamp = str(datetime.datetime.now())\
                        .replace(' ', '_').replace(':', '-')
                    backup_path = u"%s.%s.backup" % (
                        destination_path,
                        timestamp,
                    )
                shutil.move(destination_path, backup_path)
            else:
                shutil.rmtree(destination_path)
        # copy source to destination
        if os.path.exists(source_path):
            # if the source directory doesn't exist, we don't have to do
            # anything, since the backuping already moved the old destination
            # directory, making its state consistent with the source (empty)
            shutil.copytree(source_path, destination_path)
        return True


class GetContainerArchive(Action):
    """
    Returns an archive containing a backup of this container.
    """
    action_method = 'POST'
    needs_auth = True

    def get_data_for_signature(self, request):
        return {}

    def action_handler(self, request, access_id):
        request.setHeader(b'content-type', b'application/octet-stream')
        tarball = tarfile.open(mode='w|gz', fileobj=request)
        path = os.path.dirname(self.site.path(access_id, ''))
        if os.path.exists(path):
            for item_name in os.listdir(path):
                item_path = os.path.join(path, item_name)
                tarball.add(item_path, item_name)
        tarball.close()
        request.finish()


class RestoreContainerArchive(Action):
    """
    Uploads an archive containing a backup of this container and
    restores it.
    WARNING: current container will be locally moved to a backup directory.
    """
    action_method = 'POST'
    needs_auth = False

    def get_data_for_signature(self, request):
        return {'content': request.args['content'][0]}

    def action_handler(self, request, access_id, content):
        path = os.path.dirname(self.site.path(access_id, ''))
        if os.path.exists(path):
            if os.listdir(path):
                backup_path = path
                while os.path.exists(backup_path):
                    timestamp = (str(datetime.datetime.now()).
                                 replace(' ', '_').replace(':', '-'))
                    backup_path = u"%s.%s.backup" % (path, timestamp)
                shutil.move(path, backup_path)
                os.mkdir(path)
        else:
            os.mkdir(path)
        tarball = tarfile.open(mode='r:gz', fileobj=StringIO(content))
        tarball.extractall(
            path, members=safemembers(path, tarball.getmembers()))
        tarball.close()
        request.finish()


class UploadedFile(object):

    def __init__(self, key, path, access_id, timeout, max_size, pop):
        self.key = key
        self.path = path
        self.access_id = access_id
        self.timeout = timeout
        self.max_size = max_size
        self.pop = pop
        self.fileobj = open(path, 'wb')
        self.size = 0
        self.timer = reactor.callLater(self.timeout, self.cancel)

    def check(self, access_id):
        log.msg("Checking access: %s==%s" % (access_id, self.access_id))
        return access_id == self.access_id

    def write(self, data):
        self.size += len(data)
        if self.size > self.max_size:
            log.msg("File size exceeded max size %s" % self.max_size)
            self.cancel()
            return False
        else:
            self.fileobj.write(data)
            self.timer.reset(self.timeout)
            return True

    def finish(self):
        self.fileobj.close()
        self.timer.cancel()
        self.pop(self.key)

    def cancel(self):
        self.fileobj.close()
        os.remove(self.path)
        self.pop(self.key)


class FileSaver(object):
    timeout = 60

    def __init__(self, site):
        self.site = site
        self.running = {}

    def genkey(self):
        return hashlib.md5(str(time.time()) + str(id(self))).hexdigest()

    def new(self, path, access_id):
        key = self.genkey()
        while key in self.running:
            key = self.genkey()
        self.running[key] = UploadedFile(
            key=key,
            path=path,
            access_id=access_id,
            timeout=self.timeout,
            max_size=self.site.max_file_size,
            pop=self.pop
        )
        return key

    def contribute(self, access_id, key, data):
        fobj = self.running[key]
        if fobj.check(access_id):
            return fobj.write(data)
        else:
            log.msg("Access to file %s denied for %s" % (key, access_id))
            return False

    def finish(self, access_id, key):
        fobj = self.running[key]
        if fobj.check(access_id):
            return fobj.finish()
        else:
            return False

    def pop(self, key):
        del self.running[key]


class Server(Site):
    """
    /delete -> deletes a file
    /exists -> 200 if exists, 404 if not
    /listdir -> Returns JSON list of [directories, files]
    /size -> Returns the size of the file as the response content in bytes
    /url -> Returns the URL of the file as the response content
    /content -> Serves the file. SHOULD NOT BE USED IN PRODUCTION!
    /save -> Prepares a file for saving, returns a JSON mapping {chunksize, key}
    /upload -> Uploads a chunk of maximum chunksize (see save) for a given key
    /finish -> Finishes the file upload for a given key
    /available-name -> Returns an available unused name for a given name.
    /copy-container -> Copies a other container into the current one.
    """
    du_pattern = re.compile(r'^(\d+)')

    def __init__(self, root_folder, root_url, auth_server, max_bucket_size, max_file_size):
        self.root_folder = root_folder
        self.root_url = root_url
        self.auth_server = auth_server
        self.max_bucket_size = max_bucket_size
        self.max_file_size = max_file_size
        self.file_saver = FileSaver(self)
        root = Resource()
        root.putChild('delete', Delete(self))
        root.putChild('exists', Exists(self))
        root.putChild('listdir', Listdir(self))
        root.putChild('size', Size(self))
        root.putChild('url', Url(self))
        root.putChild('content', File(self.root_folder))
        root.putChild('save', Save(self))
        root.putChild('upload', Upload(self))
        root.putChild('finish', Finish(self))
        root.putChild('available-name', AvailableName(self))
        root.putChild('copy-container', CopyContainer(self))
        root.putChild('get-container-archive', GetContainerArchive(self))
        root.putChild('restore-container-archive', RestoreContainerArchive(self))
        Site.__init__(self, root)

    def verify_signature(self, access_id, signature, data):
        url = '%s?%s' % (self.auth_server, urllib.urlencode(data))
        headers = {
            'djeesefs-access-id': access_id,
            'djeesefs-signature': signature,
        }
        deferred = Deferred()

        def callback(value):
            deferred.callback(True)

        def errback(reason):
            if isinstance(reason, Error):
                if reason.status == 403:
                    deferred.callback(False)
                else:
                    deferred.errback(reason)
            else:
                deferred.errback(reason)
            return reason
        getPage(url, headers=headers).addCallback(callback).addErrback(errback)
        return deferred

    def path(self, access_id, name):
        return os.path.join(self.root_folder, access_id, name.lstrip('/'))

    def relpath(self, access_id, fullpath):
        root = os.path.join(self.root_folder, access_id)
        return os.path.relpath(fullpath, root)

    def check_quota(self, access_id):
        root = os.path.join(self.root_folder, access_id)
        if not os.path.exists(root):
            os.makedirs(root)
        output = subprocess.check_output(['du', '-s', root])
        current_size = int(self.du_pattern.match(output).group(1))
        return current_size < self.max_bucket_size

    def url(self, access_id, name):
        return '%s/%s/%s' % (self.root_url, access_id, name)
