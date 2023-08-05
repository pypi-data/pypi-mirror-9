# -*- coding: iso-8859-15 -*-

################################################################
# haufe.sharepoint
################################################################


import re
import logging
import sys
import os
import base64 ## for upload support
import urllib2
from ntlm import HTTPNtlmAuthHandler
from suds.client import Client
from suds.sax.element import Element
from suds.sax.attribute import Attribute
from suds.transport.https import WindowsHttpAuthenticated
from suds.transport.http import HttpAuthenticated
from logger import logger as LOG

# Sharepoint field descriptors start with *one* underscore (hopefully)
field_regex = re.compile(r'^_[a-zA-Z0-9]') 
_marker = object
CLIENT = dict()
MODEL = dict()
CONNECTED = False
VERBOSE = False
STDOUT = False
import patches

class Factory(object):
    def __init__(self):
        pass
        
    def connected(self):
        global CLIENT
        if 'connected' in CLIENT.keys():
            return True
        return False
        
    def set_connected(self):
        global CLIENT
        CLIENT['connected'] = True
        
    def generate(self):
        global CLIENT
        global VERBOSE
        return Connector(CLIENT['url'], 
                         CLIENT['username'], 
                         CLIENT['password'], 
                         CLIENT['list_id'], 
                         CLIENT['NTLM'], 
                         VERBOSE,
                         CLIENT['timeout'])


def stdoff():
    global STDOUT
    global VERBOSE
    if VERBOSE:
          return

    STDOUT = sys.stdout
    sys.stdout = open(os.devnull, 'wb')

def stdon():
    global STDOUT
    global VERBOSE
    if VERBOSE:
        return

    sys.stdout = STDOUT
    

class OperationalError(Exception):
    """ Generic error """

class NotFound(Exception):
    """ List item not found """

class DictProxy(dict):
    """ Dict-Proxy for mapped objects providing attribute-style access.
    """

    def __getattribute__(self, name):
        if name in dict.keys(self):
            return self.get(name)
        return super(dict, self).__getattribute__(name) 

    def __getattr__(self, name, default=None):
        if name in dict.keys(self):
            return self.get(name, default)
        return super(dict, self).__getattr__(name, default) 


def Connector(url, username, password, list_id, NTLM=True, verbose=False, timeout=65):
    global CLIENT
    global VERBOSE

    """ Sharepoint SOAP connector factory """

    if not 'connected' in CLIENT.keys():
        LOG.info('Connecting to Sharepoint (%s, %s, %s)' % (url, username, list_id))

    VERBOSE = verbose

    if NTLM:
        transport = WindowsHttpAuthenticated(username=username,
											 password=password,
											 timeout=timeout)
    else:
        transport = HttpAuthenticated(username=username, password=password)

    r = re.findall(r"copy.asmx", url)
    if len(r) > 0:
        copy = True
    else:
        copy = False
	
    #if not 'Lists.asxml' in url:
     #   url = url + '/_vti_bin/Lists.asmx?WSDL'
    try:
        client = Client(url, transport=transport)
        CLIENT['url'] = url
        CLIENT['username'] = username
        CLIENT['password'] = password
        CLIENT['list_id'] = list_id
        CLIENT['NTLM'] = NTLM
        CLIENT['timeout'] = timeout
        CLIENT['copy'] = copy
        #client.set_options(service='Lists', port='ListsSoap12')
        c = ListEndpoint(client, list_id, copy=CLIENT['copy'])
        CLIENT['connected'] = True
        return c
        
    except Exception, e:
        # *try* to capture authentication related error.
        # Suds fails dealing with a 403 response from Sharepoint in addition
        # it is unable to deal with the error text returned from Sharepoint as
        # *HTML*.
        if '<unknown>' in str(e):
            raise OperationalError('Unknown bug encountered - *possibly* an authentication problem (%s)' % e)
        raise 


