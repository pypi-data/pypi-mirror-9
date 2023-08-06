# Copyright (C) 2010-2015 by the Free Software Foundation, Inc.
#
# This file is part of mailman.client.
#
# mailman.client is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, version 3 of the License.
#
# mailman.client is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mailman.client.  If not, see <http://www.gnu.org/licenses/>.

"""Client code."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'Client',
    'MailmanConnectionError',
]


import six
import json

from base64 import b64encode
from httplib2 import Http
from mailmanclient import __version__
from operator import itemgetter
from six.moves.urllib_error import HTTPError
from six.moves.urllib_parse import urlencode, urljoin


DEFAULT_PAGE_ITEM_COUNT = 50


class MailmanConnectionError(Exception):
    """Custom Exception to catch connection errors."""


class _Connection:
    """A connection to the REST client."""

    def __init__(self, baseurl, name=None, password=None):
        """Initialize a connection to the REST API.

        :param baseurl: The base url to access the Mailman 3 REST API.
        :param name: The Basic Auth user name.  If given, the `password` must
            also be given.
        :param password: The Basic Auth password.  If given the `name` must
            also be given.
        """
        if baseurl[-1] != '/':
            baseurl += '/'
        self.baseurl = baseurl
        self.name = name
        self.password = password
        if name is not None and password is None:
            raise TypeError('`password` is required when `name` is given')
        if name is None and password is not None:
            raise TypeError('`name` is required when `password` is given')
        if name is None:
            self.basic_auth = None
        else:
            auth = '{0}:{1}'.format(name, password)
            self.basic_auth = b64encode(auth.encode('utf-8')).decode('utf-8')

    def call(self, path, data=None, method=None):
        """Make a call to the Mailman REST API.

        :param path: The url path to the resource.
        :type path: str
        :param data: Data to send, implies POST (default) or PUT.
        :type data: dict
        :param method: The HTTP method to call.  Defaults to GET when `data`
            is None or POST if `data` is given.
        :type method: str
        :return: The response content, which will be None, a dictionary, or a
            list depending on the actual JSON type returned.
        :rtype: None, list, dict
        :raises HTTPError: when a non-2xx status code is returned.
        """
        headers = {
            'User-Agent': 'GNU Mailman REST client v{0}'.format(__version__),
            }
        if data is not None:
            data = urlencode(data, doseq=True)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        if method is None:
            if data is None:
                method = 'GET'
            else:
                method = 'POST'
        method = method.upper()
        if self.basic_auth:
            headers['Authorization'] = 'Basic ' + self.basic_auth
        url = urljoin(self.baseurl, path)
        try:
            response, content = Http().request(url, method, data, headers)
            # If we did not get a 2xx status code, make this look like a
            # urllib2 exception, for backward compatibility.
            if response.status // 100 != 2:
                raise HTTPError(url, response.status, content, response, None)
            if len(content) == 0:
                return response, None
            # XXX Work around for http://bugs.python.org/issue10038
            if isinstance(content, six.binary_type):
                content = content.decode('utf-8')
            return response, json.loads(content)
        except HTTPError:
            raise
        except IOError:
            raise MailmanConnectionError('Could not connect to Mailman API')


class Client:
    """Access the Mailman REST API root."""

    def __init__(self, baseurl, name=None, password=None):
        """Initialize client access to the REST API.

        :param baseurl: The base url to access the Mailman 3 REST API.
        :param name: The Basic Auth user name.  If given, the `password` must
            also be given.
        :param password: The Basic Auth password.  If given the `name` must
            also be given.
        """
        self._connection = _Connection(baseurl, name, password)

    def __repr__(self):
        return '<Client ({0.name}:{0.password}) {0.baseurl}>'.format(
            self._connection)

    @property
    def system(self):
        return self._connection.call('system/versions')[1]

    @property
    def preferences(self):
        return _Preferences(self._connection, 'system/preferences')

    @property
    def queues(self):
        response, content = self._connection.call('queues')
        queues = {}
        for entry in content['entries']:
            queues[entry['name']] = _Queue(self._connection, entry)
        return queues

    @property
    def lists(self):
        response, content = self._connection.call('lists')
        if 'entries' not in content:
            return []
        return [_List(self._connection, entry['self_link'])
                for entry in content['entries']]

    def get_list_page(self, count=50, page=1):
        return _Page(self._connection, 'lists', _List, count, page)

    @property
    def domains(self):
        response, content = self._connection.call('domains')
        if 'entries' not in content:
            return []
        return [_Domain(self._connection, entry['self_link'])
                for entry in sorted(content['entries'],
                                    key=itemgetter('url_host'))]

    @property
    def members(self):
        response, content = self._connection.call('members')
        if 'entries' not in content:
            return []
        return [_Member(self._connection, entry['self_link'])
                for entry in content['entries']]

    def get_member(self, fqdn_listname, subscriber_address):
        return self.get_list(fqdn_listname).get_member(subscriber_address)

    def get_member_page(self, count=50, page=1):
        return _Page(self._connection, 'members', _Member, count, page)

    @property
    def users(self):
        response, content = self._connection.call('users')
        if 'entries' not in content:
            return []
        return [_User(self._connection, entry['self_link'])
                for entry in sorted(content['entries'],
                                    key=itemgetter('self_link'))]

    def get_user_page(self, count=50, page=1):
        return _Page(self._connection, 'users', _User, count, page)

    def create_domain(self, mail_host, base_url=None,
                      description=None, contact_address=None):
        # `contact_address` is deprecated but still accepted.
        data = dict(mail_host=mail_host)
        if base_url is not None:
            data['base_url'] = base_url
        if description is not None:
            data['description'] = description
        response, content = self._connection.call('domains', data)
        return _Domain(self._connection, response['location'])

    def delete_domain(self, mail_host):
        response, content = self._connection.call(
            'domains/{0}'.format(mail_host), None, 'DELETE')

    def get_domain(self, mail_host=None, web_host=None):
        """Get domain by its mail_host or its web_host."""
        if mail_host is not None:
            response, content = self._connection.call(
                'domains/{0}'.format(mail_host))
            return _Domain(self._connection, content['self_link'])
        elif web_host is not None:
            for domain in self.domains:
                # note: `base_url` property will be renamed to `web_host`
                # in Mailman3Alpha8
                if domain.base_url == web_host:
                    return domain
            else:
                return None

    def create_user(self, email, password, display_name=''):
        response, content = self._connection.call(
            'users', dict(email=email,
                          password=password,
                          display_name=display_name))
        return _User(self._connection, response['location'])

    def get_user(self, address):
        response, content = self._connection.call(
            'users/{0}'.format(address))
        return _User(self._connection, content['self_link'])

    def get_address(self, address):
        response, content = self._connection.call(
            'addresses/{0}'.format(address))
        return _Address(self._connection, content)

    def get_list(self, fqdn_listname):
        response, content = self._connection.call(
            'lists/{0}'.format(fqdn_listname))
        return _List(self._connection, content['self_link'], content)

    def delete_list(self, fqdn_listname):
        response, content = self._connection.call(
            'lists/{0}'.format(fqdn_listname), None, 'DELETE')


class _Domain:

    def __init__(self, connection, url):
        self._connection = connection
        self._url = url
        self._info = None

    def __repr__(self):
        return '<Domain "{0}">'.format(self.mail_host)

    def _get_info(self):
        if self._info is None:
            response, content = self._connection.call(self._url)
            self._info = content

    # note: `base_url` property will be renamed to `web_host`
    # in Mailman3Alpha8
    @property
    def base_url(self):
        self._get_info()
        return self._info['base_url']

    @property
    def contact_address(self):
        self._get_info()
        return self._info['contact_address']

    @property
    def description(self):
        self._get_info()
        return self._info['description']

    @property
    def mail_host(self):
        self._get_info()
        return self._info['mail_host']

    @property
    def url_host(self):
        self._get_info()
        return self._info['url_host']

    @property
    def lists(self):
        response, content = self._connection.call(
            'domains/{0}/lists'.format(self.mail_host))
        if 'entries' not in content:
            return []
        return [_List(self._connection, entry['self_link'])
                for entry in sorted(content['entries'],
                                    key=itemgetter('fqdn_listname'))]

    def create_list(self, list_name):
        fqdn_listname = '{0}@{1}'.format(list_name, self.mail_host)
        response, content = self._connection.call(
            'lists', dict(fqdn_listname=fqdn_listname))
        return _List(self._connection, response['location'])


class _List:

    def __init__(self, connection, url, data=None):
        self._connection = connection
        self._url = url
        self._info = data

    def __repr__(self):
        return '<List "{0}">'.format(self.fqdn_listname)

    def _get_info(self):
        if self._info is None:
            response, content = self._connection.call(self._url)
            self._info = content

    @property
    def owners(self):
        url = self._url + '/roster/owner'
        response, content = self._connection.call(url)
        if 'entries' not in content:
            return []
        else:
            return [item['email'] for item in content['entries']]

    @property
    def moderators(self):
        url = self._url + '/roster/moderator'
        response, content = self._connection.call(url)
        if 'entries' not in content:
            return []
        else:
            return [item['email'] for item in content['entries']]

    @property
    def fqdn_listname(self):
        self._get_info()
        return self._info['fqdn_listname']

    @property
    def mail_host(self):
        self._get_info()
        return self._info['mail_host']

    @property
    def list_id(self):
        self._get_info()
        return self._info['list_id']

    @property
    def list_name(self):
        self._get_info()
        return self._info['list_name']

    @property
    def display_name(self):
        self._get_info()
        return self._info.get('display_name')

    @property
    def members(self):
        url = 'lists/{0}/roster/member'.format(self.fqdn_listname)
        response, content = self._connection.call(url)
        if 'entries' not in content:
            return []
        return [_Member(self._connection, entry['self_link'])
                for entry in sorted(content['entries'],
                                    key=itemgetter('address'))]

    @property
    def nonmembers(self):
        url = 'members/find'
        data = {
            'role': 'nonmember',
            'list_id': self.list_id
        }
        response, content = self._connection.call(url, data)
        if 'entries' not in content:
            return []
        return [_Member(self._connection, entry['self_link'])
                for entry in sorted(content['entries'],
                                    key=itemgetter('address'))]

    def get_member_page(self, count=50, page=1):
        url = 'lists/{0}/roster/member'.format(self.fqdn_listname)
        return _Page(self._connection, url, _Member, count, page)

    @property
    def settings(self):
        return _Settings(self._connection,
                         'lists/{0}/config'.format(self.fqdn_listname))

    @property
    def held(self):
        """Return a list of dicts with held message information."""
        response, content = self._connection.call(
            'lists/{0}/held'.format(self.fqdn_listname), None, 'GET')
        if 'entries' not in content:
            return []
        else:
            entries = []
            for entry in content['entries']:
                msg = dict(hold_date=entry['hold_date'],
                           msg=entry['msg'],
                           reason=entry['reason'],
                           sender=entry['sender'],
                           request_id=entry['request_id'],
                           subject=entry['subject'])
                entries.append(msg)
        return entries

    @property
    def requests(self):
        """Return a list of dicts with subscription requests."""
        response, content = self._connection.call(
            'lists/{0}/requests'.format(self.fqdn_listname), None, 'GET')
        if 'entries' not in content:
            return []
        else:
            entries = []
            for entry in content['entries']:
                request = dict(email=entry['email'],
                               address=entry['email'],  # Deprecated.
                               delivery_mode=entry['delivery_mode'],
                               display_name=entry['display_name'],
                               language=entry['language'],
                               password=entry['password'],
                               request_id=entry['request_id'],
                               request_date=entry['when'],
                               type=entry['type'])
                entries.append(request)
        return entries

    @property
    def archivers(self):
        """
        Returns a _ListArchivers instance.
        """
        url = 'lists/{0}/archivers'.format(self.list_id)
        return _ListArchivers(self._connection, url, self)

    def add_owner(self, address):
        self.add_role('owner', address)

    def add_moderator(self, address):
        self.add_role('moderator', address)

    def add_role(self, role, address):
        data = dict(list_id=self.list_id,
                    subscriber=address,
                    role=role)
        self._connection.call('members', data)

    def remove_owner(self, address):
        self.remove_role('owner', address)

    def remove_moderator(self, address):
        self.remove_role('moderator', address)

    def remove_role(self, role, address):
        url = 'lists/%s/%s/%s' % (self.fqdn_listname, role, address)
        self._connection.call(url, method='DELETE')

    def moderate_message(self, request_id, action):
        """Moderate a held message.

        :param request_id: Id of the held message.
        :type request_id: Int.
        :param action: Action to perform on held message.
        :type action: String.
        """
        path = 'lists/{0}/held/{1}'.format(
            self.fqdn_listname, str(request_id))
        response, content = self._connection.call(
            path, dict(action=action), 'POST')
        return response

    def discard_message(self, request_id):
        """Shortcut for moderate_message."""
        return self.moderate_message(request_id, 'discard')

    def reject_message(self, request_id):
        """Shortcut for moderate_message."""
        return self.moderate_message(request_id, 'reject')

    def defer_message(self, request_id):
        """Shortcut for moderate_message."""
        return self.moderate_message(request_id, 'defer')

    def accept_message(self, request_id):
        """Shortcut for moderate_message."""
        return self.moderate_message(request_id, 'accept')

    def get_member(self, email):
        """Get a membership.

        :param address: The email address of the member for this list.
        :return: A member proxy object.
        """
        # In order to get the member object we need to
        # iterate over the existing member list
        for member in self.members:
            if member.email == email:
                return member
        else:
            raise ValueError('%s is not a member address of %s' %
                             (email, self.fqdn_listname))

    def subscribe(self, address, display_name=None):
        """Subscribe an email address to a mailing list.

        :param address: Email address to subscribe to the list.
        :type address: str
        :param display_name: The real name of the new member.
        :type display_name: str
        :return: A member proxy object.
        """
        data = dict(
            list_id=self.list_id,
            subscriber=address,
            display_name=display_name,
            )
        response, content = self._connection.call('members', data)
        return _Member(self._connection, response['location'])

    def unsubscribe(self, email):
        """Unsubscribe an email address from a mailing list.

        :param address: The address to unsubscribe.
        """
        # In order to get the member object we need to
        # iterate over the existing member list

        for member in self.members:
            if member.email == email:
                self._connection.call(member.self_link, method='DELETE')
                break
        else:
            raise ValueError('%s is not a member address of %s' %
                             (email, self.fqdn_listname))

    def delete(self):
        response, content = self._connection.call(
            'lists/{0}'.format(self.fqdn_listname), None, 'DELETE')


class _ListArchivers:
    """
    Represents the activation status for each site-wide available archiver
    for a given list. 
    """

    def __init__(self, connection, url, list_obj):
        """
        :param connection: An API connection object.
        :type connection: _Connection.
        :param url: The API url of the list's archiver endpoint.
        :param url: str.
        :param list_obj: The corresponding list object.
        :type list_obj: _List.
        """
        self._connection = connection
        self._url = url
        self._list_obj = list_obj
        self._info = None

    def __repr__(self):
        self._get_info()
        return '<Archivers on "{0}">'.format(self._list_obj.list_id)

    def _get_info(self):
        # Get data from API; only once per instance.
        if self._info is None:
            response, content = self._connection.call(self._url)
            # Remove `http_etag` from dictionary, we only want
            # the archiver info.
            content.pop('http_etag')
            self._info = content

    def __iter__(self):
        self._get_info()
        for archiver in self._info:
            yield self._info[archiver]

    def __getitem__(self, key):
        self._get_info()
        # No precautions against KeyError, should behave like a dict.
        return self._info[key]

    def __setitem__(self, key, value):
        self._get_info()
        # No precautions against KeyError, should behave like a dict.
        self._info[key] = value
        # Update archiver status via the API.
        self._connection.call(self._url, self._info, method='PUT')

    def keys(self):
        self._get_info()
        for key in self._info:
            yield key


class _Member:

    def __init__(self, connection, url):
        self._connection = connection
        self._url = url
        self._info = None
        self._preferences = None

    def __repr__(self):
        return '<Member "{0}" on "{1}">'.format(self.email, self.list_id)

    def _get_info(self):
        if self._info is None:
            response, content = self._connection.call(self._url)
            self._info = content

    @property
    def list_id(self):
        self._get_info()
        return self._info['list_id']

    @property
    def address(self):
        self._get_info()
        return self._info['email']

    @property
    def email(self):
        self._get_info()
        return self._info['email']

    @property
    def self_link(self):
        self._get_info()
        return self._info['self_link']

    @property
    def role(self):
        self._get_info()
        return self._info['role']

    @property
    def user(self):
        self._get_info()
        return _User(self._connection, self._info['user'])

    @property
    def preferences(self):
        if self._preferences is None:
            path = '{0}/preferences'.format(self.self_link)
            self._preferences = _Preferences(self._connection, path)
        return self._preferences

    def unsubscribe(self):
        """Unsubscribe the member from a mailing list.

        :param self_link: The REST resource to delete
        """
        self._connection.call(self.self_link, method='DELETE')


class _User:

    def __init__(self, connection, url):
        self._connection = connection
        self._url = url
        self._info = None
        self._addresses = None
        self._subscriptions = None
        self._subscription_list_ids = None
        self._preferences = None
        self._cleartext_password = None

    def __repr__(self):
        return '<User "{0}" ({1})>'.format(self.display_name, self.user_id)

    def _get_info(self):
        if self._info is None:
            response, content = self._connection.call(self._url)
            self._info = content

    @property
    def addresses(self):
        return _Addresses(self._connection, self.user_id)

    @property
    def display_name(self):
        self._get_info()
        return self._info.get('display_name', None)

    @display_name.setter
    def display_name(self, value):
        self._get_info()
        self._info['display_name'] = value

    @property
    def password(self):
        self._get_info()
        return self._info.get('password', None)

    @password.setter
    def password(self, value):
        self._cleartext_password = value

    @property
    def user_id(self):
        self._get_info()
        return self._info['user_id']

    @property
    def created_on(self):
        self._get_info()
        return self._info['created_on']

    @property
    def self_link(self):
        self._get_info()
        return self._info['self_link']

    @property
    def subscriptions(self):
        if self._subscriptions is None:
            subscriptions = []
            for address in self.addresses:
                response, content = self._connection.call(
                    'members/find', data={'subscriber': address})
                try:
                    for entry in content['entries']:
                        subscriptions.append(_Member(self._connection,
                                                     entry['self_link']))
                except KeyError:
                    pass
            self._subscriptions = subscriptions
        return self._subscriptions

    @property
    def subscription_list_ids(self):
        if self._subscription_list_ids is None:
            list_ids = []
            for sub in self.subscriptions:
                list_ids.append(sub.list_id)
            self._subscription_list_ids = list_ids
        return self._subscription_list_ids

    @property
    def preferences(self):
        if self._preferences is None:
            path = 'users/{0}/preferences'.format(self.user_id)
            self._preferences = _Preferences(self._connection, path)
        return self._preferences

    def add_address(self, email):
        # Adds another email adress to the user record and returns an
        # _Address object.
        url = '{0}/addresses'.format(self._url)
        self._connection.call(url, {'email': email})

    def save(self):
        data = {'display_name': self.display_name}
        if self._cleartext_password is not None:
            data['cleartext_password'] = self._cleartext_password
        self.cleartext_password = None
        response, content = self._connection.call(
            self._url, data, method='PATCH')
        self._info = None

    def delete(self):
        response, content = self._connection.call(self._url, method='DELETE')


class _Addresses:

    def __init__(self, connection, user_id):
        self._connection = connection
        self._user_id = user_id
        self._addresses = None
        self._get_addresses()

    def _get_addresses(self):
        if self._addresses is None:
            response, content = self._connection.call(
                'users/{0}/addresses'.format(self._user_id))
            if 'entries' not in content:
                self._addresses = []
            self._addresses = content['entries']

    def __getitem__(self, key):
        return _Address(self._connection, self._addresses[key])

    def __iter__(self):
        for address in self._addresses:
            yield _Address(self._connection, address)


class _Address:

    def __init__(self, connection, address):
        self._connection = connection
        self._address = address
        self._preferences = None
        self._url = address['self_link']
        self._info = None

    def __repr__(self):
        return self._address['email']

    def _get_info(self):
        if self._info is None:
            response, content = self._connection.call(self._url)
            self._info = content

    @property
    def display_name(self):
        self._get_info()
        return self._info.get('display_name')

    @property
    def registered_on(self):
        self._get_info()
        return self._info.get('registered_on')

    @property
    def verified_on(self):
        self._get_info()
        return self._info.get('verified_on')

    @property
    def preferences(self):
        if self._preferences is None:
            path = 'addresses/{0}/preferences'.format(self._address['email'])
            self._preferences = _Preferences(self._connection, path)
        return self._preferences

    def verify(self):
        self._connection.call('addresses/{0}/verify'.format(
            self._address['email']), method='POST')
        self._info = None

    def unverify(self):
        self._connection.call('addresses/{0}/unverify'.format(
            self._address['email']), method='POST')
        self._info = None


PREFERENCE_FIELDS = (
    'acknowledge_posts',
    'delivery_mode',
    'delivery_status',
    'hide_address',
    'preferred_language',
    'receive_list_copy',
    'receive_own_postings',
    )

PREF_READ_ONLY_ATTRS = (
    'http_etag',
    'self_link',
    )


class _Preferences:

    def __init__(self, connection, url):
        self._connection = connection
        self._url = url
        self._preferences = None
        self.delivery_mode = None
        self._get_preferences()

    def __repr__(self):
        return repr(self._preferences)

    def _get_preferences(self):
        if self._preferences is None:
            response, content = self._connection.call(self._url)
            self._preferences = content
            for key in PREFERENCE_FIELDS:
                self._preferences[key] = content.get(key)

    def __setitem__(self, key, value):
        self._preferences[key] = value

    def __getitem__(self, key):
        return self._preferences[key]

    def __iter__(self):
        for key in self._preferences:
            yield self._preferences[key]

    def __len__(self):
        return len(self._preferences)

    def get(self, key, default=None):
        try:
            return self._preferences[key]
        except KeyError:
            return default

    def keys(self):
        return self._preferences.keys()

    def save(self):
        data = {}
        for key in self._preferences:
            if (key not in PREF_READ_ONLY_ATTRS
                    and self._preferences[key] is not None):
                data[key] = self._preferences[key]
        response, content = self._connection.call(self._url, data, 'PATCH')


LIST_READ_ONLY_ATTRS = (
    'bounces_address',
    'created_at',
    'digest_last_sent_at',
    'fqdn_listname',
    'http_etag',
    'join_address',
    'last_post_at',
    'leave_address',
    'list_id',
    'list_name',
    'mail_host',
    'next_digest_number',
    'no_reply_address',
    'owner_address',
    'post_id',
    'posting_address',
    'request_address',
    'scheme',
    'volume',
    'web_host',
    )


class _Settings:

    def __init__(self, connection, url):
        self._connection = connection
        self._url = url
        self._info = None
        self._get_info()

    def __repr__(self):
        return repr(self._info)

    def _get_info(self):
        if self._info is None:
            response, content = self._connection.call(self._url)
            self._info = content

    def __iter__(self):
        for key in self._info:
            yield key

    def __getitem__(self, key):
        return self._info[key]

    def __setitem__(self, key, value):
        self._info[key] = value

    def __len__(self):
        return len(self._info)

    def get(self, key, default=None):
        try:
            return self._info[key]
        except KeyError:
            return default

    def keys(self):
        return self._info.keys()

    def save(self):
        data = {}
        for attribute, value in self._info.items():
            if attribute not in LIST_READ_ONLY_ATTRS:
                data[attribute] = value
        response, content = self._connection.call(self._url, data, 'PATCH')


class _Page:

    def __init__(self, connection, path, model, count=DEFAULT_PAGE_ITEM_COUNT,
                 page=1):
        self._connection = connection
        self._path = path
        self._count = count
        self._page = page
        self._model = model
        self._entries = []
        self._create_page()

    def __getitem__(self, key):
        return self._entries[key]

    def __iter__(self):
        for entry in self._entries:
            yield entry

    def __repr__(self):
        return '<Page {0} ({1})'.format(self._page, self._model)

    def __len__(self):
        return len(self._entries)

    def _create_page(self):
        self._entries = []
        # create url
        path = '{0}?count={1}&page={2}'.format(
            self._path, self._count, self._page)
        response, content = self._connection.call(path)
        if 'entries' in content:
            for entry in content['entries']:
                self._entries.append(self._model(self._connection,
                                     entry['self_link']))

    @property
    def nr(self):
        return self._page

    @property
    def next(self):
        self._page += 1
        self._create_page()
        return self

    @property
    def previous(self):
        if self._count > 0:
            self._page -= 1
            self._create_page()
            return self


class _Queue:
    def __init__(self, connection, entry):
        self._connection = connection
        self.name = entry['name']
        self.url = entry['self_link']
        self.directory = entry['directory']

    def __repr__(self):
        return '<Queue: {}>'.format(self.name)

    def inject(self, list_id, text):
        self._connection.call(self.url, dict(list_id=list_id, text=text))

    @property
    def files(self):
        response, content = self._connection.call(self.url)
        return content['files']
