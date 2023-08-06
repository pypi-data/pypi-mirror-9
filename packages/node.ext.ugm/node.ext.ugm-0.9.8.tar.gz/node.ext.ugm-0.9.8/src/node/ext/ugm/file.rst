Default UGM implementation
==========================

Create a test environment::

    >>> import os
    >>> import tempfile
    >>> tempdir = tempfile.mkdtemp()

File storage behavior::

    >>> from plumber import plumbing
    >>> from node.behaviors import (
    ...     NodeChildValidate,
    ...     Nodespaces,
    ...     Adopt,
    ...     Attributes,
    ...     DefaultInit,
    ...     Nodify,
    ... )
    >>> from node.ext.ugm.file import FileStorage

    >>> @plumbing(
    ...     NodeChildValidate,
    ...     Nodespaces,
    ...     Adopt,
    ...     Attributes,
    ...     DefaultInit,
    ...     Nodify,
    ...     FileStorage)
    ... class FileStorageNode(object):
    ...     def __init__(self, file_path):
    ...         self.__name__ = None
    ...         self.__parent__ = None
    ...         self.file_path = file_path
    ...         self._storage_data = None

    >>> file_path = os.path.join(tempdir, 'filestorage')
    >>> file_path
    '/.../filestorage'

    >>> fsn = FileStorageNode(file_path)
    >>> fsn
    <FileStorageNode object 'None' at ...>

    >>> list(fsn.__iter__())
    []

    >>> fsn['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: 'inexistent'

    >>> del fsn['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: 'inexistent'

    >>> fsn['foo'] = 'foo'
    >>> fsn.keys()
    ['foo']

    >>> fsn['foo']
    'foo'

    >>> fsn['bar'] = 'bar'

    >>> fsn['none'] = None

File not written yet::

    >>> open(file_path)
    Traceback (most recent call last):
      ...
    IOError: [Errno 2] No such file or directory: '/.../filestorage'

    >>> fsn()
    >>> with open(file_path) as file:
    ...     for line in file:
    ...         print line
    foo:foo
    <BLANKLINE>
    bar:bar
    <BLANKLINE>
    none:
    <BLANKLINE>

Recreate:: 

    >>> fsn = FileStorageNode(file_path)
    >>> fsn.keys()
    [u'foo', u'bar', u'none']

    >>> fsn.values()
    [u'foo', u'bar', u'']

Test unicode::

    >>> fsn[u'\xe4\xf6\xfc'] = u'\xe4\xf6\xfc'
    >>> fsn()

    >>> fsn = FileStorageNode(file_path)
    >>> fsn.items()
    [(u'foo', u'foo'), 
    (u'bar', u'bar'), 
    (u'none', u''), 
    (u'\xe4\xf6\xfc', u'\xe4\xf6\xfc')]

Create principal data directory::

    >>> datadir = os.path.join(tempdir, 'principal_data')
    >>> os.mkdir(datadir)

Ugm root object::

    >>> from node.ext.ugm.file import Ugm
    >>> users_file = os.path.join(tempdir, 'users')
    >>> groups_file = os.path.join(tempdir, 'groups')
    >>> roles_file = os.path.join(tempdir, 'roles')
    >>> ugm = Ugm(name='ugm',
    ...           users_file=users_file,
    ...           groups_file=groups_file,
    ...           roles_file=roles_file,
    ...           data_directory=datadir)

    >>> ugm
    <Ugm object 'ugm' at ...>

    >>> ugm.users
    <Users object 'users' at ...>

    >>> ugm.groups
    <Groups object 'groups' at ...>

    >>> ugm.attrs
    <FileAttributes object '__attrs__' at ...>

    >>> ugm.roles_storage
    <FileAttributes object '__attrs__' at ...>

    >>> ugm.attrs is ugm.roles_storage
    True

    >>> del ugm['users']
    Traceback (most recent call last):
      ...
    NotImplementedError: Operation forbidden on this node.

    >>> ugm['inexistent'] = ugm.users
    Traceback (most recent call last):
      ...
    KeyError: 'inexistent'

Nothing created yet::

    >>> sorted(os.listdir(tempdir))
    ['filestorage', 'principal_data']

Calling UGM persists::

    >>> ugm()
    >>> sorted(os.listdir(tempdir))
    ['filestorage', 'groups', 'principal_data', 'roles', 'users']

Add new User::

    >>> user = ugm.users.create('max',
    ...                         fullname='Max Mustermann',
    ...                         email='foo@bar.com')
    >>> user
    <User object 'max' at ...>

    >>> ugm.printtree()
    <class 'node.ext.ugm.file.Ugm'>: ugm
      <class 'node.ext.ugm.file.Users'>: users
        <class 'node.ext.ugm.file.User'>: max
      <class 'node.ext.ugm.file.Groups'>: groups

Nothing written yet::

    >>> with open(ugm.users.file_path) as file:
    ...     print file.readlines()
    []

    >>> user.attrs.file_path
    '/.../principal_data/users/max'

    >>> file = open(user.attrs.file_path)
    Traceback (most recent call last):
      ...
    IOError: [Errno 2] No such file or directory: '/.../users/max'

Persist and read related files again::

    >>> ugm()
    >>> with open(ugm.users.file_path) as file:
    ...     print file.readlines()
    ['max:\n']

    >>> with open(user.attrs.file_path) as file:
    ...     print file.readlines()
    ['fullname:Max Mustermann\n', 
    'email:foo@bar.com\n']

Authentication is prohibited for users without a password::

    >>> ugm.users.authenticate('max', 'secret')
    False

Set Password for new User::

    >>> ugm.users.passwd('max', None, 'secret')
    >>> ugm()
    >>> with open(ugm.users.file_path) as file:
    ...     print file.readlines()
    ['max:...\n']

Password for inextistent user::

    >>> ugm.users.passwd('sepp', None, 'secret')
    Traceback (most recent call last):
      ...
    ValueError: User with id 'sepp' does not exist.

Password with wrong oldpw::

    >>> ugm.users.passwd('max', 'wrong', 'new')
    Traceback (most recent call last):
      ...
    ValueError: Old password does not match.

Set new password for max::

    >>> ugm.users.passwd('max', 'secret', 'secret1')
    >>> ugm()
    >>> with  open(ugm.users.file_path) as file:
    ...     print file.readlines()
    ['max:...\n']

Authentication::

    >>> ugm.users.authenticate('inexistent', 'secret')
    False

    >>> ugm.users.authenticate('max', 'secret')
    False

    >>> ugm.users.authenticate('max', 'secret1')
    True

Add another user::

    >>> user = ugm.users.create('sepp',
    ...                         fullname='Sepp Mustermann',
    ...                         email='baz@bar.com')
    >>> ugm.users.passwd('sepp', None, 'secret')
    >>> ugm()

    >>> ugm.printtree()
    <class 'node.ext.ugm.file.Ugm'>: ugm
      <class 'node.ext.ugm.file.Users'>: users
        <class 'node.ext.ugm.file.User'>: max
        <class 'node.ext.ugm.file.User'>: sepp
      <class 'node.ext.ugm.file.Groups'>: groups

    >>> with open(ugm.users.file_path) as file:
    ...     print file.readlines()
    ['max:...\n', 
    'sepp:...\n']

``__setitem__`` on user is prohibited::

    >>> ugm.users['max']['foo'] = user
    Traceback (most recent call last):
      ...
    NotImplementedError: User does not implement ``__setitem__``

Add new Group::

    >>> group = ugm.groups.create('group1', description='Group 1 Description')
    >>> group
    <Group object 'group1' at ...>

    >>> ugm.printtree()
    <class 'node.ext.ugm.file.Ugm'>: ugm
      <class 'node.ext.ugm.file.Users'>: users
        <class 'node.ext.ugm.file.User'>: max
        <class 'node.ext.ugm.file.User'>: sepp
      <class 'node.ext.ugm.file.Groups'>: groups
        <class 'node.ext.ugm.file.Group'>: group1

Nothing written yet::

    >>> with  open(ugm.groups.file_path) as file:
    ...     print file.readlines()
    []

    >>> group.attrs.file_path
    '/.../principal_data/groups/group1'

    >>> file = open(group.attrs.file_path)
    Traceback (most recent call last):
      ...
    IOError: [Errno 2] No such file or directory: '/.../groups/group1'

Persist and read related files again::

    >>> ugm()
    >>> with open(ugm.groups.file_path) as file:
    ...     print file.readlines()
    ['group1:\n']

    >>> with open(group.attrs.file_path) as file:
    ...     print file.readlines()
    ['description:Group 1 Description\n']

No members yet::

    >>> group.member_ids
    []

Setitem is forbidden on a group::

    >>> group['foo'] = ugm.users['max']
    Traceback (most recent call last):
      ...
    NotImplementedError: Group does not implement ``__setitem__``

A user is added to a group via ``add``::

    >>> id = ugm.users['max'].name
    >>> id
    'max'

    >>> group.add(id)
    >>> group.member_ids
    ['max']

    >>> group.users
    [<User object 'max' at ...>]

    >>> group['max']
    <User object 'max' at ...>

Nothing written yet::

    >>> with open(ugm.groups.file_path) as file:
    ...     print file.readlines()
    ['group1:\n']

    >>> ugm()
    >>> with open(ugm.groups.file_path) as file:
    ...     print file.readlines()
    ['group1:max\n']

Note, parent of returned user is users object, not group::

    >>> group['max'].path
    ['ugm', 'users', 'max']

Add another Group and add members::

    >>> group = ugm.groups.create('group2', description='Group 2 Description')
    >>> group
    <Group object 'group2' at ...>

    >>> group.add('max')
    >>> group.add('sepp')

    >>> ugm.printtree()
    <class 'node.ext.ugm.file.Ugm'>: ugm
      <class 'node.ext.ugm.file.Users'>: users
        <class 'node.ext.ugm.file.User'>: max
        <class 'node.ext.ugm.file.User'>: sepp
      <class 'node.ext.ugm.file.Groups'>: groups
        <class 'node.ext.ugm.file.Group'>: group1
          <class 'node.ext.ugm.file.User'>: max
        <class 'node.ext.ugm.file.Group'>: group2
          <class 'node.ext.ugm.file.User'>: max
          <class 'node.ext.ugm.file.User'>: sepp

    >>> with open(ugm.groups.file_path) as file:
    ...     print file.readlines()
    ['group1:max\n']

    >>> ugm()
    >>> with open(ugm.groups.file_path) as file:
    ...     print file.readlines()
    ['group1:max\n', 
    'group2:max,sepp\n']

``groups`` attribute on user::

    >>> max = ugm.users['max']
    >>> max.groups
    [<Group object 'group1' at ...>, 
    <Group object 'group2' at ...>]

    >>> sepp = ugm.users['sepp']
    >>> sepp.groups
    [<Group object 'group2' at ...>]

``group_ids`` attribute on user::

    >>> max.group_ids
    ['group1', 'group2']

    >>> sepp.group_ids
    ['group2']

``_compare_value`` helper::

    >>> users = ugm.users
    >>> users._compare_value('*', '')
    True

    >>> users._compare_value('**', '')
    False

    >>> users._compare_value('aa', 'aa')
    True

    >>> users._compare_value('aa', 'aaa')
    False

    >>> users._compare_value('*a*', 'abc')
    True

    >>> users._compare_value('*a', 'abc')
    False

    >>> users._compare_value('*c', 'abc')
    True

    >>> users._compare_value('a*', 'abc')
    True

    >>> users._compare_value('c*', 'abc')
    False

Some more users::

    >>> users.create('maxii')
    <User object 'maxii' at ...>

    >>> users.create('123sepp')
    <User object '123sepp' at ...>

    >>> users.keys()
    ['max', 'sepp', 'maxii', '123sepp']

Test Search on users::

    >>> users.search()
    []

    >>> users.search(criteria=dict(id='max'))
    ['max']

    >>> sorted(users.search(criteria=dict(id='max*')))
    ['max', 'maxii']

    >>> users.search(criteria=dict(id='sepp'))
    ['sepp']

    >>> sorted(users.search(criteria=dict(id='*sep*')))
    ['123sepp', 'sepp']

Search on users exact match::

    >>> users.search(criteria=dict(id='max'), exact_match=True)
    ['max']

    >>> users.search(criteria=dict(id='max*'), exact_match=True)
    Traceback (most recent call last):
      ...
    ValueError: Exact match asked but result not unique

    >>> users.search(criteria=dict(id='inexistent'), exact_match=True)
    Traceback (most recent call last):
      ...
    ValueError: Exact match asked but result length is zero

Search on users attribute list::

    >>> users.search(criteria=dict(id='max'), attrlist=['fullname', 'email'])
    [('max', {'fullname': 'Max Mustermann', 'email': 'foo@bar.com'})]

    >>> sorted(users.search(criteria=dict(id='max*'),
    ...                     attrlist=['fullname', 'email']))
    [('max', 
    {'fullname': 'Max Mustermann', 
    'email': 'foo@bar.com'}), 
    ('maxii', 
    {'fullname': '', 
    'email': ''})]

    >>> sorted(users.search(criteria=dict(id='*ax*'), attrlist=['id']))
    [('max', {'id': 'max'}), ('maxii', {'id': 'maxii'})]

Search on users or search::

    >>> sorted(users.search(criteria=dict(fullname='*Muster*', id='max*'),
    ...                     or_search=True))
    ['max', 'maxii', 'sepp']

    >>> users.search(criteria=dict(fullname='*Muster*', id='max*'),
    ...              or_search=False)
    ['max']

Some more groups::

    >>> groups = ugm.groups
    >>> groups.create('group3')
    <Group object 'group3' at ...>

    >>> groups.keys()
    ['group1', 'group2', 'group3']

Test Search on groups::

    >>> groups.search(criteria=dict(id='group1'))
    ['group1']

    >>> sorted(groups.search(criteria=dict(id='group*')))
    ['group1', 'group2', 'group3']

    >>> sorted(groups.search(criteria=dict(id='*rou*')))
    ['group1', 'group2', 'group3']

    >>> groups.search(criteria=dict(id='*3'))
    ['group3']

Search on groups exact match::

    >>> groups.search(criteria=dict(id='group1'), exact_match=True)
    ['group1']

    >>> groups.search(criteria=dict(id='group*'), exact_match=True)
    Traceback (most recent call last):
      ...
    ValueError: Exact match asked but result not unique

    >>> groups.search(criteria=dict(id='inexistent'), exact_match=True)
    Traceback (most recent call last):
      ...
    ValueError: Exact match asked but result length is zero

Search on groups attribute list::

    >>> groups['group1'].attrs['description'] = 'Group 1 Description'
    >>> groups['group2'].attrs['description'] = 'Group 2 Description'

    >>> sorted(groups.search(criteria=dict(id='group*'),
    ...                      attrlist=['description']))
    [('group1', 
    {'description': 'Group 1 Description'}), 
    ('group2', 
    {'description': 'Group 2 Description'}), 
    ('group3', 
    {'description': ''})]

    >>> groups.search(criteria=dict(id='*2'), attrlist=['id', 'description'])
    [('group2', {'id': 'group2', 'description': 'Group 2 Description'})]

Search on groups or search::

    >>> sorted(groups.search(criteria=dict(description='*Desc*', id='*g*'),
    ...                      or_search=True))
    ['group1', 'group2', 'group3']

    >>> groups.search(criteria=dict(description='*Desc*', id='*1'),
    ...               or_search=False)
    ['group1']

    >>> groups.search(criteria=dict(description='*Desc*', id='*3'),
    ...               or_search=False)
    []

Remove users and groups created for search tests::

    >>> del users['maxii']
    >>> del users['123sepp']
    >>> del groups['group3']

Delete user from group::

    >>> ugm.groups.printtree()
    <class 'node.ext.ugm.file.Groups'>: groups
      <class 'node.ext.ugm.file.Group'>: group1
        <class 'node.ext.ugm.file.User'>: max
      <class 'node.ext.ugm.file.Group'>: group2
        <class 'node.ext.ugm.file.User'>: max
        <class 'node.ext.ugm.file.User'>: sepp

    >>> del ugm.groups['group2']['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: 'inexistent'

    >>> del ugm.groups['group2']['max']
    >>> ugm.groups.printtree()
    <class 'node.ext.ugm.file.Groups'>: groups
      <class 'node.ext.ugm.file.Group'>: group1
        <class 'node.ext.ugm.file.User'>: max
      <class 'node.ext.ugm.file.Group'>: group2
        <class 'node.ext.ugm.file.User'>: sepp

Not persisted yet::

    >>> with open(ugm.groups.file_path) as file:
    ...     print file.readlines()
    ['group1:max\n', 
    'group2:max,sepp\n']

Call tree and check result::

    >>> ugm()
    >>> with open(ugm.groups.file_path) as file:
    ...     print file.readlines()
    ['group1:max\n', 
    'group2:sepp\n']

Recreate ugm object::

    >>> ugm = Ugm(name='ugm',
    ...           users_file=users_file,
    ...           groups_file=groups_file,
    ...           roles_file=roles_file,
    ...           data_directory=datadir)

Users ``__getitem__``::

    >>> ugm.users['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: 'inexistent'

    >>> ugm.users['max']
    <User object 'max' at ...>

Groups ``__getitem__``::

    >>> ugm.groups['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: 'inexistent'

    >>> ugm.groups['group1']
    <Group object 'group1' at ...>

``printtree`` of alredy initialized ugm instance::

    >>> ugm = Ugm(name='ugm',
    ...           users_file=users_file,
    ...           groups_file=groups_file,
    ...           roles_file=roles_file,
    ...           data_directory=datadir)
    >>> ugm.printtree()
    <class 'node.ext.ugm.file.Ugm'>: ugm
      <class 'node.ext.ugm.file.Users'>: users
        <class 'node.ext.ugm.file.User'>: max
        <class 'node.ext.ugm.file.User'>: sepp
      <class 'node.ext.ugm.file.Groups'>: groups
        <class 'node.ext.ugm.file.Group'>: group1
          <class 'node.ext.ugm.file.User'>: max
        <class 'node.ext.ugm.file.Group'>: group2
          <class 'node.ext.ugm.file.User'>: sepp

Role Management for User.

No roles yet::

    >>> user = ugm.users['max']
    >>> user.roles
    []

Add role via User object::

    >>> user.add_role('manager')
    >>> user.roles
    ['manager']

Add same role twice fails::

    >>> user.add_role('manager')
    Traceback (most recent call last):
      ...
    ValueError: Principal already has role 'manager'

Not written yet::

    >>> with open(ugm.roles_file) as file:
    ...     print file.readlines()
    []

After ``__call__`` roles are persisted::

    >>> user()
    >>> with open(ugm.roles_file) as file:
    ...     file.readlines()
    ['max::manager\n']

Add role for User via Ugm object::

    >>> ugm.add_role('supervisor', user)
    >>> user.roles
    ['manager', 'supervisor']

    >>> ugm.roles(user) == user.roles
    True

Call and check result::

    >>> ugm()
    >>> with open(ugm.roles_file) as file:
    ...     print file.readlines()
    ['max::manager,supervisor\n']

Remove User role::

    >>> user.remove_role('supervisor')
    >>> user.roles
    ['manager']

Remove inexistent role fails::

    >>> user.remove_role('supervisor')
    Traceback (most recent call last):
      ...
    ValueError: Principal does not has role 'supervisor'

Call persists::

    >>> user()
    >>> with open(ugm.roles_file) as file:
    ...     print file.readlines()
    ['max::manager\n']

Role Management for Group.

No roles yet::

    >>> group = ugm.groups['group1']
    >>> group.roles
    []

Add role via Group object::

    >>> group.add_role('authenticated')
    >>> group.roles
    ['authenticated']

Add same role twice fails::

    >>> group.add_role('authenticated')
    Traceback (most recent call last):
      ...
    ValueError: Principal already has role 'authenticated'

Group role not written yet::

    >>> with open(ugm.roles_file) as file:
    ...     print file.readlines()
    ['max::manager\n']

After ``__call__`` roles are persisted::

    >>> group()
    >>> with open(ugm.roles_file) as file:
    ...     print file.readlines()
    ['max::manager\n', 
    'group:group1::authenticated\n']

Add role for Group via Ugm object::

    >>> ugm.add_role('editor', group)
    >>> group.roles
    ['authenticated', 'editor']

    >>> ugm.roles(group) == group.roles
    True

Call and check result::

    >>> ugm()
    >>> with open(ugm.roles_file) as file:
    ...     print file.readlines()
    ['max::manager\n', 
    'group:group1::authenticated,editor\n']

Remove Group role::

    >>> group.remove_role('editor')
    >>> group.roles
    ['authenticated']

Remove inexistent role fails::

    >>> group.remove_role('editor')
    Traceback (most recent call last):
      ...
    ValueError: Principal does not has role 'editor'

Call persists::

    >>> group()
    >>> with open(ugm.roles_file) as file:
    ...     print file.readlines()
    ['max::manager\n', 
    'group:group1::authenticated\n']

Users ``__delitem__``::

    >>> users = ugm.users
    >>> del users['max']
    >>> ugm.printtree()
    <class 'node.ext.ugm.file.Ugm'>: ugm
      <class 'node.ext.ugm.file.Users'>: users
        <class 'node.ext.ugm.file.User'>: sepp
      <class 'node.ext.ugm.file.Groups'>: groups
        <class 'node.ext.ugm.file.Group'>: group1
        <class 'node.ext.ugm.file.Group'>: group2
          <class 'node.ext.ugm.file.User'>: sepp

    >>> users()
    >>> with open(ugm.users.file_path) as file:
    ...     print file.readlines()
    ['sepp:...\n']

User data is deleted::

    >>> os.listdir(os.path.join(ugm.data_directory, 'users'))
    ['sepp']

Roles for user are deleted as well::

    >>> with open(ugm.roles_file) as file:
    ...     print file.readlines()
    ['group:group1::authenticated\n']

Groups ``__delitem__``::

    >>> groups = ugm.groups
    >>> del groups['group1']
    >>> ugm.printtree()
    <class 'node.ext.ugm.file.Ugm'>: ugm
      <class 'node.ext.ugm.file.Users'>: users
        <class 'node.ext.ugm.file.User'>: sepp
      <class 'node.ext.ugm.file.Groups'>: groups
        <class 'node.ext.ugm.file.Group'>: group2
          <class 'node.ext.ugm.file.User'>: sepp

    >>> groups()
    >>> with open(ugm.groups.file_path) as file:
    ...     print file.readlines()
    ['group2:sepp\n']

Group data is deleted::

    >>> os.listdir(os.path.join(ugm.data_directory, 'groups'))
    ['group2']

Roles for group are deleted as well::

    >>> with open(ugm.roles_file) as file:
    ...     print file.readlines()
    []

Cleanup test environment::

    >>> import shutil
    >>> shutil.rmtree(tempdir)
