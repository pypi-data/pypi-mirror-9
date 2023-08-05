haufe.extended.sharepoint
================

``haufe.extended`` is a fork of Haufe's sharepoint. It is
made to allow non NTLM auth, adds Copy.asmx for documents
and provides a new set of perks for Lists

Features
--------

* Connect with non NTLM, and NTLM connections
* CRUD interface for Lists.asmx, Copy.asmx
* Adds attachment, file upload support
* Same core as the initial Haufe Sharepoint

Usage (parts borrowed from Haufe)
-----

In order to connect to Sharepoint you need the following parameters

- the Lists/Copy WSDL URL
- the ID/Name of the related Sharepoint list you want to interact with
- a valid Sharepoint username and password (having the related rights)

API usage
---------

Connecting to sharepoint
++++++++++++++++++++++++

In order to connect to Sharepoint you need to import the ``Connector``
method which is a factory return a ``ListEndPoint`` instance::


    > from haufe.sharepoint import Connector
    > url = 'http://sharepoint/bereiche/onlineschulungen/'
    > username = 'YourDomain\\account'
    > password = 'secret'
    > list_id = '60e3f442-6faa-4b49-814d-2ce2ec88b8d5'
    > service = Connector(url, username, password, list_id, NTLM=False)
	> service = Connector(url, username, password, list_id, NTLM=True)


Sharepoint list model introspection
+++++++++++++++++++++++++++++++++++

The internals of the list schema is available through the ``model`` property
of the ``ListEndPoint`` instance::

    > fields = service.model

The primary key of the list is exposed through the ``primary_key`` property::

    > primary_key = service.primary_key

The lists of all required field names and all fields is available through::

    > all_fields = service.all_fields
    > required_fields = service.required_fields

List item deletion
++++++++++++++++++

In order to delete list items by their primary key values, you can use
the ``deleteItems()`` method::

    > result = service.deleteItems('54', '55')
    > print result
    > print result.result
    > print result.ok

The ``result`` object is an instance of ``ParsedSoapResult`` providing a
flag ``ok`` (True|False) indicating the overall success or overall failure 
of the operation. The individual error codes are available by iterating over the 
``result`` property of the ``ParsedSoapResult`` instance.

Updating list items
+++++++++++++++++++

You can update existing list items by passing one or multiple dictionaries
to ``updateItems()``. Each dict must contain the value of the related primary key
(in this case the ``ID`` field)::

    > data = dict(ID='77', Title=u'Ruebennase', FirstName=u'Heinz')
    > result = service.updateItems(data)
    > print result
    > print result.result
    > print result.ok

``updateItems()`` will not raise any exception. Instead you need to
check the ``ok`` property of the result object and if needed the individual
items of the ``result`` property::

    # update an item (non-existing ID)
    > data = dict(ID='77000', Title=u'Becker')
    > result = service.updateItems(data)
    > print result
    > print result.result
    > print result.ok

Adding items to a list
++++++++++++++++++++++

The ``addItems()`` method works like the ``updateItems()`` method 
except that do not have pass in a primary key (since it is not known
on the client side). The assigned primary key value after adding
the item to the list should be available from the ``result`` object::

    > data = dict(Title=u'Ruebennase', FirstName=u'Heinz')
    > result = service.addItems(data)
    > print result
    > print result.result
    > print result.ok
    > print 'assigned ID:', result.result[0]['row']._ows_ID

Retrieving a single list item
+++++++++++++++++++++++++++++

``getItem()`` will return a single item by its primary key value::

    > data = service.getItem('77')     

Retrieving all list items
+++++++++++++++++++++++++

``getItems()`` will return all list items (use with care!)::

    > items = service.getItems()

Generic query API
+++++++++++++++++

``query(**kw)`` can be used to query the list with arbitrary query parameters
where each subquery must perform an exact match. All subqueries are combined
using a logical AND::

  > items = service.query(FirstName='Heinz', Title='Becker')

The result is returned a Python list of dictified list items.
All query parameters must represent a valid field name of the list (ValueError
exception raised otherwise).

In order to perform a substring search across _all_ query parameter you may
pass the ``mode='contains'`` parameter. To specify a prefix search across
all query parameters, use ``mode='beginswith'``.

View support
++++++++++++

``haufe.sharepoint`` supports list views of Sharepoint. You can either
set a default view used for querying Sharepoint like::

    > service.setDefaultView('{D9DF14B-21F2-4D75-B796-EA74647C30C6'}')

or you select the view on a per-query basis by passing the view name
as ``viewName`` method parameter (applies to ``getItem()``, 
``getItems()`` and ``query()``)::

    > items = service.getItems(viewName='{D9DF14B-21F2-4D75-B796-EA74647C30C6'}')
	
Creating/Deleting/Reading Attachments
+++++++++++

	> attachment = service.addAttachment(dict(listItemID='ITEM ID', fileName="A File", file=file))
	> attachments = service.getAttachments(dict(listItemID='ITEM ID'))
	> attachments = service.deleteAttachments(dict(listItemID='ITEM ID', url='FULL URL OF ATTACHMENT'))

Copy.asmx Support
+++++++++++

Uploading new documents:

	> service.upload(dict(
	> destinationUrl='my file',
	> fields=dict(
	> Name='A Document Title',
	> ),
	> overwrite=True,
    > file=file	
    > ))
	
Like attachment support in Lists.asmx file should be the path to a file. 
Fields are the meta data listed in the documents, they can also be
edited with another 'meta' dictionary. This will tell sharepoint
what types you are using. For example:

	> service.upload(
	> dict(destinationUrl='my file', 
	> fields=dict(MultiChoice='Blue'),
	> meta=dict(MultiChoice='MultiChoice')))

Tells 'MultiChoice' field is a MultiChoice and should not be treated
like any other type. 	


Overwriting Current Documents
++++++++++++

you can overwrite current documents. 
Using overwrite = True


Command line usage
------------------

``haufe.sharepoint`` comes with a small ``sharepoint-inspector`` commandline utility::

  sharepoint-inspector --url <URL> --list <LIST-ID-OR-NAME> --username <USERNAME> --password <PASSWORD> --cmd <CMD>

where <CMD> is either ``fields`` or ``items`` 



Requirements
------------

* Python 2.4 or higher (no support for Python 3.X)

Tested
------
* tested with Python 2.4-2.6
* suds 0.4.1 beta or checkout of the suds trunk (https://fedorahosted.org/suds/). suds 0.4.0 is _not_ sufficient!
* python-ntlm 1.0
* Microsoft Sharepoint Services 3.0 API

Author
------

Written for Haufe-Lexware GmbH, Freiburg, Germany.

| ZOPYX Limited
| Andreas Jung
| Charlottenstr. 37/1
| D-72070 Tuebingen
| www.zopyx.com
| info@zopyx.com

Extended by
-------

Nadir Hamid
| matrix.nad@gmail.com

Special Thanks:
-------
| Pat S