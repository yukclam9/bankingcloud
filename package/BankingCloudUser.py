import requests

class BankingCloudUser:

    def __init__(self,userInfo):
        self._client_id=userInfo['client_id']
        self._username=userInfo['username']
        self._password=userInfo['password']
        self._secret=userInfo['secret']
        self._grantType=userInfo['grantType']
        
    def getUserInfo(self):
        userInfo= { 'username': self._username, \
                 'password': self._password, \
                 'client_id': self._client_id, \
                 'client_secret': self._secret, \
                 'grant_type': self._grantType }
        #print(userInfo)
        return userInfo
