===================
Mailman REST client
===================

This is the official Python bindings for the GNU Mailman REST API.  In order
to talk to Mailman, the engine's REST server must be running.  You begin by
instantiating a client object to access the root of the REST hierarchy,
providing it the base URL, user name and password (for Basic Auth).

    >>> from mailmanclient import Client
    >>> client = Client('http://localhost:9001/3.0', 'restadmin', 'restpass')

.. note::
    Please note that port '9001' is used above, since mailman's test server
    runs on port *9001*. In production Mailman's REST API usually listens on
    port *8001*.

We can retrieve basic information about the server.

    >>> dump(client.system)
    http_etag: "..."
    mailman_version: GNU Mailman 3.0... (...)
    python_version: ...
    self_link: http://localhost:9001/3.0/system/versions

To start with, there are no known mailing lists.

    >>> client.lists
    []


Domains
=======

Before new mailing lists can be added, the domain that the list will live in
must be added.  By default, there are no known domains.

    >>> client.domains
    []

It's easy to create a new domain; when you do, a proxy object for that domain
is returned.

    >>> example_dot_com = client.create_domain('example.com')
    >>> example_dot_com
    <Domain "example.com">
    >>> print(example_dot_com.base_url)
    http://example.com
    >>> print(example_dot_com.description)
    None
    >>> print(example_dot_com.mail_host)
    example.com
    >>> print(example_dot_com.url_host)
    example.com

You can also get an existing domain independently using its mail host.

    >>> example = client.get_domain('example.com')
    >>> example
    <Domain "example.com">
    >>> print(example_dot_com.base_url)
    http://example.com

Additionally you can get an existing domain using its web host.

    >>> example = client.get_domain(web_host='http://example.com')
    >>> example
    <Domain "example.com">
    >>> print(example_dot_com.base_url)
    http://example.com

After creating a few more domains, we can print the list of all domains.

    >>> client.create_domain('example.net')
    <Domain "example.net">
    >>> client.create_domain('example.org')
    <Domain "example.org">
    >>> for mail_host in client.domains:
    ...     print(mail_host)
    <Domain "example.com">
    <Domain "example.net">
    <Domain "example.org">

Also, domain can be deleted.

    >>> client.delete_domain('example.org')
    >>> for mail_host in client.domains:
    ...     print(mail_host)
    <Domain "example.com">
    <Domain "example.net">


Mailing lists
=============

Once you have a domain, you can create mailing lists in that domain.

    >>> test_one = example.create_list('test-one')
    >>> test_one
    <List "test-one@example.com">
    >>> print(test_one.fqdn_listname)
    test-one@example.com
    >>> print(test_one.mail_host)
    example.com
    >>> print(test_one.list_name)
    test-one
    >>> print(test_one.display_name)
    Test-one

You can also retrieve the mailing list after the fact.

    >>> my_list = client.get_list('test-one@example.com')
    >>> my_list
    <List "test-one@example.com">

And you can print all the known mailing lists.
::

    >>> example.create_list('test-two')
    <List "test-two@example.com">
    >>> domain = client.get_domain('example.net')
    >>> domain.create_list('test-three')
    <List "test-three@example.net">
    >>> example.create_list('test-three')
    <List "test-three@example.com">

    >>> for mlist in client.lists:
    ...     print(mlist)
    <List "test-one@example.com">
    <List "test-two@example.com">
    <List "test-three@example.net">
    <List "test-three@example.com">

List results can be retrieved as pages:

    >>> page = client.get_list_page(count=2, page=1)
    >>> page.nr
    1
    >>> len(page)
    2
    >>> for m_list in page:
    ...     print(m_list)
    <List "test-one@example.com">
    <List "test-two@example.com">
    >>> page = page.next
    >>> page.nr
    2
    >>> for m_list in page:
    ...     print(m_list)
    <List "test-three@example.net">
    <List "test-three@example.com">

If you only want to know all lists for a specific domain, use the domain
object.

    >>> for mlist in example.lists:
    ...     print(mlist)
    <List "test-one@example.com">
    <List "test-three@example.com">
    <List "test-two@example.com">

You can use a list instance to delete the list.

    >>> test_three = client.get_list('test-three@example.net')
    >>> test_three.delete()

You can also delete a list using the client instance's delete_list method.

    >>> client.delete_list('test-three@example.com')

    >>> for mlist in client.lists:
    ...     print(mlist)
    <List "test-one@example.com">
    <List "test-two@example.com">


Membership
==========

Email addresses can subscribe to existing mailing lists, becoming members of
that list.  The address is a unique id for a specific user in the system, and
a member is a user that is subscribed to a mailing list.  Email addresses need
not be pre-registered, though the auto-registered user will be unique for each
email address.

