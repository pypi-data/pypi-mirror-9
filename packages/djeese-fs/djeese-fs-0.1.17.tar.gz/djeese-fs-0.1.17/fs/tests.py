# -*- coding: utf-8 -*-
from fs.client import SyncClient
from fs.server import Server
from twisted.internet import reactor, threads
from twisted.internet.base import DelayedCall
from twisted.internet.defer import DeferredList
from twisted.trial import unittest
from twisted.web.resource import Resource
from twisted.web.server import Site
import shutil
import tempfile


class TestingAuth(Resource):
    isLeaf = True
    
    def __init__(self, site):
        self.site = site
        Resource.__init__(self)
    
    def render_GET(self, request):
        if not self.site.check():
            request.setResponseCode(403)
        return ''

class TestingAuthServer(Site):
    def __init__(self):
        self.allow = True
        Site.__init__(self, TestingAuth(self))
    
    def check(self):
        return self.allow


DelayedCall.debug = True

class DjeeseFSTests(unittest.TestCase):
    def setUp(self):
        self.root_folder = tempfile.mkdtemp()
        self.auth_server = TestingAuthServer()
        self.auth_port = reactor.listenTCP(0, self.auth_server, interface="127.0.0.1")
        self.access_id = 'accessid'
        self.access_key = 'accesskey'
        self.server = Server(
            root_folder=self.root_folder,
            root_url='http://127.0.0.1/',
            auth_server='http://127.0.0.1:%s/' % self.auth_port.getHost().port,
            max_file_size=10 * 1024 * 1024,
            max_bucket_size=1 * 1024 * 1024 * 1024
        )
        self.port = reactor.listenTCP(0, self.server, interface="127.0.0.1")
        self.server.root_url = 'http://127.0.0.1:%s/' % self.port.getHost().port
        self.client = SyncClient(self.access_id, self.access_key, self.server.root_url)

    def tearDown(self):
        shutil.rmtree(self.root_folder)
        self.server.stopFactory()
        self.auth_server.stopFactory()
        return DeferredList([self.port.stopListening(), self.auth_port.stopListening()])
    
    def _call_client(self, method, *args, **kwargs):
        client_method = getattr(self.client, method)
        return threads.deferToThread(client_method, *args, **kwargs)
    
    def test_not_exists(self):
        def cb(ok):
            self.assertFalse(ok)
        return self._call_client('exists', 'test.jpg').addCallback(cb)


# class TestDjeeseFSCopyContainer(TestDjeeseFS):
#     def setUp(self):
#         super(TestDjeeseFSCopyContainer, self).setUp()
#         self.source_access_id = 'sourceaccessid'
#         self.source_access_key = 'sourceaccesskey'
#         self.souce_client = SyncClient(
#             self.source_access_id, self.source_access_key, self.server.root_url)
#
#     def create_sample_data(self):
#         # create a source folder
#         file_paths = [
#             '/a/folder/file.txt',
#             '/file.txt',
#             '/.otherfile',
#             '/.otherfolder/anotherfile.txt',
#             '/.otherfolder/.anotherfile.txt',
#         ]
#         for file_path in file_paths:
#             dummy_file = StringIO.StringIO()
#             dummy_file.write('some content')
#             self.client.save(file_path, dummy_file)
#
#         # create destination folder
#         file_paths = [
#             '/a/asfas/file.txt',
#             '/fiassdle.txt',
#             '/.othecccrfile',
#             '/.othexsrfolder/anotherfile.txt',
#             '/.otherfolder/.anotheaarfile.txt',
#         ]
#         for file_path in file_paths:
#             dummy_file = StringIO.StringIO()
#             dummy_file.write('some content')
#             self.souce_client.save(file_path, dummy_file)
#
#
#     def test_copy_container(self):
#         self.create_sample_data()
#         source_path = self.server.path(self.source_access_key)
#         destination_path = self.server.path(self.access_id)
#         assert len(filecmp.dircmp(source_path, destination_path).same_files()) == 0
#
#         def cb(ok):
#             self.assertTrue(ok)
#             dcmp = filecmp.dircmp(source_path, destination_path)
#             self.assertEqual(len(dcmp.diff_files()), 0, 'files in cloned directory differ')
#             self.assertEqual(len(dcmp.common()), len(dcmp.left_list()), 'directories in cloned directory differ')
#         self._call_client(
#             'copy-container',
#             self.source_access_id, self.source_access_key
#         ).addCallback(cb)

