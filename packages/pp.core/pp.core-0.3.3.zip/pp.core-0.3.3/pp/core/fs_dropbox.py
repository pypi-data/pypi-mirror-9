################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import os
import cPickle
from os.path import expanduser
import time
from dropbox import client 
from dropbox import rest
from dropbox import session
from dropboxfs import DropboxFS
from splinter import Browser
import fs.wrapfs

from pp.core.logger import LOG


access_type = 'dropbox'


class DropboxFSWrapper(fs.wrapfs.WrapFS):
    """ A wrapper for a DropboxFS in order to sandbox
        all Filesystem operations below a certain
        subpath since the DropboxFS core implementation
        does not support FS sandboxing.
    """

    def __init__(self, fs, prefix='wrapper'):
        super(DropboxFSWrapper, self).__init__(fs)
        self.prefix = prefix
    
    def _encode(self, path):
        return self.prefix + '/' + path

    def _decode(self, path):
        if path.startswith('/'):
            return path.replace('/' + self.prefix + '/', '')
        else:
            return path.replace(self.prefix + '/', '')

def dropboxfs_factory(app_key, app_secret, username, password):

    home = expanduser("~")
    token_filename = os.path.join(home, '.ppcore_{}'.format(username))

    if os.path.exists(token_filename):

        with open(token_filename, 'rb') as fp:
            access_token = cPickle.loads(fp.read())

    else:

        access_token = None
        sess = session.DropboxSession(app_key, app_secret, access_type)
        request_token = sess.obtain_request_token()
        urlDropbox = sess.build_authorize_url(request_token)

        browser = Browser('phantomjs')
        LOG.debug('Starting phantomjs browser {}'.format(urlDropbox))
        browser.visit(urlDropbox)

        import pytest; pytest.set_trace()
        browser.find_by_id('email-field').first.find_by_id('login_email').first.fill(username)
        LOG.debug('Email form successfully filled')

        browser.find_by_id('login_password').first.fill(password)
        LOG.debug('Password form successfully filled')

        submitButton = browser.is_element_present_by_name('login_submit_dummy')

        if submitButton == True:
            LOG.debug('Pausing for 5 seconds to avoid clicking errors')
            time.sleep(5)
            browser.find_by_name('login_submit_dummy').first.click()
            LOG.debug('"Submit" button successfully clicked')

            # Allow connection with Dropbox
            allowButton = browser.is_element_present_by_css('.freshbutton-blue')

            if allowButton == True:
                browser.find_by_css('.freshbutton-blue').click()
                browser.quit()
                access_token = sess.obtain_access_token(request_token)
                with open(token_filename, 'wb') as fp:
                    fp.write(cPickle.dumps(access_token))

            else:
                LOG.error('The "Allow" button is not present, quitting.')
                browser.quit()

        else:
            LOG.error('The "Submit" button was not present, quitting.')
            browser.quit()

    if access_token:
        fs = DropboxFS(app_key,
                       app_secret,
                       access_type, 
                       access_token.key, 
                       access_token.secret)
        return DropboxFSWrapper(fs)
    else:
        raise RuntimeError('Unable to get hold of Dropbox access token')


from fs.opener import opener
from fs.opener import Opener
from fs.opener import OpenerRegistry
from fs.opener import _parse_credentials

# get_dropbox_app_credentials() is a hook that must be configured in order to
# return a valid tuple (app_key, app_secret) for accessing Dropbox. This method
# must be provided by the higher level application
#
# Example:
#
# def get_dropbox_app_credentials():
#     app_key = os.environ['APP_KEY']
#     app_secret = os.environ['APP_SECRET']
#     return (app_key, app_secret)

get_dropbox_app_credentials = None

class DropboxOpener(Opener):
    names = ['dropbox']
    desc = """Opens a Dropbox directory """

    @classmethod
    def get_fs(cls, registry, fs_name, fs_name_params, fs_path, writeable, create_dir):
        
        url = fs_path
        if not '://' in url:
            url = 'dropbox://' + url
        scheme, url = url.split('://', 1)
        username, password = url.split('/', 1)[0].split(':')

        if get_dropbox_app_credentials:
            app_key, app_secret = get_dropbox_app_credentials()
        else:
            raise RuntimeError(u'No callback for get_dropbox_app_credentials() configured')

        if username and password:
            return dropboxfs_factory(app_key, app_secret, username, password), ''
        raise RuntimeError('No Dropbox credentials found in {}'.format(url))
        
opener.add(DropboxOpener)
