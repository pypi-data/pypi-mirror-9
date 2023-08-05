#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: usuario
# @Date:   2014-09-05 07:45:22
# @Last Modified by:   Jonathan Prieto 
# @Last Modified time: 2014-10-07 15:35:23

__author__ = 'Jonathan Prieto'
import os
import sys
import scandir
from latin2ascii import enconding_path

from kitchen.text.converters import getwriter, to_unicode

UTF8Writer = getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

debug = True

__version__ = '0.1.1'
__all__ = ['walk', 'size_str', 'walk_size']


def walk(top, topdown=True, onerror=None, flinks=False, tfiles=['*'], sdirs=[],
         level=0):
    """
    :param top: node root of the depth-first search on tree directory
    :param topdown: if yield results, to modify in any iteration
    :param onerror: a function to handle the errors
    :param flinks: allow to continue search in subdirectories (not symlinks)
    :param tfiles: types of files allowed to show, p.e .pdf, .docx, .txt
    :param sdirs: don't search in these directory ( a full path system adress)
    :param level: max level of depth reached for search walklevel
    :return: a generator with values, top, root-path and dirs, nondirs
                    ( class from scandir library )
    """
    
    top = enconding_path(top)
        
    try:
        level = int(level)
    except ValueError:
        level = 0

    dirs = []
    nondirs = []
    symlinks = set()

    sdirs_ = sdirs[:]
    sdirs = []
    for d in sdirs_:
        d = d.rstrip(os.path.sep)
        if os.path.isdir(d):
            sdirs.append(d)
    del sdirs_
    try:
        for entry in scandir.scandir(top):
            try:
                if not entry.name.startswith('.'):
                    if entry.is_dir() and \
                            not os.path.join(top, entry.name) in sdirs:
                        dirs.append(entry)
                    elif tfiles == ["*"]:
                        nondirs.append(entry)
                    elif os.path.splitext(entry.name)[1].lower() in tfiles:
                        nondirs.append(entry)
            except OSError:
                nondirs.append(entry)
            try:
                if entry.is_symlink():
                    symlinks.add(entry)
            except OSError:
                pass
    except OSError as error:
        if onerror is not None:
            onerror(error)
        return

    if topdown:
        yield top, dirs, nondirs

        if level > 0:
            for entry in dirs:
                if flinks or entry.name not in symlinks:
                    npath = os.path.join(top, entry.name)
                    for x in walk(npath, topdown, onerror, flinks, tfiles, sdirs, level - 1):
                        yield x

    if not topdown:
        yield top, dirs, nondirs


def size_str(bytes, precision=1):
    """
    http://code.activestate.com/recipes/577081-humanized-
    representation-of-a-number-of-bytes/
    """
    bytes = long(bytes)
    abbrevs = (
        (1 << 50L, 'PB'),
        (1 << 40L, 'TB'),
        (1 << 30L, 'GB'),
        (1 << 20L, 'MB'),
        (1 << 10L, 'kB'),
        (1, 'bytes')
    )
    if bytes == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if bytes >= factor:
            break
    return '%.*f %s' % (precision, bytes / factor, suffix)


def walk_size(dir='', sdirs=[], level=0, tfiles=['*']):
    total_size = 0
    count_files = 0
    try:
        for root, dirs, files in walk(dir, sdirs=sdirs, level=level, tfiles=tfiles):
            for f in files:
                filepath = os.path.join(root, f.name)
                total_size += os.path.getsize(filepath)
                count_files += 1
    except Exception, e:
       print e
    return [count_files, total_size]
