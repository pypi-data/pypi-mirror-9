#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: usuario
# @Date:   2014-09-14 00:09:52
# @Last Modified by:   usuario
# @Last Modified time: 2014-09-15 22:36:41

import os
import sys
import subprocess as sub

import shutil as sh
import walking as wk
import tempfile as tmp

import logging as log

debug = True
verbose = True

if debug:
    log.basicConfig(level=log.DEBUG, format='%(message)s')

if verbose:
    log.basicConfig(level=log.INFO, format='%(message)s')

if sys.platform in ["win32"]:
    xpdf_path = os.path.join(os.curdir, 'bin', 'win', 'bin64')
    pdftopng = os.path.join(xpdf_path, 'pdftopng.exe')
    pdffonts = os.path.join(xpdf_path, 'pdffonts.exe')
elif sys.platform in ["darwin"]:
    xpdf_path = os.path.join(os.curdir, 'bin', 'mac', 'bin64')
    pdftopng = os.path.join(xpdf_path, 'pdftopng')
    pdffonts = os.path.join(xpdf_path, 'pdffonts')
    tesseract_binary = '/usr/local/bin/tesseract'
    log.debug(xpdf_path)


def main():
    dirpath = '/Users/usuario/Desktop'
    filepath = os.path.join(dirpath, '1.pdf')

    try:
        a = sub.check_output(pdffonts + ' ' + filepath, shell=True)
        print a.count('\n')
    except:
        pass

    temp_dir = tmp.mkdtemp()
    try:
        sub.call('open ' + temp_dir, shell=True)
    except:
        pass
    print temp_dir

    sh.copy2(filepath, temp_dir)
    options = [pdftopng, '-r 300 -aa no -gray',
               filepath, os.path.join(temp_dir, 'image')]
    options = ' '.join(options)
    print options
    try:
        sub.call(options, shell=True)
    except Exception, e:
        print e

    txt = tmp.NamedTemporaryFile(
        dir=temp_dir,
        delete=False)
    print txt.name

    for root, dirs, files in wk.walk(
            temp_dir,
            tfiles=['.png'],
            level=0):
        for f in files:
            p_ = os.path.join(root, f.name)
            o_ = os.path.join(root, 'output')
            cmd = [tesseract_binary, p_, o_, '-l', 'spa']
            try:
                sub.call(' '.join(cmd), shell=True)
            except:
                pass

            f_ = file(o_ + '.txt', 'r')
            for line in f_:
                txt.write(line)
            f_.close()

    txt.close()
    print os.path.exists(txt.name)
    print os.path.isfile(txt.name)
    # os.rename(txt.name, filepath+'99999.txt')

    # sh.copy2(txt.name, os.path.join(dirpath,filename+'.txt'))
    # sh.rmtree(temp_dir)


main()
