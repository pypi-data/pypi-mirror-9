import requests
import json
import time

from pprint import pprint

# Wink API
# http://docs.wink.apiary.io/#arestfulservice

WINK_API_URL = 'https://winkapi.quirky.com'
WINK_API_CLIENT_ID = 'quirky_wink_ios_app'
WINK_API_CLIENT_SECRET = 'ce609edf5e85015d393e7859a38056fe'
WINK_API_TOKEN_EXPIRATION = 900

class Wink(object):
    def __init__(self, username, password, timeout=15.0):
        self._apiURL=WINK_API_URL
        self._apiClientId=WINK_API_CLIENT_ID
        self._apiClientSecret=WINK_API_CLIENT_SECRET
        self._apiTimeout=timeout
        self._username=username
        self._password=password
        self._accessToken=None
        self._refreshToken=None
        self._stampAccessTokenExpiration=0

    def service(self, path):
        url='%s%s' % (self._apiURL, path)
        # print url
        return url

    def requestHeaders(self, useToken=True):
        headers = {'Content-Type': 'application/json'}
        if useToken and self._accessToken:
            headers['Authorization']='Bearer %s' % self._accessToken
        return headers

    def requestAuthPOST(self, service, data=None):
        try:
            r=requests.post(self.service(service),
                headers=self.requestHeaders(False),
                data=json.dumps(data),
                timeout=self._apiTimeout)
            if r and r.status_code in [200, 201, 202]:
                response=r.json()
                data=response['data']
                #pprint(data)
                return data
        except:
            pass

    def requestPOST(self, service, data=None):
        if self.authenticate():
            try:
                r=requests.post(self.service(service),
                    headers=self.requestHeaders(not isAuthRequest),
                    data=json.dumps(data),
                    timeout=self._apiTimeout)
                if r and r.status_code in [200, 201, 202]:
                    response=r.json()
                    data=response['data']
                    #pprint(data)
                    return data
            except:
                pass

    def requestPUT(self, service, data=None):
        if self.authenticate():
            try:
                r=requests.put(self.service(service),
                    headers=self.requestHeaders(),
                    data=json.dumps(data),
                    timeout=self._apiTimeout)
                if r and r.status_code==200:
                    response=r.json()
                    data=response['data']
                    #pprint(data)
                    return data
            except:
                pass

    def requestGET(self, service):
        if self.authenticate():
            try:
                r=requests.get(self.service(service),
                    headers=self.requestHeaders(),
                    timeout=self._apiTimeout)
                if r and r.status_code==200:
                    response=r.json()
                    data=response['data']
                    #pprint(data)
                    return data
            except:
                pass

    def login(self):
        self._accessToken=None
        self._refreshToken=None
        payload={'grant_type':'password',
            'client_id':self._apiClientId,
            'client_secret':self._apiClientSecret,
            'username':self._username,
            'password':self._password}

        response=self.requestAuthPOST('/oauth2/token', payload)
        try:
            self._accessToken=response['access_token']
            self._refreshToken=response['refresh_token']
            self._stampAccessTokenExpiration=time.time()+WINK_API_TOKEN_EXPIRATION
            return True
        except:
            pass

    def authenticate(self, force=False):
        if self._refreshToken:
            if not force and time.time()<self._stampAccessTokenExpiration:
                return True
            payload={'grant_type':'refresh_token',
                'refresh_token':self._refreshToken}
            response=self.requestPOST('/oauth2/token', payload)
            try:
                self._accessToken=response['access_token']
                self._refreshToken=response['refresh_token']
                self._stampAccessTokenExpiration=time.time()+WINK_API_TOKEN_EXPIRATION
                return True
            except:
                pass
        return self.login()

    def getDevices(self):
        response=self.requestGET('/users/me/wink_devices')
        for device in response:
            #todo:
            print device['upc_id']


if __name__ == "__main__":
    pass