The system starts out with no members.

    >>> client.members
    []

New members can be easily added; users are automatically registered.
::

    >>> test_two = client.get_list('test-two@example.com')

    >>> test_one.subscribe('anna@example.com', 'Anna')
    <Member "anna@example.com" on "test-one.example.com">
    >>> test_one.subscribe('bill@example.com', 'Bill')
    <Member "bill@example.com" on "test-one.example.com">
    >>> test_two.subscribe('anna@example.com')
    <Member "anna@example.com" on "test-two.example.com">
    >>> test_two.subscribe('cris@example.com', 'Cris')
    <Member "cris@example.com" on "test-two.example.com">

We can retrieve all known memberships.  These are sorted first by mailing list
name, then by email address.

    >>> for member in client.members:
    ...     print(member)
    <Member "anna@example.com" on "test-one.example.com">
    <Member "bill@example.com" on "test-one.example.com">
    <Member "anna@example.com" on "test-two.example.com">
    <Member "cris@example.com" on "test-two.example.com">

We can also view the memberships for a single mailing list.

    >>> for member in test_one.members:
    ...     print(member)
    <Member "anna@example.com" on "test-one.example.com">
    <Member "bill@example.com" on "test-one.example.com">

Membership lists can be paginated, to recieve only a part of the result.

    >>> page = client.get_member_page(count=2, page=1)
    >>> page.nr
    1
    >>> for member in page:
    ...     print(member)
    <Member "anna@example.com" on "test-one.example.com">
    <Member "bill@example.com" on "test-one.example.com">

    >>> page = page.next
    >>> page.nr
    2
    >>> for member in page:
    ...     print(member)
    <Member "anna@example.com" on "test-two.example.com">
    <Member "cris@example.com" on "test-two.example.com">

    >>> page = test_one.get_member_page(count=1, page=1)
    >>> page.nr
    1
    >>> for member in page:
    ...     print(member)
    <Member "anna@example.com" on "test-one.example.com">
    >>> page = page.next
    >>> page.nr
    2
    >>> for member in page:
    ...     print(member)
    <Member "bill@example.com" on "test-one.example.com">

We can get a single membership too.

    >>> cris_test_two = test_two.get_member('cris@example.com')
    >>> cris_test_two
    <Member "cris@example.com" on "test-two.example.com">
    >>> print(cris_test_two.role)
    member

A membership can also be retrieved without instantiating the list object first:

    >>> client.get_member('test-two@example.com', 'cris@example.com')
    <Member "cris@example.com" on "test-two.example.com">

A membership has preferences.

    >>> prefs = cris_test_two.preferences
    >>> print(prefs['delivery_mode'])
    regular
    >>> print(prefs['acknowledge_posts'])
    None
    >>> print(prefs['delivery_status'])
    None
    >>> print(prefs['hide_address'])
    None
    >>> print(prefs['preferred_language'])
    en
    >>> print(prefs['receive_list_copy'])
    None
    >>> print(prefs['receive_own_postings'])
    None

The membership object's ``user`` attribute will return a User object:

    >>> cris_test_two.user
    <User "Cris" (...)>

If you use an address which is not a member of test_two `ValueError` is raised:

    >>> test_two.unsubscribe('nomember@example.com')
    Traceback (most recent call last):
    ...
    ValueError: nomember@example.com is not a member address of
    test-two@example.com

After a while, Anna decides to unsubscribe from the Test One mailing list,
though she keeps her Test Two membership active.

    >>> import time
    >>> time.sleep(2)
    >>> test_one.unsubscribe('anna@example.com')
    >>> for member in client.members:
    ...     print(member)
    <Member "bill@example.com" on "test-one.example.com">
    <Member "anna@example.com" on "test-two.example.com">
    <Member "cris@example.com" on "test-two.example.com">

A little later, Cris decides to unsubscribe from the Test Two mailing list.

    >>> cris_test_two.unsubscribe()
    >>> for member in client.members:
    ...     print(member)
    <Member "bill@example.com" on "test-one.example.com">
    <Member "anna@example.com" on "test-two.example.com">

If you try to unsubscribe an address which is not a member address
`ValueError` is raised:

    >>> test_one.unsubscribe('nomember@example.com')
    Traceback (most recent call last):
    ...
    ValueError: nomember@example.com is not a member address of
    test-one@example.com


Non-Members
===========

When someone attempts to post to a list but is not a member, then they are
listed as a "non-member" of that list so that a moderator can choose how to
handle their messages going forward.  In some cases, one might wish to
accept or reject their future messages automatically.  Just like with regular
members, they are given a unique id.

