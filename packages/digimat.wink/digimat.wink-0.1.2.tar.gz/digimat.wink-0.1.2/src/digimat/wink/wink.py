import requests
import json
import time

from pprint import pprint
import sys, traceback

# Wink API
# http://docs.wink.apiary.io/#arestfulservice
# http://branch.com/b/wink-api

WINK_API_URL = 'https://winkapi.quirky.com'
WINK_API_CLIENT_ID = 'quirky_wink_android_app'
WINK_API_CLIENT_SECRET = 'e749124ad386a5a35c0ab554a4f2c045'
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
        self._session=requests.Session()

    def setAccessToken(self, accessToken, refreshToken=None):
        if accessToken:
            self._accessToken=accessToken
            self._refreshToken=refreshToken
            self._stampAccessTokenExpiration=time.time()+WINK_API_TOKEN_EXPIRATION

    def service(self, path):
        url='%s%s' % (self._apiURL, path)
        # print url
        return url

    def requestHeaders(self, useToken=True):
        headers = {'Content-Type': 'application/json',
            # 'X-API-VERSION' : '1.0',
            # 'X-CLIENT-VERSION': 'IOS-8.2',
            # 'Accept-Encoding' : 'gzip, deflate',
            # 'User-Agent': 'Manufacturer/Apple-iPhone6_2 iOS/8.2 WinkiOS/2.8.0.11-production-release (Scale/2.00)'
        }
        if useToken and self._accessToken:
            headers['Authorization']='Bearer %s' % self._accessToken
        return headers

    def requestAuthPOST(self, service, data=None):
        print "OK"
        try:
            print "AUTH"
            r=self._session.post(self.service(service),
                headers=self.requestHeaders(False),
                data=json.dumps(data),
                timeout=self._apiTimeout,
                verify=True)
            print r
            if r and r.status_code in [200, 201, 202]:
                print r.content
                response=r.json()
                data=response['data']
                #pprint(data)
                return data
        except:
            print "EXC"
            traceback.print_exc(file=sys.stdout)
            pass

    def requestPOST(self, service, data=None):
        if self.authenticate():
            try:
                r=self._session.post(self.service(service),
                    headers=self.requestHeaders(not isAuthRequest),
                    data=json.dumps(data),
                    timeout=self._apiTimeout,
                    verify=True)
                if r and r.status_code in [200, 201, 202]:
                    response=r.json()
                    data=response['data']
                    #pprint(data)
                    return data
            except:
                traceback.print_exc(file=sys.stdout)
                pass

    def requestPUT(self, service, data=None):
        if self.authenticate():
            try:
                r=self._session.put(self.service(service),
                    headers=self.requestHeaders(),
                    data=json.dumps(data),
                    timeout=self._apiTimeout,
                    verify=True)
                if r and r.status_code==200:
                    response=r.json()
                    data=response['data']
                    # pprint(data)
                    return data
            except:
                traceback.print_exc(file=sys.stdout)
                pass

    def requestGET(self, service):
        if self.authenticate():
            try:
                r=self._session.get(self.service(service),
                    headers=self.requestHeaders(),
                    timeout=self._apiTimeout,
                    verify=True)
                if r and r.status_code==200:
                    response=r.json()
                    data=response['data']
                    #pprint(data)
                    return data
            except:
                traceback.print_exc(file=sys.stdout)
                pass

    def login(self):
        self._accessToken=None
        self._refreshToken=None
        payload={'grant_type':'password',
            'client_id':self._apiClientId,
            'client_secret':self._apiClientSecret,
            'username':self._username,
            'password':self._password}

        print payload

        response=self.requestAuthPOST('/oauth2/token', payload)
        try:
            self.setAccessToken(response['access_token'], response['refresh_token'])
            return True
        except:
            pass

    def authenticate(self, force=False):
        if self._accessToken:
            if not force and time.time()<self._stampAccessTokenExpiration:
                return True
            if self._refreshToken:
                payload={'grant_type':'refresh_token',
                    'refresh_token':self._refreshToken}
                response=self.requestPOST('/oauth2/token', payload)
                try:
                    self.setAccessToken(response['access_token'], response['refresh_token'])
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
