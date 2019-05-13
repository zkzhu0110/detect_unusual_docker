#!/bin/env python
#encoding=utf-8
import requests

class Singleton(type):
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance

class PaiToken:
    #__metaclass__ = Singleton

    def __init__(self, userConfig, tokenServerUrl):
        self.userConfig = userConfig
        self.tokenServerUrl = tokenServerUrl
        self.__token = self.__updateToken(userConfig, tokenServerUrl)

    def __updateToken(self, userConfig, tokenServerUrl):
        print ('userConfig = {}'.format(userConfig))
        print ('tokenServerUrl = {}'.format(tokenServerUrl))
        result = requests.post(tokenServerUrl, userConfig).json()
        print ('result = {}'.format(result))
        print ('OK')
        return result['token']

    def updateToken(self):
        self.__token = self.__updateToken(self.userConfig, self.tokenServerUrl)

    def getToken(self):
        return self.__token

