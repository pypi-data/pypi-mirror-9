#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 15.12.2014

'''
from eWRT.ws.rest import MultiRESTClient
from weblyzard_api.client import WEBLYZARD_API_URL, WEBLYZARD_API_USER, WEBLYZARD_API_PASS

SERVER_URL_PATH = '/rest/polarity/document'

class OpinionClient(MultiRESTClient):
    
    URL_PATH = '/'.join(SERVER_URL_PATH.split('/')[:-1])

    def __init__(self, url=WEBLYZARD_API_URL, 
                 usr=WEBLYZARD_API_USER, pwd=WEBLYZARD_API_PASS):
        MultiRESTClient.__init__(self, service_urls=url, user=usr, password=pwd)

    def get_polarity(self, content, content_format):
        '''
        Sends the content in the content_format to the opinion mining server
        to calculate the polarity/sentiment of the content.

        :param content str: The string containing the document to analyze.
        :param content_format str: The format of the content. Must be 'xml' or
            'plaintext'
        :returns: The content (modified, if xml) and the content's overall
            polarity in a dict with content and polarity as keys. If an error
            ocurred, it is also contained in the dict with the 'error' key.
        :rtype: dict
        '''
        return self.request('document', 
                            parameters={'format': content_format,
                                        'content': content},
                            return_plain=False)

    def status(self):
        return self.request('config')
