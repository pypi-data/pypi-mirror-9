# coding: utf-8

from __future__ import print_function

import sys
import os
import subprocess
import hashlib
import tempfile
import shutil
import glob

from ruamel.std.argparse import ProgramBase, option, sub_parser, version, \
    CountAction, SmartFormatter
from ruamel.appconfig import AppConfig
from . import __version__


class PdfData(object):
    def __init__(self, path=None, size=None):
        self._path = path
        self._size = size
        self._hash = None
        self._typ = None
        self._tmp_dir = None
        self._text_hex = None

    def __str__(self):
        return "{0._typ} {0._hash} {0._size} {0._path}".format(self)

    def determine_hash(self):
        try:
            res = subprocess.check_output(['pdfinfo', self._path])
        except:
            print('pdfinfo cannot process', self._path)
        self._info = self.parseinfo(res)
        if self.metadata_hash():
            return True
        if self.scan_hash():
            del self.tmp_dir
            return True
        if self.text_hash():
            del self.tmp_dir
            return True
        del self.tmp_dir
        print ('no hash found for', self._path)
        return False

    def metadata_hash(self):
        m = hashlib.sha256()
        for key in ['title', 'pages', 'author']:
            if self._info[key] is None:
                return False
            m.update('{0}: {1}'.format(key, self._info[key]))
        self._hash = m.hexdigest()
        self._typ = 'M'
        return True

    def scan_hash(self):
        # first check number of images against number of pages
        res = subprocess.check_output(['pdfimages', '-list', self._path])
        count = -1
        page = None
        for line in res.splitlines():
            if count < 0:
                if line.startswith('-------'):
                    count = 0
                continue
            try:
                page, img_num = map(int, line.split(None, 2)[:2])
            except ValueError:
                return False
        # print(page, img_num, self._info['pages'])
        # images are numbered starting 0, you can have multiple pictures
        # on a page, e.g. when compositing images in image slideshow.
        # pages are numbered starting 1
        if page is None:
            return False
        if page > img_num + 1 or page != int(self._info['pages']):
            return False
        m = hashlib.sha256()
        # make a temporary directory
        # redo the text conversion in case there is text and there are images
        text_file_name = os.path.join(self.tmp_dir, 'converted.txt')
        if not os.path.exists(text_file_name):
            res = subprocess.check_output(['pdftotext', self._path,
                                           text_file_name])
        with open(text_file_name) as fp:
            x = self.filter_for_marking(fp.read())
            if x:   # only if any text left
                m.update(x)
                self._text_hex = m.hexdigest()
            else:
                self._text_hex = False
        img_dir = os.path.join(self.tmp_dir, 'img')
        os.mkdir(img_dir)
        res = subprocess.check_output(["pdfimages", "-j", self._path,
                                       img_dir+'/img'])
        # walk over the images and process
        for file_name in sorted(glob.glob(img_dir + '/*')):
            self.process_img_and_update(file_name, m)
        # could include info as well in hash
        # for key in ['title', 'pages', 'author']:
        #     if self._info[key]:
        #         m.update('{0}: {1}'.format(key, self._info[key]))
        self._hash = m.hexdigest()
        self._typ = 'S'
        return True

    def text_hash(self):
        m = hashlib.sha256()
        text_file_name = os.path.join(self.tmp_dir, 'converted.txt')
        if self._text_hex is False:  # in case the converted text was empty
            return False
        if self._text_hex:  # already converted and calculated
            return text_hex
        # not converted yet
        text_file_name = os.path.join(self.tmp_dir, 'converted.txt')
        if not os.path.exists(text_file_name):
            res = subprocess.check_output(['pdftotext', self._path,
                                           text_file_name])
        with open(text_file_name) as fp:
            x = self.filter_for_marking(fp.read())
            if not x:   # only if any text left
                return False
            m.update(x)
        self._hash = m.hexdigest()
        self._typ = 'T'
        return True

    def process_img_and_update(self, file_name, m):
        """this function should update m (a hash) based on
        filtered image data:
        - strip header and footer that might contain markings
        - only keep full black pixels in case the background contains
          some marking in big gray text diagonally
        """
        # print(file_name)
        with open(file_name, 'rb') as fp:
            m.update(fp.read())

    def filter_for_marking(self, txt):
        """filter out any markings from the text"""
        return txt.strip()

    @property
    def tmp_dir(self):
        if self._tmp_dir is None:
            self._tmp_dir = tempfile.mkdtemp(suffix='pdfdbl')
        return self._tmp_dir

    @tmp_dir.deleter
    def tmp_dir(self):
        if self._tmp_dir and os.path.exists(self._tmp_dir):
            shutil.rmtree(self._tmp_dir)
        self._tmp_dir = None

    def parseinfo(self, res):
        d = dict(title=None, author=None, pages=None)
        for line in res.splitlines():
            if line.startswith('Pages:'):
                d['pages'] = line.split()[1].strip()
            if line.startswith('Title:'):
                t = line.split()[1]
                if self.significant(t):
                    d['title'] = t.strip()
            if line.startswith('Author:'):
                try:
                    a = line.split()[1]
                except IndexError:
                    pass
                else:
                    if self.significant(a):
                        d['author'] = a.strip()
        # print('d', d)
        return d

    @staticmethod
    def significant(s):
        s = s.lower()
        # get some common words out
        for w in ['acrobat', 'pdf', 'distiller']:
            s = s.replace(w, '')
        for c in s:
            if c.isalpha():
                return True  # some char from alphabet (non digit, non token)
        return False

    def scan_line(self, s):
        """create from a line"""
        self._typ, self._hash, size, self._path = s.split(None, 3)
        self._size = int(size)


