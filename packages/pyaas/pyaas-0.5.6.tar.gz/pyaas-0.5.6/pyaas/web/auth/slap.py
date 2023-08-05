
import logging

import pyaas

import tornado.web

try:
    import ldap
except ImportError:
    raise pyaas.error('Missing LDAP module')


class Slap(tornado.web.RequestHandler):
    def get(self):
        next = self.get_argument('next', '/')
        self.render('login.html', next=next)

    def post(self):
        username = self.get_argument('username', '')
        username = tornado.escape.xhtml_escape(username)
        password = self.get_argument('password', '')

        ldap_dn  = pyaas.config.get('slap', 'dn')
        ldap_uri = pyaas.config.get('slap', 'uri')

        try:
            dn = ldap_dn.format(username)
            ldap_server = ldap.initialize(ldap_uri)
            ldap_server.bind_s(dn, password)
            ldap_server.unbind()

            self.set_secure_cookie('uid', username)

        except ldap.INVALID_CREDENTIALS:
            logging.warn('Invalid credentials for user: %s', username)

        except ldap.SERVER_DOWN:
            logging.warn('Could not connect to LDAP server: %s', ldap_uri)

        self.redirect(self.get_argument('next', '/'))
