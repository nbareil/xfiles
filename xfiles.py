#! /usr/bin/env python
# -*- coding: utf-8 *-*
#
# Copyright (C) Nicolas Bareil <nico@chdir.org>
#
# This program is published under a GPLv2 license


from optparse import OptionParser

import re
import fileinput
import logging
import sys
import os
import web
import cgi
import tempfile
import gnupg
import json
import string
import random

def usage(ret=1):
    parser.print_help()
    sys.exit(ret)

urls = (
    '/', 'RedirectView',
    '/upload', 'UploadView',
    '/download/([^/]+)', 'DownloadView',
)

MAX_FILES = 9
hash_re = re.compile('^[a-zA-Z0-9]+$')


def pwgen(size=16, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


class PersistantFieldStorage(cgi.FieldStorage):
    def make_file(self, binary=None):
        return tempfile.NamedTemporaryFile()
cgi.FieldStorage = PersistantFieldStorage    


class RedirectView:
    def GET(self):
        raise web.seeother('/upload')


class UploadView:
    dir = "space"
    def GET(self):
        render = web.template.render('templates')
        return render.upload()
    def POST(self):
        user_filename = web.ctx.env.get('HTTP_X_FILE_NAME')
        load = web.data()
        key = pwgen(size=32)
        internal_filename = pwgen()
        try:
            gpg = gnupg.GPG()
            meta = os.path.join(self.dir, internal_filename + '.meta')
            gpg.encrypt(user_filename, [], armor=False, symmetric=True,
                        output=meta, passphrase=key)

            safe_path = os.path.join(self.dir, internal_filename)
            gpg.encrypt(load, [], symmetric=True,
                        passphrase=key, output=safe_path,
                        armor=False)
            ret = True
        except:
            ret = False
        response = {
            'key': key,
            'filename': internal_filename,
            'success': ret,
        }
        return json.dumps(response)


class DownloadView:
    dir = "space"
    def GET(self, hash):
        render = web.template.render('templates')
        return render.download()

    def POST(self, hash):
        i = web.input(key=None)
        key = i['key']
        gpg = gnupg.GPG()
        match = hash_re.match(hash)
        if not match:
            # log.error('Invalid hash %r' % hash)
            raise web.notfound()
        safe_path = os.path.join(self.dir, hash)
        try:
            encrypted_filename = open(safe_path + '.meta').read()
        except IOError:
            raise web.notfound()
        gpgret = gpg.decrypt(encrypted_filename, passphrase=key)
        if not gpgret.ok:
            raise web.notfound()
        user_filename = gpgret.data
        web.header('Content-Disposition', 'attachment; filename=%s' % user_filename)
        fd = open(safe_path)
        gpgret = gpg.decrypt_file(fd, passphrase=key)
        if not gpgret.ok:
            raise web.notfound()
        return gpgret.data


if __name__ == '__main__':
    parser = OptionParser(usage=u'usage: %prog [options]')
    parser.add_option('-o', '--store-dir', dest='store', metavar="DIR",
                      help=u"Write files in directory", default="space")
    parser.add_option('-v', '--verbose', dest='verbose', action="store_true",
                      default=False, help=u"Verbose mode")
    parser.add_option('-d', '--debug', dest='debug', action="store_true",
                      default=False, help=u"Debug mode")

    (options,args) = parser.parse_args()

    loglvl = logging.INFO if options.verbose else logging.WARNING
    loglvl = logging.DEBUG if options.debug else loglvl
    logging.basicConfig(level=loglvl,
                        format="%(asctime)s %(name)8s %(levelname)5s: %(message)s")
    log = logging.getLogger(sys.argv[0])

    web.config.debug = options.debug

    try:
        os.makedirs(options.store)
    except OSError, e:
        if e.errno != os.errno.EEXIST:
            log.error("Cannot create directory: %s" % e)
            sys.exit(1)

    log.info('Writing files in %s' % options.store)
    tempfile.tempdir = options.store
    sys.argv = []
    app = web.application(urls, globals())
    app.run()