The list starts out with no nonmembers.

    >>> test_one.nonmembers
    []

When someone tries to send a message to the list and they are not a
subscriber, they get added to the nonmember list.


Users
=====

Users are people with one or more list memberships. To get a list of all users,
access the clients user property.

    >>> for user in client.users:
    ...     print(user)
    <User "..." (...)>
    <User "..." (...)>
    <User "..." (...)>

The list of users can also be paginated:

    >>> page = client.get_user_page(count=2, page=1)
    >>> page.nr
    1

    >>> for user in page:
    ...     print(user)
    <User "Anna" (...)>
    <User "Bill" (...)>

You can get the next or previous pages without calling ``get_userpage`` again.

    >>> page = page.next
    >>> page.nr
    2

    >>> for user in page:
    ...     print(user)
    <User "Cris" (...)>

    >>> page = page.previous
    >>> page.nr
    1

    >>> for user in page:
    ...     print(user)
    <User "Anna" (...)>
    <User "Bill" (...)>

A single user can be retrieved using their email address.

    >>> cris = client.get_user('cris@example.com')
    >>> print(cris.display_name)
    Cris

Every user has a list of one or more addresses.

    >>> for address in cris.addresses:
    ...     print(address)
    ...     print(address.display_name)
    ...     print(address.registered_on)
    cris@example.com
    Cris
    ...

Multiple addresses can be assigned to a user record:

    >>> cris.add_address('cris.person@example.org')
    >>> print(client.get_address('cris.person@example.org'))
    cris.person@example.org

    >>> for address in cris.addresses:
    ...     print(address)
    cris.person@example.org
    cris@example.com


Addresses
=========

Addresses can be accessed directly:

    >>> address = client.get_address('cris@example.com')
    >>> print(address)
    cris@example.com
    >>> print(address.display_name)
    Cris

The address has not been verified:

    >>> print(address.verified_on is None)
    True

But that can be done via the address object:

    >>> address.verify()
    >>> address.verified_on is None
    False

It can also be unverified:

    >>> address.unverify()
    >>> address.verified_on is None
    True


Users can be added using ``create_user``. The display_name is optional:
    >>> client.create_user(email='ler@primus.org',
    ...                    password='somepass',
    ...                    display_name='Ler')
    <User "Ler" (...)>
    >>> ler = client.get_user('ler@primus.org')
    >>> print(ler.password)
    $...
    >>> print(ler.display_name)
    Ler

User attributes can be changed through assignment, but you need to call the
object's ``save`` method to store the changes in the mailman core database.

    >>> ler.display_name = 'Sir Ler'
    >>> ler.save()
    >>> ler = client.get_user('ler@primus.org')
    >>> print(ler.display_name)
    Sir Ler

Passwords can be changed as well:

    >>> old_pwd = ler.password
    >>> ler.password = 'easy'
    >>> old_pwd == ler.password
    True
    >>> ler.save()
    >>> old_pwd == ler.password
    False


User Subscriptions
------------------

A User's subscriptions can be access through their ``subscriptions`` property.

    >>> bill = client.get_user('bill@example.com')
    >>> for subscription in bill.subscriptions:
    ...     print(subscription)
    <Member "bill@example.com" on "test-one.example.com">

If all you need are the list ids of all mailing lists a user is subscribed to,
you can use the ``subscription_list_ids`` property.

    >>> for list_id in bill.subscription_list_ids:
    ...     print(list_id)
    test-one.example.com


List Settings
=============

We can get all list settings via a lists settings attribute. A proxy object
for the settings is returned which behaves much like a dictionary.

    >>> settings = test_one.settings
    >>> len(settings)
    50

    >>> for attr in sorted(settings):
    ...     print(attr + ': ' + str(settings[attr]))
    acceptable_aliases: []
    ...
    welcome_message_uri: mailman:///welcome.txt

    >>> print(settings['display_name'])
    Test-one

We can access all valid list settings as attributes.

    >>> print(settings['fqdn_listname'])
    test-one@example.com
    >>> print(settings['description'])

    >>> settings['description'] = 'A very meaningful description.'
    >>> settings['display_name'] = 'Test Numero Uno'

    >>> settings.save()

    >>> settings_new = test_one.settings
    >>> print(settings_new['description'])
    A very meaningful description.
    >>> print(settings_new['display_name'])
    Test Numero Uno

The settings object also supports the `get` method of usual Python
dictionaries:

    >>> print(settings_new.get('OhNoIForgotTheKey',
    ...                        'HowGoodIPlacedOneUnderTheDoormat'))
    HowGoodIPlacedOneUnderTheDoormat


Preferences
===========

Preferences can be accessed and set for users, members and addresses.

