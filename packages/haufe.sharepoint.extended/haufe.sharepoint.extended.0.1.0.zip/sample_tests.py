# coding=UTF-8
import os
from haufe.sharepoint import Connector

""" All tests are using NTLM. If you need NTLM support, please add the NTLM """
""" flag in the connector. These tests are for both Lists.asmx and Copy.asmx and """
""" will give you a rough idea of how to use this library """


url = ''
username = ''
password = ''
list_id = ''

if username == 'username_here' or password == 'password_here':
	print "Please set your username, password and list ids to use tests, exiting.."
	exit(1)

service = Connector(url, username, password, list_id, NTLM=False)

print "Testing for Sharepoint Lists.asmx"
print "Connecting to: {0}".format(list_id)

print "Primary key is: " + service.primary_key

A_TITLE = "My Item"
A_DESCRIPTION = "Description"
## creating an item
result = service.addItems(dict(Title=A_TITLE, MLOT=A_DESCRIPTION))

## reading an item
## the last item on the list
result = service.query('exact', Title=A_TITLE)
last = result[0]
print "Last item created was: " + last.Title
assert(A_TITLE == last.Title)


## updating an item
##
A_NEW_TITLE = "Changed title"
res = service.updateItems(dict(ID=last.ID, Title=A_NEW_TITLE))

print "Title updated to: " + A_NEW_TITLE

## read the item 
## and check if the title has changed

result = service.query('exact',Title=A_NEW_TITLE)
item = result[0]

## is the new title there?
assert(item.Title == A_NEW_TITLE)

## adds an attachment
## to a given list item
## this time we 'attach' a JSON file

filename = 'example-attachment.json'
file = os.path.abspath("./tests/{0}".format(filename))

print "Testing attachment with: {0} (No overwrite)".format(file)

A_ATTACHMENT = service.addAttachment(dict(listItemID=last.ID, fileName="A File", file=file))

print "Last added attachment: {0}".format(A_ATTACHMENT)

## deleting an item
##
result = service.deleteItems(last.ID)

print "Item has been deleted: " + repr(result.ok)

## lastly check if the item is still there
## just in case
result = service.query('exact', ID=last.ID)
assert(len(result) == 0)

## Copy.asmx.
## this will test file uploading to documents
## also check for overwrites

url = ''
list_id = ''

print "Testing for Sharepoint Copy.asmx"
print "Connecting to library: {0}".format(list_id)

## example of 
## a document based instance
## using copy.asmx in place of Lists.asmx
## connecting to Reports
## we need a new service to this.
## if you use a different username/password
## for this list make sure to update
## username, password and list_id

list_id = 'Reports'
service1 = Connector(url, username, password, list_id, NTLM=False)

## uploads a document 
## fields are the meta
## data passed
## destination can either be relative
## or absolute
## in this case we know the list id, so 
## we're going relative
## absolute would be: https://wss.apan.org/s/PSP/Reports/te_1__s1t1.jpg,
## relative: test_1.jpg

filename = 'example-document.png'
file = os.path.abspath("./tests/{0}".format(filename))
print "Testing file upload with file: {0} (With overwrite)".format(file)

A_DOCUMENT = service1.upload(dict(
    destinationUrl=filename,
    fields=dict(
		Name='A Document Title',
     ),
	
	## meta is an aux to fields. When
	## using abstracted types, use.
	meta=dict(
		Name='Text'
	),
	overwrite=True,
    file=file	
))

## what happened?
## if it was good, we
## will get 'Success'
assert(A_DOCUMENT.Results.CopyResult[0]._ErrorCode == 'Success')

print "Item was uploaded with status: {0}".format(A_DOCUMENT.Results.CopyResult[0]._ErrorCode)

print "Tests are complete."
