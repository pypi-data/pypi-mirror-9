from pythonmarketo.helper  import http_lib 
import json
import time

class MarketoClient:    
    host = None
    client_id = None
    client_secret = None
    token = None
    expires_in = None
    valid_until = None
    token_type = None
    scope = None
    last_request_id = None
    
    def __init__(self, host, client_id, client_secret):
        assert(host is not None)
        assert(client_id is not None)
        assert(client_secret is not None)
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret

    def authenticate(self):
        if self.valid_until is not None and\
            self.valid_until > time.time():
            return

        args = { 
            'grant_type' : 'client_credentials', 
            'client_id' : self.client_id,
            'client_secret' : self.client_secret
        }
        data = http_lib.HttpLib().get("https://" + self.host + "/identity/oauth/token", args)
        if data is None: raise Exception("Empty Response")
        self.token = data['access_token']
        self.token_type = data['token_type']
        self.expires_in = data['expires_in']
        self.valid_until = time.time() + data['expires_in'] 
        self.scope = data['scope']

    def get_leads(self, filtr, values = [], fields = []):
        self.authenticate()
        values = values.split() if type(values) is str else values
        args = {
            'access_token' : self.token,
            'filterType' : str(filtr),
            'filterValues' : (',').join(values)
        }
        if len(fields) > 0:
            args['fields'] = ",".join(fields)
        data = http_lib.HttpLib().get("https://" + self.host + "/rest/v1/leads.json", args)
        if data is None: raise Exception("Empty Response")
        self.last_request_id = data['requestId']
        if not data['success'] : raise Exception(str(data['errors'])) 
        return data['result']

    def get_leads_by_listId(self, listId = None , batchSize = None, fields = []):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        if len(fields) > 0:
            args['fields'] = ",".join(fields)
        if batchSize:
            args['batchSize'] = batchSize   
        result_list = []    
        while True:
            data = http_lib.HttpLib().get("https://" + self.host + "/rest/v1/list/" + str(listId)+ "/leads.json", args)
            if data is None: raise Exception("Empty Response")
            self.last_request_id = data['requestId']
            if not data['success'] : raise Exception(str(data['errors'])) 
            result_list.extend(data['result'])
            if len(data['result']) == 0 or 'nextPageToken' not in data:
                break
            args['nextPageToken'] = data['nextPageToken']         
        return result_list    

    def get_activity_types(self):
        self.authenticate()
        args = {
            'access_token' : self.token 
        }
        data = http_lib.HttpLib().get("https://" + self.host + "/rest/v1/activities/types.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise Exception(str(data['errors'])) 
        return data['result']

        
    def get_lead_activity_page(self, activityTypeIds, nextPageToken, batchSize = None, listId = None):
        self.authenticate()
        activityTypeIds = activityTypeIds.split() if type(activityTypeIds) is str else activityTypeIds
        args = {
            'access_token' : self.token,
            'activityTypeIds' : ",".join(activityTypeIds),
            'nextPageToken' : nextPageToken
        }
        if listId:
            args['listId'] = listId
        if batchSize:
            args['batchSize'] = batchSize
        data = http_lib.HttpLib().get("https://" + self.host + "/rest/v1/activities.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise Exception(str(data['errors'])) 
        return data

    def get_lead_activity(self, activityTypeIds, sinceDatetime, batchSize = None, listId = None):
        activity_result_list = []
        nextPageToken = self.get_paging_token(sinceDatetime)
        moreResult = True
        while moreResult:
            result = self.get_lead_activity_page(activityTypeIds, nextPageToken, batchSize, listId)
            if result is None:
                break
            moreResult = result['moreResult']
            nextPageToken = result['nextPageToken']
            if 'result' in result:
                activity_result_list.extend(result['result'])
       
        return activity_result_list         
           
    def get_paging_token(self, sinceDatetime):
        self.authenticate()
        args = {
            'access_token' : self.token, 
            'sinceDatetime' : sinceDatetime
        }
        data = http_lib.HttpLib().get("https://" + self.host + "/rest/v1/activities/pagingtoken.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise Exception(str(data['errors'])) 
        return data['nextPageToken']

    def update_lead(self, lookupField, lookupValue, values):
        updated_lead = dict(list({lookupField : lookupValue}.items()) + list(values.items()))
        data = {
            'action' : 'updateOnly',
            'lookupField' : lookupField,
            'input' : [
             updated_lead
            ]
        }
        self.post(data)

    def create_lead(self, lookupField, lookupValue, values):
        new_lead = dict(list({lookupField : lookupValue}.items()) + list(values.items()))
        data = {
            'action' : 'createOnly',
            'lookupField' : lookupField,
            'input' : [
             new_lead
            ]
        }
        self.post(data)
           
    def post(self, data):
        self.authenticate()
        args = {
            'access_token' : self.token 
        }
        data = http_lib.HttpLib().post("https://" + self.host + "/rest/v1/leads.json" , args, data)
        if not data['success'] : raise Exception(str(data['errors']))
        print("Status:", data['result'][0]['status'])
