# -*- coding: utf-8 -*-
import os


def resolved(path):
    return os.path.realpath(os.path.abspath(path))


def safe_path(path, base):
    return resolved(os.path.join(base, path)).startswith(base)


def safe_link(info, base):
    link_base = resolved(os.path.join(base, os.path.dirname(info.name)))
    return safe_path(info.linkname, link_base)


def safemembers(base_path, members):
    base = resolved(base_path)

    for finfo in members:
        if not safe_path(finfo.name, base):
            print >>os.stderr, finfo.name, "is blocked (illegal path)"
        elif finfo.issym() and not safe_link(finfo, base):
            print >>os.stderr, finfo.name, "is blocked: Hard link to", finfo.linkname
        elif finfo.islnk() and not safe_link(finfo, base):
            print >>os.stderr, finfo.name, "is blocked: Symlink to", finfo.linkname
        else:
            yield finfo
