# -*- coding: utf-8 -*-

import cgi
import copy
import fnmatch
import json
import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.response import Response
from pyramid.security import Everyone, Authenticated
from pyramid.settings import aslist
from pyramid.threadlocal import get_current_registry
from pyramid.view import view_config
from zope.interface import implementer, Interface

from .authentication_policy import get_user_from_session
from .interfaces import *
from .openstax_accounts import UserNotFoundException
from .utils import local_settings


DEFAULT_PROFILE = {
    'username': 'test', # to be generated
    'id': 1, # to be generated
    'first_name': 'Test',
    'last_name': 'User',
    'full_name': 'Test User',
    'title': None,
    }


def get_users_from_settings(setting):
    users = {}
    for i, user in enumerate(aslist(setting, flatten=False)):
        if user.count(',') > 1:
            username, password, profile = user.split(',', 2)
            profile = json.loads(profile)
        else:
            username, password = user.split(',', 1)
            profile = copy.deepcopy(DEFAULT_PROFILE)

        profile['id'] = i + 1
        profile['username'] = username
        users[username] = {
            'profile': profile,
            'password': password,
            }
    return users


@implementer(IOpenstaxAccountsAuthenticationPolicy)
class StubAuthenticationPolicy(object):
    def __init__(self, users):
        self.users = users

    def _groups(self, request):
        """A mapping of group ids a list of user ids"""
        # TODO Ideally, we'd use the accounts groups, but the implementation
        #      of groups in accounts is not fleshed out enough at this time.
        #      So for now we pull them from configuration settings.
        if not hasattr(self, '_parsed_groups'):
            self._parsed_groups = {}
            settings = request.registry.settings
            prefix = 'openstax_accounts.groups'
            groups = local_settings(settings, prefix=prefix)
            for group_name, values in groups.items():
                self._parsed_groups[group_name] = aslist(values)
        return self._parsed_groups

    def _membership(self, request, userid):
        """List of groups this `userid` has membership with."""
        return [group_name
                for group_name, userids in self._groups(request).items()
                if userid in userids]

    def authenticated_userid(self, request):
        settings = request.registry.settings
        login_path = settings['openstax_accounts.login_path']
        callback_path = settings['openstax_accounts.callback_path']
        if request.path == login_path:
            raise HTTPFound(location=request.route_url('stub-login-form'))
        if request.path == callback_path:
            return self.unauthenticated_userid(request)

        username = request.params.get('username')
        password = request.params.get('password')
        user = self.users.get(username)
        if user and user['password'] == password:
            self.remember(request, username, profile=user['profile'])
            return username
        return self.unauthenticated_userid(request)

    def unauthenticated_userid(self, request):
        return request.session.get('username')

    def effective_principals(self, request):
        principals = [Everyone]
        userid = self.authenticated_userid(request)
        if userid:
            principals.append(Authenticated)
            principals.append(userid)
        principals.extend(['g:{}'.format(name)
                           for name in self._membership(request, userid)])
        return principals

    def remember(self, request, principal, **kw):
        request.session.update({
            'username': principal,
            'profile': kw.get('profile'),
            })
        request.session.changed()
        return []

    def forget(self, request):
        request.session.clear()
        return []


@view_config(route_name='stub-login-form', request_method=['GET', 'POST'])
def login_form(request):
    error = ''
    if request.method == 'POST':
        if request.authenticated_userid:
            raise HTTPFound(request.registry.settings[
                'openstax_accounts.callback_path'])
        error = 'Username or password incorrect'
    return Response('''\
<html>
<body>
    <div>{error}</div>
    <form method="POST" action="">
        <div>
            <label for="username">Username:</label>
            <input name="username" id="username" />
        </div>
        <div>
            <label for="password">Password:</label>
            <input name="password" type="password" id="password" />
        </div>
        <div>
            <input type="submit" />
        </div>
    </form>
</body>
</html>
    '''.format(error=error))


class IStubMessageWriter(Interface):
    """Writes sent messages to an output interface."""

    def write(self, s):
        """Writes the content ``s`` to the output."""

@implementer(IStubMessageWriter)
class LogWriter(object):

    def write(self, s):
        logger = logging.getLogger()
        message = "Sent message:\n\n{}".format(s)
        logger.info(message)


@implementer(IStubMessageWriter)
class FileWriter(object):

    def write(self, s):
        with open('messages.txt', 'a') as file:
            file.write("{}\n\n\n".format(s))


@implementer(IStubMessageWriter)
class MemoryWriter(object):

    def __init__(self):
        self.messages = []

    def write(self, s):
        self.messages.append(s)


@implementer(IOpenstaxAccounts)
class OpenstaxAccounts(object):
    def __init__(self, users):
        self.users = users

    def search(self, query, **kwargs):
        query = query.replace('%', '*')
        order_by = kwargs.get('order_by', 'username ASC')
        results = {
                'items': [],
                'total_count': 0,
                }
        for username in self.users:
            profile = self.users[username]['profile']
            for value in profile.values():
                if fnmatch.fnmatch(username, query) \
                   or username in query:
                    results['items'].append(profile)
                    break

        # sort results
        for sort_by in order_by.split(','):
            results['items'].sort(
                lambda a, b: cmp(a.get(sort_by), b.get(sort_by)))
        results['total_count'] = len(results['items'])

        return results

    global_search = search

    def send_message(self, username, subject, text_body, html_body=None):
        users = self.global_search('username:{}'.format(username))
        userid = None
        for user in users['items']:
            if user['username'] == username:
                userid = user['id']
        if userid is None:
            raise UserNotFoundException('User "{}" not found'.format(username))

        if html_body is None:
            html_body = '<html><body>{}</body></html>'.format(
                cgi.escape(text_body).replace('\n', '\n<br/>'))

        msg_data = {
            'user_id': int(userid),
            'to[user_ids][]': [int(userid)],
            'subject': subject,
            'body[text]': text_body,
            'body[html]': html_body,
            }

        write_util = get_current_registry().getUtility(IStubMessageWriter)
        write_util.write(json.dumps(msg_data))

    def get_profile(self):
        raise NotImplementedError

    def get_profile_by_username(self, username):
        profile = None
        for uname, info in self.users.items():
            if username == uname:
                profile = info['profile']
                break
        return profile

    def update_email(self, existing_emails, email):
        raise NotImplementedError

    def update_profile(self, request, **post_data):
        raise NotImplementedError


# BBB (11-Mar-2015) Deprecated, use 'includeme' by invoking
#     ``config.include('openstax_accounts')``.
def main(config):
    includeme(config)


def includeme(config):
    config.add_request_method(get_user_from_session, 'user', reify=True)
    settings = config.registry.settings
    settings = local_settings(settings)
    users = get_users_from_settings(settings.get('stub.users'))
    writer_type = settings.get('stub.message_writer', 'file')

    # Set authentication policy
    config.registry.registerUtility(StubAuthenticationPolicy(users),
                                    IOpenstaxAccountsAuthenticationPolicy)

    # add stub login form
    config.add_route('stub-login-form', '/stub-login-form')

    # register stub openstax accounts utility
    # TODO register is named mapping somewhere rather than hardcode it.
    writer_mapping = {
        'file': FileWriter,
        'log': LogWriter,
        'memory': MemoryWriter,
        }
    writer = writer_mapping[writer_type]()
    config.registry.registerUtility(writer, IStubMessageWriter)
    openstax_accounts = OpenstaxAccounts(users)
    config.registry.registerUtility(openstax_accounts, IOpenstaxAccounts)

    config.scan(package='openstax_accounts.stub')
