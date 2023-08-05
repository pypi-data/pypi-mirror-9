# -*- coding: utf-8 -*-
from StringIO import StringIO
from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from fs.client import SyncClient
import os


class DjeeseFile(File):
    def __init__(self, storage, name, mode):
        self._storage = storage
        self.name = name
        self.mode = mode
        self._is_dirty = False
        self._file = StringIO()
        self._active = False
    
    @property
    def file(self):
        if not self._active:
            self._file = StringIO(self._storage.get_content(self.name))
            self._active = True
        return self._file

    @property
    def size(self):
        if not hasattr(self, '_size'):
            self._size = self._storage.size(self.name)
        return self._size
    
    def seek(self, pos, mode=os.SEEK_SET):
        self.file.seek(pos, mode)

    def read(self, num_bytes=None):
        if not self._active:
            self._file = StringIO(self._storage.get_content(self.name))
            self._active = True
        return self.file.read(num_bytes)

    def write(self, content):
        if 'w' not in self.mode:
            raise AttributeError("File was opened for read-only access.")
        if not self._active:
            self._file = StringIO(content)
        self._active = True
        self._is_dirty = True
        self.file.write(content)

    def open(self, mode=None):
        if not self.closed:
            self.seek(0)
        elif self.name and self._storage.exists(self.name):
            # no need to do anything. the file is lazily opened when accessing self.file
            pass
        else:
            raise ValueError("The file cannot be reopened.")

    def close(self):
        if self._is_dirty:
            self._storage._save(self.name, self)
        if self._active:
            self.file.close()
            self._active = False


class DjeeseFSStorage(Storage):
    def __init__(self):
        self.client = SyncClient(settings.DJEESE_STORAGE_ID, settings.DJEESE_STORAGE_KEY, settings.DJEESE_STORAGE_HOST)

    def delete(self, name):
        self.client.delete(name)

    def exists(self, name):
        return self.client.exists(name)

    def listdir(self, path):
        return self.client.listdir(path)

    def size(self, name):
        return self.client.size(name)

    def url(self, name):
        return self.client.url(name)

    def _open(self, name, mode='rb'):
        return DjeeseFile(self, name, mode)
    
    def _save(self, name, content):
        content.seek(0)
        self.client.save(name, content)
        return name
        
    def get_valid_name(self, name):
        return self.client.get_valid_name(name)
    
    def get_available_name(self, name):
        return self.client.get_available_name(name)
    
    def get_content(self, name):
        return self.client.get_content(name)