class ParsedSoapResult(object):
    """ Represent he result datastructure from sharepoint in a 
        mode Pythonic way. The ParsedSoapResult class exposes two attributes:
        ``ok`` - True if all operations completed successfully,
                  False otherwise
        ``result`` - a list of dicts containing the original SOAP
                  response ``code`` and ``text``
    """

    def __init__(self, results):
        self.raw_result = results
        self.ok = True
        self.result = list()
        # Stupid SOAP response are either returned as single 'Result'
        # instance or a list (depending on the number of list items touched
        # during one SOAP operation.
        if isinstance(results.Results.Result, (list, tuple)):
            results = [r for r in results.Results.Result]
        else:
            results = [results.Results.Result]
        for item_result in results:
            d = dict(code=item_result.ErrorCode,
                     success=item_result.ErrorCode=='0x00000000')
            for key in ('ErrorText', ):
                value = getattr(item_result, key, _marker)
                if value is not _marker:
                    d[key.lower()] = value

            row = getattr(item_result, 'row', _marker)
            if row is not _marker:
                # should be serialized
                d['row'] = item_result.row

            self.result.append(d)
            if item_result.ErrorCode != '0x00000000':
                self.ok = False

class ListEndpoint(object):

    def __init__(self, client, list_id, copy=False):
        global CONNECTED
        global CLIENT
        global MODEL
        self.iclient = client
        self.iservice = client.service
        self.client = client
        self.service = client.service
        self.list_id = list_id
        self.viewName = None

        ## find the base given the list id and url
        self.base = re.sub('_vti.*', '', CLIENT['url']) + list_id + '/'
        self.lbase = re.sub('_vti.*', '', CLIENT['url']) + 'Lists/' + list_id + '/'
        # perform some introspection on the list

        if not CONNECTED:
            if not copy:
                self.model = MODEL['fields'] = self._getFields()       
                self.required_fields = MODEL['required_fields'] = self._required_fields()
                self.all_fields = MODEL['keys'] =self.model.keys()
                self.primary_key = MODEL['primary_key'] = self._find_primary_key()

            CONNECTED = True
        else:
            if not 'fields' in MODEL.keys() and not copy:
                self.model = MODEL['fields'] = self._getFields() 
                self.required_fields = MODEL['required_fields'] = self._required_fields()
                self.all_fields = MODEL['keys'] = self.model.keys()
                self.primary_key = MODEL['primary_keys'] = self._find_primary_key()
                self.model = MODEL['fields']
                self.required_fields = MODEL['required_fields']
                self.all_fields = MODEL['keys']

        Factory().set_connected()

    def _getFields(self):
        """ extract field list """
        stdoff()
        list_ = self.client.service.GetList(self.list_id)
        stdon()
        fields = dict()
        for row in list_.List.Fields.Field:
            if row._Name.startswith('_'):
                continue
            # dictify field description (chop of leading underscore)
            d = dict()
            for k, v in row.__dict__.items():
                if field_regex.match(k):
                    # chop of leading underscore
                    d[unicode(k[1:])] = v
            fields[row._Name] = d
        return fields

    def _find_primary_key(self):
        """ Return the name of the primary key field of the list """
        for k, field_d in self.model.items():
            if field_d.get('PrimaryKey') == u'TRUE':
                return k
        raise OperationalError('No primary key found in sharepoint list description')

    def _required_fields(self):
        """ Return the list of required field names in Sharepoint """
        return [d['Name'] 
                for d in self.model.values() 
                if d.get('Required') == 'TRUE']

    def _serializeListItem(self, item):
        """ Serialize a list item as dict """
        d = DictProxy()
        for fieldname in self.model:
            v = getattr(item, '_ows_' + fieldname, _marker)
            if v is _marker:
                v = None
            d[fieldname] = v 
        return d

    def _preflight(self, data, primary_key_check=True):
        """ Perform some sanity checks on data """

        # data must include the value of the primary key field            
        value_primary_key = data.get(self.primary_key)
        if primary_key_check and value_primary_key is None:
            raise ValueError('No value for primary key "%s" found in update dict (%s)' % (self.primary_key, data))

        data_keys = set(data.keys())
        all_fields = set(self.all_fields)
        if not data_keys.issubset(all_fields):
            disallowed = ', '.join(list(data_keys - all_fields))
            raise ValueError('Data dictionary contains fieldnames unknown to the Sharepoint list model (Disallowed field names: %s)' % disallowed)

    def setDefaultView(self, viewName):
        """ set the default viewName parameter """
        self.viewName = viewName

    def getItems(self, rowLimit=999999999, viewName=None):
        """ Return all list items without further filtering """
        stdoff()
        items = Factory().generate().client.service.GetListItems(self.list_id, viewName=viewName or self.viewName, rowLimit=rowLimit)
        stdon()
        if int(items.listitems.data._ItemCount) > 0:
            return [self._serializeListItem(item) for item in items.listitems.data.row]
        return []

    def getItem(self, item_id, viewName=None):
        """ Return all list items without further filtering """
        query0= Element('ns1:query')
        query = Element('Query')
        query0.append(query)
        where = Element('Where')
        query.append(where)
        eq = Element('Eq')
        where.append(eq)
        fieldref = Element('FieldRef').append(Attribute('Name', self.primary_key))
        value = Element('Value').append(Attribute('Type', 'Number')).setText(item_id)
        eq.append(fieldref)
        eq.append(value)
        viewfields = Element('ViewFields')
        viewfields.append(Element('FieldRef').append(Attribute('Name', self.primary_key)))
        queryOptions = Element('queryOptions')
        stdoff()
        result = Factory().generate().client.service.GetListItems(self.list_id, 
                                          viewName=viewName or self.viewName, 
                                          query=query0,  
                                          viewFields=viewfields, 
                                          queryOptions=queryOptions, 
                                          rowLimit=1)
        stdon()
        if int(result.listitems.data._ItemCount) > 0:
            return self._serializeListItem(result.listitems.data.row)
        return []

    def query(self, mode='exact', viewName=None, **kw):
        """ A generic query API. All list field names can be passed to query()
            together with the query values. All subqueries are combined using AND.
            All search criteria must perform an exact match. A better
            implementation of query() may support the 'Contains' or 'BeginsWith'
            query options (as given through CAML). The mode=exact ensures an exact
            match of all query parameter. mode=contains performs a substring search
            across *all* query parameters. mode=beginswith performs a prefix search
            across *all* query parameters.
        """

        if not mode in ('exact', 'contains', 'beginswith'):
            raise ValueError('"mode" must be either "exact", "beginswith" or "contains"')

        # map mode parameters to CAML query options
        query_modes = {'exact' : 'Eq', 'beginswith' : 'BeginsWith', 'contains' : 'Contains'}

        query0= Element('ns1:query')
        query = Element('Query')
        query0.append(query)
        where = Element('Where')
        query.append(where)

        if len (kw) > 1: # more than one query parameter requires <And>
            and_= Element('And')
            where.append(and_)
            where = and_

        # build query 
        for k, v in kw.items():
            if not k in self.all_fields:
                raise ValueError('List definition does not contain a field "%s"' % k)
            
            query_mode = Element(query_modes[mode])
            where.append(query_mode)
            fieldref = Element('FieldRef').append(Attribute('Name', k))
            value = Element('Value').append(Attribute('Type', self.model[k]['Type'])).setText(v)
            query_mode.append(fieldref)
            query_mode.append(value)

        viewfields = Element('ViewFields')
        viewfields.append(Element('FieldRef').append(Attribute('Name', self.primary_key)))
        queryOptions = Element('queryOptions')
        stdoff()
        result = Factory().generate().client.service.GetListItems(self.list_id, 
                                          viewName=viewName or self.viewName, 
                                          query=query0,  
                                          viewFields=viewfields, 
                                          queryOptions=queryOptions, 
                                          )
        stdon()
        row_count = int(result.listitems.data._ItemCount)
        if row_count == 1:
            return [self._serializeListItem(result.listitems.data.row)]
        elif row_count > 1:
            return [self._serializeListItem(item) for item in result.listitems.data.row]
        else:
            return []

    def deleteItems(self, *item_ids):
        """ Remove list items given by value of their primary key """
        batch = Element('Batch')
        batch.append(Attribute('OnError','Return')).append(Attribute('ListVersion','1'))
        for i, item_id in enumerate(item_ids):
            method = Element('Method')
            method.append(Attribute('ID', str(i+1))).append(Attribute('Cmd', 'Delete'))
            method.append(Element('Field').append(Attribute('Name', self.primary_key)).setText(item_id))
            batch.append(method)
        updates = Element('ns0:updates')
        updates.append(batch)
        stdoff()
        result = Factory().generate().client.service.UpdateListItems(self.list_id, updates)
        stdon()
        return ParsedSoapResult(result)
		
    """
	base64 encode an attachment
	then upload to a list item
	
    @param data
	"""
    def addAttachment(self, data):
        if not 'raw' in data.keys(): data['raw'] = False
        if not 'overwrite' in data.keys(): data['overwrite'] = False
 
        if data['raw']:
           f = data['f']
        else:
           f = base64.b64encode(open(os.path.abspath(data['file']), 'rb').read())

        if data['overwrite']:
           """ 
		      delete an existing attachment 
		      only attempt as we do not want to bother a attachment upload
		   """
           try:
		        self.deleteAttachment(dict(listItemID=data['listItemID'], 
                                           url="{0}Attachments/{1}/{2}".format(self.lbase, 
																			    data['listItemID'], 
																			    data['fileName'])))
           except:
		        pass
		
        stdoff()
        result = Factory().generate().client.service.AddAttachment(self.list_id, fileName=data['fileName'], listItemID=data['listItemID'], attachment=f)
        stdon()
        return result ## no need if we have an error it will warn
	
	"""
    get an attachment.
	needs list item id

    @param data
	"""
    def getAttachments(self, data):
        stdoff()
        cli = Factory().generate()
        result = cli.client.service.GetAttachmentCollection(self.list_id, listItemID=data['listItemID'])
        stdon()
        
        return result.Attachments
		
    """ 
    deletes any attachments
    needs the attachment as
    first parameter
    """
    def deleteAttachment(self, data):
        stdoff()
        cli = Factory().generate()
        result = cli.client.service.DeleteAttachment(self.list_id, listItemID=data['listItemID'], url=data['url'])
        stdon()
        
        return result

    """
    uploads a new file
    to a document
    """
    def upload(self,data):
        stdoff()
        if not 'raw' in data.keys(): data['raw'] = False
		
        """ to hack for a overwrite, we have to set the source url base as the filename """
        """ see: http://sharepoint.stackexchange.com/questions/39982/overwrite-sharepoint-document-using-copyintoitems-service-of-copy-asmx """
	
        if not 'meta' in data.keys():
           data['meta'] = dict()
        if not 'overwrite' in data.keys():
           data['overwrite'] = False
           
        if data['overwrite']:
	       data['sourceUrl'] = data['destinationUrl']
        else:
		   data['sourceUrl'] = self.base + data['destinationUrl']
		   
        if data['raw']:
           f = data['f']
        else:
           f = base64.b64encode(open(os.path.abspath(data['file']), 'rb').read())

        if not len(re.findall('http', data['destinationUrl'])) > 0:
               data['destinationUrl'] = self.base + data['destinationUrl']

        du = Element('DestinationUrls')
        du.append(Element('string').setText(data['destinationUrl']))

        fit_m = Element('Fields')
        for k,v in data['fields'].iteritems():
            fit = Element('FieldInformation')
            bool_type = False
				
            """
                <FieldInformation Type="Invalid or Integer or Text or Note or DateTime or Counter or Choice or Lookup or Boolean or Number or Currency or URL or Computed or Threading or Guid or MultiChoice or GridChoice or Calculated or File or Attachments or User or Recurrence or CrossProjectLink or ModStat or AllDayEvent or Error" DisplayName="string" InternalName="string" Id="guid" Value="string" />
            """
            if k in data['meta'].keys():
                if data['meta'][k] == 'Boolean':
                     bool_type = True
					
                fit.append(Attribute('Type', data['meta'][k]))

            else:
                if isinstance(v, bool):
                      fit.append(Attribute('Type', 'Boolean'))				
                elif isinstance(v, float) or isinstance(v, int):
                      fit.append(Attribute('Type', 'Number'))  

                else:					
                      fit.append(Attribute('Type', 'Text'))

               
            if isinstance(v, bool):
                v = 'true' if v else 'false'
            if bool_type:
                """ accept either Yes, No, 0, 1, true, false """
                if v in ['Yes', 1]:
                      v = 'true'
                elif v in ['No', 0]:
                      v = 'false'
					  
            if isinstance(v, list):
                choices = Element('choices')
                 
                for i in v:
                     if isinstance(i, tuple):
                         default = Element('default').setText(i[1])
                     else:
			 choice = Element('choice').setText(i)
			 choices.append(choice)
						 
                fit.append(choices)
   
            """ make sure attribute newlines are escaped with CLRF """
            if isinstance(v, str):
                v = re.sub(r'\n|<br\/>|\r\n', '&#13;&#10;', v)
                v = re.sub("\n", '&#13;&#10;', v)
                v = unicode(v, errors='ignore')
         
            fit.append(Attribute('InternalName', v))
            fit.append(Attribute('DisplayName', unicode(k, errors='ignore')))
            #fit.append(Attribute('FillInChoice', 'TRUE'))
            fit.append(Attribute('Value', v))
            #fit.setText(v)
            fit_m.append(fit)

        cli = Factory().generate()
        result = cli.client.service.CopyIntoItems(
        SourceUrl=data['sourceUrl'], 
        DestinationUrls=du, 
        Fields=fit_m,
        Stream=f)    
        stdon()
		
        return result	

    """
	get an updload with
	its fields
	"""
    def getUpload(self, data):
        stdon()
        cli = Factory().generate()
		
        if not len(re.findall('http', data['url'])) > 0:
               data['url'] = self.base + data['url']
			 

        result = cli.client.service.GetItem(self.list_id, data['url'])
        stdoff()
        return result	

    def updateItems(self, *update_items):
        """ Update list items as given through a list of update_item dicts
            holding the data to be updated. The list items are identified
            through the value of the primary key inside the update dict.
        """
        batch = Element('Batch')
        batch.append(Attribute('OnError','Return')).append(Attribute('ListVersion','1'))
        for i, d in enumerate(update_items):
            self._preflight(d)
            method = Element('Method')
            method.append(Attribute('ID', str(i+1))).append(Attribute('Cmd', 'Update'))
            for k,v in d.items():
                method.append(Element('Field').append(Attribute('Name', k)).setText(v))
            batch.append(method)
        updates = Element('ns0:updates')
        updates.append(batch)
        stdoff()
        result = Factory().generate().client.service.UpdateListItems(self.list_id, updates)
        stdon()
        return ParsedSoapResult(result)

    def addItems(self, *addable_items):
        """ Add a sequence of items to the list. All items must be passed as dict.
            The list of assigned primary key values should from the 'row' values of 
            the result object.
        """
        batch = Element('Batch')
        batch.append(Attribute('OnError','Return')).append(Attribute('ListVersion','1'))
        for i, d in enumerate(addable_items):
            method = Element('Method')
            method.append(Attribute('ID', str(i+1))).append(Attribute('Cmd', 'New'))
            for k,v in d.items():
                method.append(Element('Field').append(Attribute('Name', k)).setText(v))
            batch.append(method)
        updates = Element('updates')
        updates.append(batch)
        stdoff()
        result = Factory().generate().client.service.UpdateListItems(self.list_id, updates)
        stdon()
        return ParsedSoapResult(result)

    def checkout_file(self, pageUrl, checkoutToLocal=False):
        """ Checkout a file """
        return Factory().generate().client.service.CheckOutFile(pageUrl, checkoutToLocal)

    def checkin_file(self, pageUrl, comment=''):
        return Factory().generate().client.service.CheckInFile(pageUrl, comment)

