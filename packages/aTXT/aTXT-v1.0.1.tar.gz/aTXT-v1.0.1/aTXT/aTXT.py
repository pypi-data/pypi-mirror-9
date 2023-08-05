# @Author: Jonathan S. Prieto
# @Date:   2015-01-15 18:49:00
# @Last Modified by:   Jonathan Prieto 
# @Last Modified time: 2015-01-15 19:37:20
#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division

from version import __version__ as version

import os
import tempfile as tmp
import walking as wk

import docx.docx as docx
from pdfminer import layout, pdfinterp, converter, pdfpage
from latin2ascii import enconding_path, remove_accents, latin2ascii
import sys
import subprocess as sub
import shutil as sh
import logging as log
import zipfile as zp
import datetime

from docopt import docopt
import usagedoc

from kitchen.text.converters import getwriter, to_unicode

__version__ = version

UTF8Writer = getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

verbose = False
DEBUG = False

if DEBUG:
    log_filename = "LOG.txt"
else:
    log_filename = (
        "aTXT" + datetime.datetime.now().strftime("-%Y_%m_%d_%H-%M") + ".txt")

PATH_BIN = os.path.dirname(os.path.abspath(__file__))


class Debug(object):

    def __init__(self, log_path=log_filename, debug=False):
        self.debug = debug
        if verbose:
            log.basicConfig(filename=log_path,
                            filemode='w',
                            level=log.DEBUG,
                            format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%y %I:%M:%S %p | '
                            )

    def write(self, msg, *args):
        if not self.debug:
            pass
        try:
            if type(msg) is type(lambda x: x):
                log.debug(msg.func_name)
                for arg in args:
                    log.debug("\t{0}".format(args))
            else:
                log.debug(msg + ' ' + ' '.join(args))
        except:
            log.debug(msg)
            for arg in args:
                log.debug(arg)


class File(object):
    _debug = Debug()

    def __init__(self, path, debug=None):
        self.debug('FileClass initialitation with' + path)
        if not debug:
            self._debug = debug

        self.path = enconding_path(path)
        self.debug('Setting basename, name, extension, dirname')
        try:
            self.basename = os.path.basename(self.path)
            self.name, self.extension = os.path.splitext(self.basename)
            self.extension = self.extension.lower()
            self.dirname = os.path.dirname(self.path)
        except Exception, e:
            self.debug(e)
            self.debug("*" * 50)
        self.to_str()

    def debug(self, *args):
        self._debug.write(*args)

    def remove(self):
        if os.path.isfile(self.path):
            try:
                sh.remove(self.path)
                self.debug("File deleted", self.path)
                return 1
            except:
                self.debug("*", "Failed remove file", self.path)
        return 0

    def size(self):
        if not os.path.isfile(self.path):
            self.debug("is not a file", self.path)
            return 0
        size = os.path.getsize(self.path)
        return size

    def move(self, topath=None):
        if not topath:
            return False
        try:
            self.debug("moving from", self.path, "to", topath)
            sh.copy2(self.path, topath)
            self.debug("file moved")
        except Exception, e:
            self.debug("*", "fail moving file", e)
        return topath

    def to_str(self):
        s = [self.basename, self.path, self.size(), os.path.isdir(
            self.dirname), os.path.isfile(self.path)]
        test = os.path.isdir(self.dirname), os.path.isfile(self.path)
        self.debug("test: (exist dirname, exist filepath)", test)
        return '\n'.join(map(enconding_path, s))

    def create_temp(self, tempdir=None):
        if not tempdir or not os.path.exists(tempdir):
            try:
                self.debug("creating a temporary directory")
                self._tempdir = tmp.mkdtemp()
                self.debug(self._tempdir)
            except Exception, e:
                self.debug("* fail to create directory", e)
        else:
            self._tempdir = tempdir
        try:
            self.debug(
                "from temp()", "copy ", self.basename, "to ", self._tempdir)
            sh.copy2(self.path, self._tempdir)
        except:
            self.debug("* fail to copy of", self.basename, "to", self._tempdir)

        self._name = "temp"
        self._basename = self._name + self.extension
        self._path = os.path.join(self._tempdir, self._basename)
        try:
            self.debug("change name for security: " + self._basename)
            os.rename(os.path.join(self._tempdir, self.basename), self._path)
        except Exception, e:
            self.debug("fail to change name to 1.pdf", e)

    def remove_temp(self):
        try:
            self.debug("deleting temp directory", self._tempdir)
            sh.rmtree(self._tempdir)
        except:
            self.debug("fail delete", self._tempdir)
            self.debug("please remove manually")
        try:
            del self._name
            del self._basename
            del self._path
        except:
            pass
            return False
        return True


