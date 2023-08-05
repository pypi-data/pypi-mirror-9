Box Python V2 SDK
=================


Box Python SDK for v2 of the Box API.

Featuring:

* Automatic tokens refresh (client does not have to handle token expiration)
* Big file upload (upload by chunk and whole file is never loaded in memory)
* Chunked download
* Searching

###Prerequisites
* requests

Installation
------------
```shell
pip install boxv2
```
Quick Start
-----------

### Authenticate
The authentication workflow is a 2-step process that first retrieves an *Auth Code* and then exchanges it for *Access/Refresh Tokens*

#####First step
```python
>>> from boxv2 import BoxAuthenticateFlow, BoxSession, BoxError
>>>
>>> flow = BoxAuthenticateFlow('<client_id>', '<client_secret>')
>>> flow.get_authorization_url()
'https://www.box.com/api/oauth2/authorize?response_type=code&client_id=<client_id>&state=authenticated'
>>>
```
If you dont' have a client id or client secret, you can get one here: https://app.box.com/developers/services

By going through the url provided, you can get the authorisation code.

#####Second step
```python
>>> access_token, refresh_token = flow.get_access_tokens('<auth_code>')
```
*The authorisation code is valid only 30 seconds. So be quick ;)*
### Create session
```python
>>> def tokens_changed(refresh_token, access_token):
...    save_to_file(refresh_token, access_token)
...
>>> box = BoxSession('<client_id>', '<client_secret>', refresh_token, access_token, tokens_changed)
```
The *Access Token* expires every hour. When using this session with an *Access Token* expired, a new one will be requested automatically.

Use ```tokens_changed``` callback to backup *Access/Refresh Token* each time they change. If you do not backup them, next time you create a session, you will have to follow the authenticate flow first (with ```BoxAuthenticateFlow```).
    

### Get Folder Information
```python
>>> box.get_folder_info(0)
{u'item_collection': {u'total_count': 1, u'offset': 0, u'limit': 100, u'order': [{u'direction': u'ASC', u'by': u'type'}, {u'direction': u'ASC', u'by': u'name'}], u'entries': [{u'sequence_id': u'0', u'etag': u'0', u'type': u'folder', u'id': u'1230276227'...
```

### Create Folder
```python
>>> response = box.create_folder('my_folder')
>>> print 'Folder ID: %s' % response['id']
Folder ID: 1230944187
>>>
```

### Upload a New File
```python
>>> response = box.upload_file('test.txt', 1230944187, '/tmp/test.txt')
>>> print 'File ID: %s' % response['entries'][0]['id']
File ID: 11006194629
>>>
```
*For big files, use ```chunk_upload_file```*

### Download a File
```python
>>> box.download_file(11006194629, '/tmp/test_dl.txt')
>>>
```

### Find Folder/File ID from Name
```python
>>> box.find_id_in_folder('test.txt', 1230944187)
11006194629
>>>
```

### Searching for files
```python
>>> response = box.search(query="test",limit=30)
>>> print "Searched File ID: %s" % response['entries'][0]['id']
Searched File ID: 11006194629
```
For the complete list of search parameters go to: https://developers.box.com/docs/#search


### Getting User's information
```python
>>> response = box.get_user_info()
>>> print "User ID: %s" % response['id']
Searched File ID: 17738362
```



Handling errors
---------------
```python
>>> try:
...    box.create_folder('my_folder')
... except BoxError, berr:
...    if berr.status == 409:
...       print 'Item with same name already exists'
...    else:
...       print '%s' % berr
...
Item with same name already exists
>>>
```

For a complete list of error code : http://developers.box.com/docs/#errors

Automatic tokens refresh
------------------------

The *Access Token* expires every hour. When you use ```BoxSession``` class with an *Access Token* expired, a new one will be requested automatically.

So if you use ```box.create_folder('my_folder')``` and the *Access Token* has just expired, a request to have a new one is made. As soon as the new *Access Token* is retrieved (with new *Refresh Token* too), your original request (create folder) is made. Then the repsonse of the create folder is returned.

When new *Access/Refresh Token* are retrieved the ```tokens_changed``` callback is called. This is the good time to backup them, so next time you instantiate ```BoxSession``` you will have valid tokens.

Documentation
-------------
[Click here for the docs](https://rawgithub.com/octonius/Boxv2/master/docs/_build/html/index.html "Reference documentation")

Project Status
--------------

Here is the files/folders actions available right now:
- get_folder_info
- create_folder
- delete_folder
- get_folder_items
- upload_file
- download_file
- search

Adding an action is easy as:
```python
def delete_folder(self, folder_id):
    return self.__request("DELETE", 
                            "folders/%s" % (folder_id, ),
                            querystring={'recursive': 'true'})
```

Inspired from
-------------

The project is inspired from https://github.com/wesleyfr/boxpython.


Contributing
------------

We are glad to receive contributions.To contribute

1. Clone this repository `git clone https://github.com/Octonius/Boxv2`
2. Make the changes.
3. Commit the changes and send a pull request

### Tips for contributing

* Make sure to conform to [PEP-8](http://legacy.python.org/dev/peps/pep-0008/ "PEP 8 style guide")
