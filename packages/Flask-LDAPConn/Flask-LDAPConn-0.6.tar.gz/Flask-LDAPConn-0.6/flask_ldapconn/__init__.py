# -*- coding: utf-8 -*-
from ssl import CERT_OPTIONAL, PROTOCOL_TLSv1
from flask import current_app
from flask import _app_ctx_stack as stack
from ldap3 import Server, Connection, Tls
from ldap3 import STRATEGY_SYNC, GET_ALL_INFO, SUBTREE
from ldap3 import AUTO_BIND_NO_TLS, AUTO_BIND_TLS_BEFORE_BIND
from ldap3 import LDAPBindError, LDAPInvalidFilterError, LDAPInvalidDnError
from ldap3.utils.dn import split_ava

from .entry import LDAPEntry
from .attribute import LDAPAttribute


__all__ = ('LDAPConn',)


class LDAPConn(object):

    def __init__(self, app=None):

        self.Entry = LDAPEntry
        self.Attribute = LDAPAttribute

        self.Model = self.Entry

        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        # Default config
        app.config.setdefault('LDAP_SERVER', 'localhost')
        app.config.setdefault('LDAP_PORT', 389)
        app.config.setdefault('LDAP_BINDDN', None)
        app.config.setdefault('LDAP_SECRET', None)
        app.config.setdefault('LDAP_TIMEOUT', 10)
        app.config.setdefault('LDAP_USE_SSL', False)
        app.config.setdefault('LDAP_USE_TLS', True)
        app.config.setdefault('LDAP_REQUIRE_CERT', CERT_OPTIONAL)
        app.config.setdefault('LDAP_CERT_PATH', None)

        self.tls = Tls(validate=app.config['LDAP_REQUIRE_CERT'],
                       version=PROTOCOL_TLSv1,
                       ca_certs_file=app.config['LDAP_CERT_PATH'])

        self.ldap_server = Server(
            host=app.config['LDAP_SERVER'],
            port=app.config['LDAP_PORT'],
            use_ssl=app.config['LDAP_USE_SSL'],
            get_info=GET_ALL_INFO
        )

        # Store ldap_conn object to extensions
        app.extensions['ldap_conn'] = self

        # Teardown appcontext
        app.teardown_appcontext(self.teardown)

    def connect(self, user, password):
        auto_bind_strategy = AUTO_BIND_TLS_BEFORE_BIND
        if current_app.config['LDAP_USE_TLS'] is not True:
            auto_bind_strategy = AUTO_BIND_NO_TLS

        ldap_conn = Connection(
            self.ldap_server,
            auto_bind=auto_bind_strategy,
            client_strategy=STRATEGY_SYNC,
            user=user,
            password=password,
            check_names=True
        )

        return ldap_conn

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'ldap_conn'):
            ctx.ldap_conn.unbind()

    @property
    def connection(self):
        user = current_app.config['LDAP_BINDDN']
        password = current_app.config['LDAP_SECRET']

        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'ldap_conn'):
                ctx.ldap_conn = self.connect(user, password)
            return ctx.ldap_conn

    def authenticate(self,
                     username,
                     password,
                     attribute=None,
                     base_dn=None,
                     search_filter=None,
                     search_scope=SUBTREE):
        '''Attempts to bind a user to the LDAP server.

        Args:
            username (str): DN or the username to attempt to bind with.
            password (str): The password of the username.
            attribute (str): The LDAP attribute for the username.
            base_dn (str): The LDAP basedn to search on.
            search_filter (str): LDAP searchfilter to attempt the user
                search with.

        Returns:
            bool: ``True`` if successful or ``False`` if the
                credentials are invalid.
        '''
        # If the username is no valid DN we can bind with, we nee to find
        # the user first.
        if not split_ava(username)[0]:
            user_filter = '({0}={1})'.format(attribute, username)
            if search_filter is not None:
                user_filter = '(&{0}{1})'.format(user_filter, search_filter)

            try:
                self.connection.search(base_dn, user_filter, search_scope,
                                       attributes=[attribute])
                response = self.connection.response
                username = response[0]['dn']
            except (LDAPInvalidDnError, LDAPInvalidFilterError, IndexError):
                return False

        try:
            conn = self.connect(username, password)
            conn.unbind()
            return True
        except LDAPBindError:
            return False

    def whoami(self):
        '''Deprecated

        Use LDAPConn.connection.extend.standard.who_am_i()
        '''
        return self.connection.extend.standard.who_am_i()

    def result(self):
        '''Deprecated

        Use LDAPConn.connection.result
        '''
        return self.connection.result

    def response(self):
        '''Deprecated

        Use LDAPConn.connection.response
        '''
        return self.connection.response

    def search(self, *args, **kwargs):
        '''Deprecated

        Use LDAPConn.connection.search()
        '''
        return self.connection.search(*args, **kwargs)
