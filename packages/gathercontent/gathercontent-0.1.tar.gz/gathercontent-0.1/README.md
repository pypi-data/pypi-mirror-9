gathercontent
=============


This is a very simple API wrapper for GatherContent in Python. For more information about the GatherContent API, have a look at:

http://help.gathercontent.com/developer-api/


Dependencies
------------

You'll need `requests`. If you're installing via Pypi/pip, this should be installed automatically. If you need to install it manually, this was developed against `requests==2.5.1`, so it's probably best to use that.


Usage
-----

This module exposes all documented GatherContent API methods. Assuming the URL schema doesn't change, it should work with future API versions, too, as long as the URI's are all prefixed with `get_`. Right now, I've tested this with the following API methods:

- get_me – logged in user
- get_users – all visible users for given API key
- get_user (id) – user with specified id
- get_my_group – group that API user belongs to
- get_groups – all visible groups for given API key
- get_group (id) – group with specified id
- get_projects – all visible projects for given API key
- get_project (id) – project with specified id
- get_page (id) – page with specified id
- get_pages_by_project (id) – all pages belonging to project with specified id
- get_file (id) – file with specified id
- get_files_by_project (id) – all files belonging to project with specified id
- get_files_by_page (id) – all files belonging to page with specified id
- get_custom_state (id) – custom state with specified id
- get_custom_states_by_project (id)

The API takes the JSON responses and converts them into Python dictionaries. For example:

	>>> from gathercontent import GatherContent
	>>> gc = GatherContent(api_key="your-api-key-here", account_name="your-account-name-here")
	>>> gc.get_users()
	>>> users = gc.get_users()
	>>> type(users)
	<type 'dict'>
	>>> users
	{u'users': [{u'first_name': u'Example', u'last_name': u'User', u'created_at': u'2014-10-14 10:33:08', u'updated_at': u'2015-02-04 11:30:01', u'email': u'person@example.com', u'timezone': u'UTC', u'group_id': u'29122', u'id': u'75580'}], u'success': True}
	>>> gc.get_user(id=75580)
	{u'user': {u'first_name': u'Example', u'last_name': u'User', u'created_at': u'2014-10-14 10:33:08', u'updated_at': u'2015-02-04 11:30:01', u'email': u'person@example.com', u'timezone': u'UTC', u'group_id': u'29122', u'id': u'75580'}, u'success': True}


License
-------

The MIT License (MIT)

Copyright (c) 2015 FARM Digital Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


Credits
-------

Thanks to everyone at [FARM Digital](http://www.wearefarm.com/) for the code review before we published this.