class PdfDb(object):
    def __init__(self, path):
        self._path = path
        self.h2d = {}
        self.p2d = {}
        if not os.path.exists(path):
            return
        for line in open(path):
            pdfdata = PdfData()
            pdfdata.scan_line(line.rstrip())
            self.update(pdfdata)

    def update(self, pdfdata):
        if pdfdata._hash in self.h2d:
            print('hash found: {}'.format(pdfdata))
            return False
        self.h2d[pdfdata._hash] = pdfdata
        self.p2d[pdfdata._path] = pdfdata
        return True

    def save(self):
        with open(self._path, 'wb') as fp:
            for k in self.h2d.itervalues():
                fp.write('{0}\n'.format(k))

    def __str__(self):
        """only use for testing, space inefficient"""
        return '\n'.join([str(x) for x in self.h2d.values()]) + '\n'


class PdfDouble(object):
    def __init__(self, args, config):
        self._args = args
        self._config = config
        self._db = None

    def scan(self):
        changed = False
        for file_name in self.search_pdfs():
            if self.process(file_name):
                changed = True
        # print(self.db)
        if changed:
            self.db.save()

    def process(self, file_name):
        db = self.db
        pdfdata = PdfData(file_name, os.path.getsize(file_name))
        if pdfdata.determine_hash():
            # print('\npdfdata:', pdfdata)
            db.update(pdfdata)
            return True
        return False

    def search_pdfs(self):
        for p in self._args.path:
            # use absolute paths
            p = os.path.abspath(p)
            for root, directory_names, file_names in os.walk(p):
                # only consider files with extension .pdf
                # could scan the header of the file instead
                for d in ['.tox', '.hg']:
                    if d in directory_names:
                        directory_names.remove(d)
                for file_name in file_names:
                    if os.path.splitext(file_name)[1].lower() != '.pdf':
                        continue
                    yield os.path.join(root, file_name)

    @property
    def db(self):
        if self._db is None:
            self._db = PdfDb(self._config.file_in_config_dir('pdf.lst'))
        return self._db


def to_stdout(*args):
    sys.stdout.write(' '.join(args))


class PdfDoubleCmd(ProgramBase):
    def __init__(self):
        super(PdfDoubleCmd, self).__init__(
            formatter_class=SmartFormatter,
            # aliases=True,
        )

    # you can put these on __init__, but subclassing PdfDoubleCmd
    # will cause that to break
    @option('--verbose', '-v',
            help='increase verbosity level', action=CountAction,
            const=1, nargs=0, default=0, global_option=True)
    @version('version: ' + __version__)
    def _pb_init(self):
        # special name for which attribs are included in help
        pass

    def run(self):
        self.pdfdouble = PdfDouble(self._args, self._config)
        if self._args.func:
            return self._args.func()

    def parse_args(self):
        self._config = AppConfig(
            'pdfdbl',
            filename=AppConfig.check,
            parser=self._parser,  # sets --config option
            warning=to_stdout,
            add_save=False,  # add a --save-defaults (to config) option
        )
        # self._config._file_name can be handed to objects that need
        # to get other information from the configuration directory
        self._config.set_defaults()
        self._parse_args(
            default_sub_parser="scan",
        )

    @sub_parser(help='some command specific help for tmux')
    @option('path', nargs='+')
    def scan(self):
        self.pdfdouble.scan()


def main():
    n = PdfDoubleCmd()
    n.parse_args()
    sys.exit(n.run())