class aTXT(object):
    overwrite = True
    uppercase = False
    savein = 'TXT'
    hero_docx = 'xml'
    hero_pdf = 'xpdf'
    msword = None

    def __init__(self, debug=False, lang='spa', msword=None, use_temp=False):
        self._debug = debug
        if not debug:
            self._debug = Debug()

        self.debug("aTXT v" + __version__)
        self.debug("Set Configuration")

        # basic setting
        self.lang = lang
        self.use_temp = use_temp
        if not msword:
            try:
                self.debug("importing win32")
                from win32com import client
                self.msword = client.DispatchEx("Word.Application")
                self.msword.Visible = False
                self.debug('Successful Dispatching of Word.Application')
            except:
                self.debug("It's not available win32com")

        # TESSERACT AND OTHERS BINARIES
        self.tesseract_required = "3.02.02"
        self.xpdf_required = "3.04"

        if sys.platform in ["win32"]:
            self.debug('set thirdy paths for win32')
            try:
                self.xpdf_path = os.path.join(PATH_BIN, 'bin', 'win', 'bin32')
                self.pdftotext = os.path.join(self.xpdf_path, 'pdftotext.exe')
                self.pdftopng = os.path.join(self.xpdf_path, 'pdftopng.exe')
                self.pdffonts = os.path.join(self.xpdf_path, 'pdffonts.exe')
            except:
                self.debug('fail set thirdy paths for win32')

        elif sys.platform in ["darwin"]:
            self.debug('set thirdy paths for darwin mac')
            try:
                self.xpdf_path = os.path.join(PATH_BIN, 'bin', 'mac', 'bin64')
                self.pdftotext = os.path.join(self.xpdf_path, 'pdftotext')
                self.pdftopng = os.path.join(self.xpdf_path, 'pdftopng')
                self.pdffonts = os.path.join(self.xpdf_path, 'pdffonts')
            except:
                self.debug('fail set thirdy paths for darwin mac')

        if not os.path.exists(self.pdftotext):
            self.debug("not exists", self.pdftotext)
        if not os.path.exists(self.pdftopng):
            self.debug("not exists", self.pdftopng)

        self.debug('set path for tesseract OCR')

        if str(os.name) == 'nt':  # windows 7 or later
            self.tesseract_binary = '"c:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"'
        else:
            self.tesseract_binary = "/usr/local/bin/tesseract"
            if self.debug:
                try:
                    self.debug(
                        "trying to find tesseract binary by which command")
                    self.tesseract_binary = sub.check_output(
                        ['which', 'tesseract']).rstrip()
                except:
                    self.debug("*", "fail with which commnand")
                self.debug("set tesseract: ", self.tesseract_binary)

        self.debug("Ready to start any conversion")
        self.debug("")

    def close(self):
        self.debug('Close aTXT ' + ':' * 50)
        try:
            self.msword.Quit()
        except:
            pass
        self.debug('Finish work')

    def debug(self, *args):
        self._debug.write(*args)
        if verbose:
            print args

    def make_dir(self, path):
        try:
            os.makedirs(path)
            self.debug('\tDirectory created:', path)
        except:
            pass

        if not os.access(path, os.W_OK):
            self.debug('\tDirectory without permissions: %s' % path)
            return 0
        return 1

    def remove_dir(self, path):
        if os.path.isdir(path):
            try:
                sh.rmtree(path)
                self.debug("Directory removed", path)
                return 1
            except:
                self.debug("*", "Failed remove directory", path)
        return 0

    def set(self, filepath, savein='TXT', overwrite='True', uppercase='False'):

        self.debug("Set configuration for file:")
        try:
            del self.file
        except Exception, e:
            self.debug("del file in set() method.")

        # FILEPATH

        try:
            self.file = File(filepath, debug=self._debug)
            self.debug("Successful instance of file")
        except Exception, e:
            self.debug("Fail creating File object")
            self.debug(e)
            self.debug("*" * 50)
        # SAVE IN PATH
        self.savein = enconding_path(savein)

        if not os.path.isdir(self.savein):
            self.debug('Directory Save In is not a directory')
            self.savein = os.path.join(self.file.dirname, self.savein)
            self.debug("savein: " + self.savein)
            try:
                self.make_dir(self.savein)
            except Exception, e:
                self.debug("Fail make_dir")
                self.debug(e)
                self.debug("*" * 50)

        self.debug('File will be save in', self.savein)
        if type(overwrite) == type(True):
            self.overwrite = overwrite

        if type(uppercase) == type(True):
            self.uppercase = uppercase

        self.txt = None
        try:
            path = os.path.join(self.savein,  self.file.name + ".txt")
            self.debug("Creating .txt file", path)
            self.txt = File(path, self._debug)
        except Exception, e:
            self.debug("\tCreate txt file fail", e)

    def from_docx(self, hero='xml'):

        self.debug('')
        self.debug('[new conversion]')
        self.debug('\tfrom_docx starting')

        if not self.overwrite and os.path.exists(self.txt.path):
            return self.txt.path

        try:
            self.debug("\tfrom_docx", "creating file", self.txt.path)
            self.txt.doc = open(self.txt.path, "w")
            self.debug("\tfrom_docx", "file created", self.txt.path)
        except Exception, e:
            self.debug("\t*from_docx fail to create", self.txt.path)
            self.debug(e)
            return ''

        self.debug('\tfrom_docx', 'hero =', hero)
        if hero == "python-docx":
            self.debug('\tfrom_docx using python-docx')
            doc_ = docx.opendocx(self.file.path)
            for line in docx.getdocumenttext(doc_):
                try:
                    line = latin2ascii(unicode(line, 'utf-8', 'ignore'))
                except:
                    pass
                try:
                    line = line.encode('utf-8', 'replace')
                except:
                    pass
                self.txt.doc.write(line + '\n')
            self.txt.doc.close()
            self.debug("\tfinish work with .docx")
            return self.txt.path
        try:
            self.txt.doc.write(self.from_docx_())
        except Exception, e:
            self.debug("\t* from_docx_ error", e)
            return ''
        return self.txt.path

    def from_docx_(self):
        '''
         http://stackoverflow.com/questions/42482/best-way-to-extract-text-from-a-word-doc-
         without-using-com-automation
        '''
        try:
            from xml.etree.cElementTree import XML
        except:
            self.debug("*", "from_docx_ failed XML")
            from xml.etree.ElementTree import XML

        WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        PARA = WORD_NAMESPACE + 'p'
        TEXT = WORD_NAMESPACE + 't'

        document = zp.ZipFile(self.file.path)

        self.debug("\tfrom_docx_ zipfile open document")
        xml_content = document.read('word/document.xml')

        self.debug("\ttfrom_docx_ close document")
        document.close()

        self.debug("\tfrom_docx_ XML(xml_content)")
        tree = XML(xml_content)
        paragraphs = []

        self.debug("\tfrom_docx_ tree.iterator")
        for paragraph in tree.getiterator(PARA):
            line = [
                node.text for node in paragraph.getiterator(TEXT) if node.text]
            line = ''.join(line)
            try:
                line = latin2ascii(unicode(line, 'utf-8', 'ignore'))
            except:
                pass
            try:
                line = line.encode('utf-8', 'replace')
            except:
                pass
            if line:
                paragraphs.append(line)
        return '\n\n'.join(paragraphs)

    def from_doc(self):

        self.debug('')
        self.debug('[new conversion]')
        self.debug('\tfrom_doc starting')

        if not self.overwrite and os.path.exists(self.txt.path):
            return self.txt.path

        cerrar = False
        if not self.msword:
            try:
                self.debug("Dispatching Word by from_doc")
                # Using DispatchEx for an entirely new Word instance
                self.msword = client.DispatchEx("Word.Application")
                self.msword.Visible = False
                cerrar = True
            except Exception, e:
                self.debug("fail Dispatching Word.Application")
                return ''

        try:
            self.debug(
                'from_doc', "exists temp file: " + str(os.path.exists(self.file._path)))
            self.debug("from_doc", "opening file", self.file._path)
            # http://msdn.microsoft.com/en-us/library/bb216319%28office.12%29.aspx
            # wb = self.msword.Documents.Open(
            wb = self.msword.Documents.OpenNoRepairDialog(
                FileName=self.file._path,
                ConfirmConversions=False,
                ReadOnly=True,
                AddToRecentFiles=False,
                # PasswordDocument,
                # PasswordTemplate,
                Revert=True,
                # WritePasswordDocument,
                # WritePasswordTemplate,
                # Format,
                # Encoding,
                Visible=False,
                OpenAndRepair=True,
                # DocumentDirection,
                NoEncodingDialog=True
            )

        except Exception, e:
            self.debug("from_doc", "fail open file with Word", e)
            self.txt.remove()
            return ''

        try:
            self.debug("from_doc", "saving file", self.txt.path)
            wb.SaveAs(self.txt.path, FileFormat=2)
        except Exception, e:
            self.debug("from_doc", "fail to save file", e)
            self.txt.remove()
            return ''

        self.debug("from_doc", "closing file")
        wb.Close()
        if cerrar:
            self.msword.Quit()
        return self.txt.path

    def from_pdf(self, hero='xpdf'):

        self.debug('')
        self.debug('[new conversion]')
        self.debug('starting pdf to txt')

        if not self.overwrite and os.path.exists(self.txt.path):
            self.debug(self.txt.path, "yet exists")
            return self.txt.path

        try:
            self.debug("from_pdf opening to read", self.file._path)
            doc_ = file(self.file._path, 'rb')
        except Exception, e:
            self.debug("* from_pdf", e)
            return ''
        try:
            self.debug("from_pdf creating to write", self.txt.path)
            f = file(self.txt.path, "wb")
            self.debug("from_pdf created", self.txt.basename)
        except Exception, e:
            self.debug("* from_pdf", e)
            return ''

        self.debug("\thero:" + hero)

        if hero == "pdfminer":
            try:
                self.debug("from_pdf", "creating PDFResourceManager")
                resourceman = pdfinterp.PDFResourceManager()
                self.debug("from_pdf",  "using TextConverter")
                device = converter.TextConverter(
                    resourceman, f, laparams=layout.LAParams())
                self.debug("from_pdf",  "using PDFPageInterpreter")
                interpreter = pdfinterp.PDFPageInterpreter(resourceman, device)
                for page in pdfpage.PDFPage.get_pages(doc_):
                    interpreter.process_page(page)
                f.close()
                device.close()
            except Exception, e:
                self.debug("* from_pdf", e)
                return ''

        if hero == "xpdf":
            try:
                self.debug("from_pdf", "xpdf")
                options = [self.pdftotext, self.file._path, '-']

                self.debug("from_pdf", options)
                self.debug("from_pdf", "starting subprocess")
                output = sub.call(options, stdout=f)
                self.debug("from_pdf", "finished subprocess")
                if output == 0:
                    self.debug("from_pdf", "No error.")
                elif output == 1:
                    self.debug("from_pdf", "Error opening a PDF file.")
                elif output == 2:
                    self.debug("from_pdf", "Error opening an output file.")
                elif output == 3:
                    self.debug(
                        "from_pdf", "Error related to PDF permissions.")
                else:
                    self.debug("from_pdf", "Other error.")
            except Exception, e:
                self.debug("*", "from_pdf", e)
        f.close()
        doc_.close()
        return self.txt.path

    def need_ocr(self):
        try:
            if not self.file._path:
                self.file.create_temp()
            cmd = self.pdffonts + ' ' + self.file._path
        except:
            cmd = self.pdffonts + ' ' + self.file.path
            self.debug("cmd", cmd)

        o_ = ''
        try:
            self.debug("OCR?")
            o_ = sub.check_output(cmd, shell=True)

            self.debug("using pdffonts")
            self.debug("\n" + o_)
            if o_.count('yes') or o_.count('Type') or o_.count('no'):
                self.debug('ORC is not necessary!')
                return False, o_

        except Exception, e:
            self.debug("* from_pdf_ocr", "looks like OCR is necessary")
            self.debug(e)
        return True, o_

    def from_pdf_ocr(self, hero="xpdf"):

        self.debug('')
        self.debug('[new conversion]')
        self.debug('starting pdf_ocr to txt')

        if not self.overwrite and os.path.exists(self.txt.path):
            self.debug(self.txt.path, "yet exists")
            return self.txt.path

        necessary_ocr, out_info = self.need_ocr()
        if not necessary_ocr:
            return self.from_pdf(hero)

        options = [self.pdftopng,
                   self.file._path,
                   os.path.join(self.file._tempdir, 'image')]

        options = ' '.join(options)
        self.debug("from_pdf_ocr", "set options pdftopng:", options)
        try:
            self.debug("from_pdf_ocr", "calling pdftopng")
            sub.call(options, shell=True)
            # sub.call(options)
        except Exception, e:
            self.debug("*", "from_pdf_ocr", "fail to use pdftopng")
            self.debug(e)
            return ''

        txt = open(self.txt.path, "w")

        page = 1
        for root, dirs, files in wk.walk(self.file._tempdir, tfiles=['.png']):
            for f in files:
                p_ = os.path.join(root, f.name)
                o_ = os.path.join(root, 'output')
                cmd = [self.tesseract_binary, p_, o_, '-l', 'spa']
                cmd = ' '.join(cmd)
                try:
                    self.debug("from_pdf_ocr", "processing page " + str(page))
                    page += 1
                    sub.call(cmd, shell=True)
                except:
                    self.debug("* from_pdf_ocr", "fail subprocess with", cmd)
                    return ''

                f_ = file(o_ + '.txt', 'r')
                for line in f_:
                    txt.write(line)
                f_.close()
        txt.close()
        return self.txt.path

    def from_dat(self):
        sh.copy(self.file.path, self.txt.path)
        return self.txt.path

    def upper(self):
        if not os.path.exists(self.txt.path):
            self.debug(self.txt.path, "Not Found")
            return self.txt.path

        # FIXME: maybe it's enough with self.file._path
        temp = tmp.NamedTemporaryFile(mode='w', delete=False)

        with open(self.txt.path, 'r') as f:
            for line in f:
                try:
                    line = remove_accents(line)
                except:
                    # self.debug("from upper", "fail remove_accents")
                    pass
                try:
                    line = enconding_path(line)
                except:
                    pass
                # try:
                #     line = latin2ascii(line)
                # except:
                #     self.debug("from upper", "fail latin2ascii")
                try:
                    line = line.encode('utf-8', 'replace')
                except:
                    # self.debug("from upper", "fail encode(ascii)")
                    pass
                try:
                    line = line.upper()
                except:
                    # self.debug("*", "from upper", "fail .upper()")
                    pass
                temp.write(line)
            temp.close()

            self.txt.remove()

            try:
                self.debug("moving tempfile", temp.name)
                sh.copy2(temp.name, self.txt.path)
            except:
                try:
                    sh.remove(temp.name)
                except Exception, e:
                    self.debug("*", "fail to move tempfile", temp.name)
                    self.debug(e)
                return ''
        return self.txt.path

    def convert(self, heroes=['xpdf', 'xml'], filepath='', savein='', overwrite='', uppercase=''):

        self.debug('from convert')
        self.set(
            filepath=filepath,
            savein=savein,
            overwrite=overwrite,
            uppercase=uppercase)

        try:
            self.file.create_temp()
        except Exception, e:
            self.debug("fail to call get_temp()")
            self.debug(e)
            return ''

        if self.file.extension.endswith('pdf'):
            newpath = self.from_pdf_ocr(hero=heroes[0])

        elif self.file.extension.endswith('docx'):
            newpath = self.from_docx(hero=heroes[1])

        elif self.file.extension.endswith('doc'):
            newpath = self.from_doc()

        elif self.file.extension.endswith('.dat'):
            newpath = self.from_dat()

        if self.uppercase:
            self.upper()
        try:
            self.file.remove_temp()
        except Exception, e:
            self.debug("Fail deleting temp file and directory")
            self.debug(e)

        return newpath