By default, preferences are not set and fall back to the global system
preferences. They're read-only and can be accessed through the client object.

    >>> global_prefs = client.preferences
    >>> print(global_prefs['acknowledge_posts'])
    False
    >>> print(global_prefs['delivery_mode'])
    regular
    >>> print(global_prefs['delivery_status'])
    enabled
    >>> print(global_prefs['hide_address'])
    True
    >>> print(global_prefs['preferred_language'])
    en
    >>> print(global_prefs['receive_list_copy'])
    True
    >>> print(global_prefs['receive_own_postings'])
    True

Preferences can be set, but you have to call ``save`` to make your changes
permanent.

    >>> prefs = test_two.get_member('anna@example.com').preferences
    >>> prefs['delivery_status'] = 'by_user'
    >>> prefs.save()
    >>> prefs = test_two.get_member('anna@example.com').preferences
    >>> print(prefs['delivery_status'])
    by_user


Owners and Moderators
=====================

Owners and moderators are properties of the list object.

    >>> test_one.owners
    []
    >>> test_one.moderators
    []

Owners can be added via the ``add_owner`` method:

    >>> test_one.add_owner('foo@example.com')
    >>> for owner in test_one.owners:
    ...     print(owner)
    foo@example.com

The owner of the list not automatically added as a member:

    >>> test_one.members
    [<Member "bill@example.com" on "test-one.example.com">]

Moderators can be added similarly:

    >>> test_one.add_moderator('bar@example.com')
    >>> for moderator in test_one.moderators:
    ...     print(moderator)
    bar@example.com

Moderators are also not automatically added as members:

    >>> test_one.members
    [<Member "bill@example.com" on "test-one.example.com">]

Members and owners/moderators are separate entries in in the general members
list:

    >>> test_one.subscribe('bar@example.com')
    <Member "bar@example.com" on "test-one.example.com">

    >>> for member in client.members:
    ...     print('%s: %s' %(member, member.role))
    <Member "foo@example.com" on "test-one.example.com">: owner
    <Member "bar@example.com" on "test-one.example.com">: moderator
    <Member "bar@example.com" on "test-one.example.com">: member
    <Member "bill@example.com" on "test-one.example.com">: member
    <Member "anna@example.com" on "test-two.example.com">: member

Both owners and moderators can be removed:

    >>> test_one.remove_owner('foo@example.com')
    >>> test_one.owners
    []

    test_one.remove_moderator('bar@example.com')
    test_one.moderators
    []


Moderation
==========

Message Moderation
------------------

By injecting a message by a non-member into the incoming queue, we can
simulate a message being held for moderator approval.

    >>> msg = """From: nomember@example.com
    ... To: test-one@example.com
    ... Subject: Something
    ... Message-ID: <moderated_01>
    ...
    ... Some text.
    ...
    ... """
    >>> inq = client.queues['in']
    >>> inq.inject('test-one.example.com', msg)

Now wait until the message has been processed.

    >>> while True:
    ...     if len(inq.files) == 0:
    ...         break
    ...     time.sleep(0.1)

It might take a few moments for the message to show up in the moderation
queue.

    >>> while True:
    ...     held = test_one.held
    ...     if len(held) > 0:
    ...         break
    ...     time.sleep(0.1)

Messages held for moderation can be listed on a per list basis.

    >>> print(held[0]['subject'])
    Something
    >>> print(held[0]['reason'])
    <BLANKLINE>
    >>> print(held[0]['request_id'])
    1

    >>> print(test_one.defer_message(held[0]['request_id'])['status'])
    204

    >>> len(test_one.held)
    1

    >>> print(test_one.discard_message(held[0]['request_id'])['status'])
    204

    >>> len(test_one.held)
    0


Archivers
=========


Each list object has an ``archivers`` attribute.

    >>> archivers = test_one.archivers
    >>> print(archivers)
    <Archivers on "test-one.example.com">

The activation status of each available archiver can be accessed like a 
key in a dictionary.

    >>> archivers = test_one.archivers
    >>> for archiver in sorted(archivers.keys()):
    ...     print('{0}: {1}'.format(archiver, archivers[archiver]))
    mail-archive: True
    mhonarc: True
    prototype: False

    >>> archivers['mail-archive']
    True
    >>> archivers['mhonarc']
    True

They can also be set like items in dictionary.

    >>> archivers['mail-archive'] = False
    >>> archivers['mhonarc'] = False

So if we get a new ``archivers`` object from the API (by accessing the 
list's archiver attribute again), we can see that the archiver stati 
have now been set.

    >>> archivers = test_one.archivers
    >>> archivers['mail-archive']
    False
    >>> archivers['mhonarc']
    False
