from pickle import TRUE
import requests
from urllib import parse
import json
import logging
from copy import deepcopy

class BankingCloudAPI:
    
    def __init__(self,bcUser):
        self.bcUserInfo = bcUser.getUserInfo()
        self.bearerHeader = {}
        self.bearerToken = {}
        self.logger = logging.getLogger(__name__)

    '''
    Generic Post Request entry point
    Body type is Json
    as authenticaiton api only accept 'application/x-www-form-urlencoded;charset=utf-8', 
    Using JSON for authentication post will result in 415 unsupported media type
    Added a parameter urlencoded to differentiate the two
    Return the entire json object as dict. Important key = access token, 'expires_in': 186
    '''

    def request(self,identifier,inputs_dict,urlencoded=False,bypass_check=False):
        api_meta_data = identifier()
        http_type = api_meta_data['http_type']
        name = api_meta_data['name']
        if bypass_check or self.is_valid_token(api_meta_data):       
            #print(apiMetadata)
            input_data_list= api_meta_data['requiredParams']      
            endpoint = api_meta_data['endpoint']
            required_data_dict = dict.fromkeys(input_data_list)
            name = api_meta_data['name']
            for d in required_data_dict:
                try:
                    required_data_dict[d] = inputs_dict[d]
                except KeyError as e:
                    print(e.args + ' : ' + 'Missing input in APIs Call ' + name + ' : ' + d)
            headers  = deepcopy(self.bearerHeader)
            self.logger.info(f'Sending {http_type} Request with API[{name}]')
            self.logger.debug('with http_type ' + http_type)
            self.logger.debug('with headers ' + str(headers))
            self.logger.debug('To Endpoint ' + endpoint)
            self.logger.debug('with data ' + str(required_data_dict))
            if http_type=='POST':
                if urlencoded:
                    headers.update({'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8','Accept':'application/json'})
                    encodedRequriedData = parse.urlencode(required_data_dict)
                    response = requests.post(endpoint, headers= headers, data=required_data_dict)
                else:
                    headers.update({'Content-Type': "application/json"})
                    response = requests.post(endpoint, headers= headers, json=required_data_dict)
            elif http_type=='GET':
                 headers.update({'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8','Accept':'application/json'})
                 response = requests.get(endpoint, headers=headers,params=required_data_dict)
            elif http_type=='PUT':
                headers.update({'Content-Type': "application/json"})
                response = requests.request('PUT', endpoint, headers=headers, data=json.dumps(required_data_dict))
            else:
                raise Exception('Unauthorized HTTP Type obtained:{http_type}')
            status_code= response.status_code
            self.logger.info(f'Sending {http_type} Request with API[{name}] with status code {status_code}')
            if status_code != 200:
                self.logger.error(f'Hit Error with HTTP Request. Result Status Code = {status_code}')
            try:
                return {'status' : response.status_code, 'body': response.json()}
            except:
                return {'status' : response.status_code,'body': [{}]}
        else:
            self.logger.error(f'Failed {http_type} Request with API{name}]')
            raise('Failed to submit {http_type} request due to invalid token')

    def post(self,identifier,postData,urlencoded=False,bypass_check=False):
        apiMetadata = identifier()
        if bypass_check or self.is_valid_token(apiMetadata):  
            
            headers = {"Content-Type": "application/json"}
            #print(apiMetadata)
            postDataList= apiMetadata['requiredParams']
            endpoint = apiMetadata['endpoint']
            requiredData = dict.fromkeys(postDataList)
            for d in requiredData:
                try:
                    requiredData[d] = postData[d]
                except KeyError as e:
                    print(e.args + ' : ' + 'Missing input in APIs Call ' + apiMetadata['name'] + ' : ' + d)
            headers  = deepcopy(self.bearerHeader)
            self.logger.info('Sending Post Request with API[' + str(apiMetadata['name']) + ']')
            self.logger.debug('with headers ' + str(headers))
            self.logger.debug('To Endpoint ' + str(endpoint))
            self.logger.debug('with data ' + str(requiredData))
            if urlencoded:
                headers.update({'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8','Accept':'application/json'})
                encodedRequriedData = parse.urlencode(requiredData)
                response = requests.post(endpoint, headers= headers, data=requiredData)
            else:
                headers.update({'Content-Type': "application/json"})
                response = requests.post(endpoint, headers= headers, json=requiredData)

            self.logger.info('Sending Post Request with API[' + str(apiMetadata['name']) + '] with status code ' + str(response.status_code))
            if response.status_code != 200:
                self.logger.error(f'Hit Error with HTTP Request. Result Status Code = {response.status_code}')

            try:
                return {'status' : response.status_code, 'body': response.json()}
            except:
                return {'status' : response.status_code,'body': [{}]}
        else:
            self.logger.error('Failed Post Request with API[' + str(apiMetadata['name']) + ']')
            raise('Failed to submit Post request due to invalid token')
    '''
    Generic Put entry point
    '''
    def put(self,identifier,putParams):
        apiMetadata = identifier()
        if self.is_valid_token(apiMetadata):     
            headers = {'Content-Type': 'application/json'}
            #print(apiMetadata)
            putDataList= apiMetadata['requiredParams']
            endpoint = apiMetadata['endpoint']
            requiredData = dict.fromkeys(putDataList)
            for d in requiredData:
                try:
                    requiredData[d] = putParams[d]
                except KeyError as e:
                    print(e.args + ' : ' + 'Missing input in APIs Call ' + identifier + ' : ' + d)
            headers.update(self.bearerHeader)
            #print(requiredData)
            response = requests.request('PUT', endpoint, headers=headers, data=json.dumps(requiredData))
            #print(response.status_code)
            try:
                return {'status' : response.status_code, 'body': response.json()}
            except:
                return {'status' : response.status_code,'body': [{}]}
        
    '''
    Generic Get entry point
    '''
    def get(self,identifier,getParams,bypass_check=False):
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8','Accept':'application/json'}
        apiMetadata = identifier()
        if bypass_check or  self.is_valid_token(apiMetadata):
            getDataList= apiMetadata['requiredParams']
            endpoint = apiMetadata['endpoint']
            requiredData = dict.fromkeys(getDataList)
            for d in requiredData:
                try:
                    requiredData[d] = getParams[d]
                except KeyError as e:
                    print(e.args + ' : ' + 'Missing input in APIs Call ' + identifier + ' : ' + d)
            #print(requiredData)
            headers.update(self.bearerHeader)
            self.logger.info('Sending Get Request with API[' + str(apiMetadata['name']) + ']')
            #print(headers)
            response = requests.get(endpoint, headers=headers,params=requiredData)
            try:
                return {'status' : response.status_code, 'body': response.json()}
            except:
                return {'status' : response.status_code,'body': [{}]}
        else:
            self.logger.error('Failed Get Request with API[' + str(apiMetadata['name']) + ']')
            raise('Failed to submit Get request due to invalid token')

    def authenticate(self):
        name= 'authenticate'
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8','Accept':'application/json'}
        requestParams = ['username','password','client_id','client_secret','grant_type','scope']
        endpoint = r'https://gtja.bankingcloud.moodysanalytics.com/oauth2/token'
        return {
            'http_type': 'POST',
            'name' : name,
            'endpoint' : endpoint,
            'requiredParams' : requestParams
        }

    '''
    Check Token validity{
    only skip when the actual api calling is to authenticate oneself
    '''

    def tokenValidation(self):
        name= 'tokenValidation'
        requestParams = []
        endpoint = r'https://gtja.bankingcloud.moodysanalytics.com/api/cr/nonprod/dev/v1/ping'
        return {
            'http_type': 'GET',
            'name' : name,
            'endpoint' : endpoint,
            'requiredParams' : requestParams
        }

    def is_valid_token(self,api_metadata,trials=1):
        self.logger.debug('Running Token Validation with ' + str(api_metadata) + ' with ' + str(trials) + ' trials ')
        if trials > 5:
            self.logger.error('Consecutive failure in generating a valid token! Process Abort')
            return False
        if api_metadata['name'] == 'authenticate':
            return True
        response = self.request(self.tokenValidation,{},urlencoded=True,bypass_check=True)
        self.logger.info('Valid Token Check return status code ' + str(response['status']))
        if response['status'] != 200:
            self.logger.info('Found invalid token! Regenerating One')
            self.set_valid_token()
            result = self.is_valid_token(api_metadata,trials = trials+ 1)
        else:
            result=True
        return result

    def set_valid_token(self):
        self.logger.debug('Running Authentication')
        scope = {'scope':'openid'}
        response = self.request(self.authenticate, {**scope, **self.bcUserInfo},urlencoded=True,bypass_check=True)
        self.logger.info('Authentication Request returned status code of ' + str(response['status']))
        if response['status'] == 200:
            self.bearerToken = response['body']
            self.bearerHeader = {'Authorization': 'Bearer ' + self.bearerToken['access_token']}
            self.logger.info('Successfully Authenticated! Bearer header is ' + str(self.bearerHeader))
        else:
            self.logger.error('Failed Authentication! Pleaese ensure correct configuraiton is passed !')

    def autoCatalog():
        name='autoCatalog'
        endpoint = r'https://gtja.bankingcloud.moodysanalytics.com/api/cr/nonprod/dev/v2/catalog/files'
        requiredParams = ['data_source','files']
        return {'http_type':'POST','name' : 'autoCatalog','endpoint' : endpoint ,
                'requiredParams' : requiredParams
                }

    def startProject():
        name = 'startProject'
        endpoint= r'https://gtja.bankingcloud.moodysanalytics.com/api/cr/nonprod/dev/v2/project/execution'
        requiredParams =['project_name','closing_date','company','project_scope','collection_name']
        return {'http_type': 'POST','name': name, 'endpoint' : endpoint ,
                'requiredParams' : requiredParams
                }
    
    
    def getProjectStatus():
        name = 'getProjectStatus'
        endpoint= r'https://gtja.bankingcloud.moodysanalytics.com/api/cr/nonprod/dev/v2/project/execution'
        requiredParams = ['project']
        return {'http_type': 'GET','name': name, 'endpoint' : endpoint ,
                'requiredParams' : requiredParams
                }


    def generateZip():
        name = 'generateZip'
        endpoint= r'https://gtja.bankingcloud.moodysanalytics.com/api/cr/nonprod/dev/v2/project/generate-reports-zip'
        requiredParams = ['project_name','company','closing_date','parameters']
        return {'http_type': 'PUT','name': name, 'endpoint' : endpoint ,
                'requiredParams' : requiredParams
              }

    def zipToS3():
        name = 'zipToS3'
        endpoint= r'https://gtja.bankingcloud.moodysanalytics.com/api/cr/nonprod/dev/v1/aws/reports-zip'
        requiredParams = ['project_id']
        return {'http_type': 'POST','name': name, 'endpoint' : endpoint ,
                'requiredParams' : requiredParams
              }

    
                   
        
        

        
        