def main():
    global verbose
    args = docopt(usagedoc.__doc__, version='aTXT V' + __version__)
    verbose = args['--verbose']

    manager = aTXT()

    if args['<file>']:
        path = args['--from']
        if path:
            if not os.path.exists(path) or not os.path.isdir(path):
                if verbose:
                    print path, 'is not a valid path for --from option'
                print usagedoc.__doc__
                return
        else:
            path = os.getcwd()
        to = args['--to']
        if to:
            if not os.path.exists(to) or not os.path.isdir(to):
                if verbose:
                    print to, 'is not a valid path for --to option'
                print usagedoc.__doc__
                return
        else:
            to = path

        tfiles = set()
        files = []
        for f in args['<file>']:
            if not os.path.isabs(f):
                fpath = os.path.join(path, f)
            else:
                fpath = f
            root, ext = os.path.splitext(fpath)
            ext = ext.lower()
            if (not os.path.isfile(fpath) or
                    not os.path.exists(fpath) or
                    not ext in ['.pdf', '.docx', '.dat', '.doc']):
                if verbose:
                    print fpath, 'not found or \n\tignored (may has not a format supported)'
                continue
            if verbose:
                print fpath, 'indexed'
            files.append(fpath)
            tfiles.add(ext)
        tfiles = list(tfiles)
        if not files:
            print 'No files to process.'
            return

        if verbose:
            print 'path={p}\nto={t}\ntfiles={f}\n'.format(p=path, t=to, f=tfiles)
            print 'Pending', len(files)
            for f in files:
                print '\t', f

        for fpath in files:
            manager.convert(
                filepath=fpath,
                uppercase=args['-u'],
                overwrite=args['-o'],
                savein=to
            )

    elif args['--path']:
        if args['<path>']:
            path = args['<path>']
            if not os.path.exists(path) or not os.path.isdir(path):
                if verbose:
                    print path, 'is not a valid path for --path option'
                print usagedoc.__doc__
                return
            depth = args['--depth']
            try:
                depth = int(depth)
                if depth < 0:
                    raise ValueError
            except:
                if verbose:
                    print depth, 'is not a valid depth for trasversing. Put a positive integer.'
                print usagedoc.__doc__
                return
            to = args['--to']
            if not to:
                to = path
            if to == 'TXT':
                to = os.path.join(path, to)
                manager.make_dir(to)
            if not os.path.exists(to) or not os.path.isdir(to):
                if verbose:
                    print path, 'is not a valid path for --to option'
                print usagedoc.__doc__
                return
            tfiles = []
            if args['--pdf']:
                tfiles.append('.pdf')
            if args['--docx']:
                tfiles.append('.docx')
            if args['--doc'] and sys.platform in ['win32']:
                tfiles.append('.doc')
            if args['--dat']:
                tfiles.append('.dat')
            if not tfiles or args['--all']:
                tfiles = ['.pdf', '.docx', '.dat']
                if sys.platform in ['win32']:
                    tfiles.append('.doc')
            if verbose:
                print 'path={p}\ndepth={d}\nto={t}\ntfiles={f}\n'.format(p=path, d=depth, t=to, f=tfiles)

            conta = 0
            for root, dirs, files in wk.walk(path, level=depth, tfiles=tfiles):
                for f in files:
                    conta += 1
                    fpath = os.path.join(root, f.name)
                    if verbose:
                        print "File #" + str(conta)
                        print "Filepath: " + fpath

                    try:
                        if verbose:
                            print 'Converting File ... '
                        if fpath.lower().endswith('.pdf') and verbose:
                            print 'Please Wait (.pdf) usually take few minutes.'

                        manager.convert(
                            filepath=fpath,
                            uppercase=args['-u'],
                            overwrite=args['-o'],
                            savein=to
                        )
                    except Exception, e:
                        print e
                        return
    elif args['-i']:
        try:
            import GUI
        except Exception, e:
            print e
            return
        GUI.main()
    else:
        print usagedoc.__doc__
        return

if __name__ == '__main__':
    main()
