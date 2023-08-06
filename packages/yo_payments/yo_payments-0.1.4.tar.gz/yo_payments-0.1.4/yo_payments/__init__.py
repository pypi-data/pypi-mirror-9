#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Yo Payments API Wrapper
"""
import requests

import xmltodict
ACDEPOSITFUNDS = "acdepositfunds"
NON_BLOCKING = "NonBlocking"
PROVIDER_REFERENCE_TEXT = "ProviderReferenceText"
EXTERNAL_REFERENCE = "ExternalReference"
INTERNAL_REFERENCE = "InternalReference"
NARRATIVE = "Narrative"
ACCOUNT = "Account"
AMOUNT = "Amount"
ERROR_MESSAGE_CODE = "ErrorMessageCode"
ERROR_MESSAGE = "ErrorMessage"
STATUS_MESSAGE = "StatusMessage"
STATUS_CODE = "StatusCode"
AUTO_CREATE = "AutoCreate"
RESPONSE = "Response"
OK = "OK"
STATUS = "Status"

__title__ = "Yo Payments"
__author__ = 'James Muranga'
__email__ = 'jmured@gmail.com'
__version__ = '0.1.4'


class YoResponse(object):
    def __init__(self, data):
        self.data = data
        self.status = data[AUTO_CREATE][RESPONSE][STATUS]
        self.code = data[AUTO_CREATE][RESPONSE][STATUS_CODE]
        try:
            self.message = data[AUTO_CREATE][RESPONSE][STATUS_MESSAGE]
            self.error_message = data[AUTO_CREATE][RESPONSE][ERROR_MESSAGE]
            self.error_message_code = \
                data[AUTO_CREATE][RESPONSE][ERROR_MESSAGE_CODE]
        except KeyError:
            self.message = None
            self.error_message = None
            self.error_message_code = None

    def is_ok(self):
        return self.status == OK


class YoClient(object):
    """
    Wrapper on top of the requrests client to access the Yo Payments api.
    """
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url

    def parse_xml_response_to_dict(self, response):
        return xmltodict.parse(response.text)

    def make_request(self, method, **kwargs):
        response = requests.post(self.url,
                                 data=self.get_xml_data(method, kwargs),
                                 headers=self.get_headers(),
                                 verify=False)
        return YoResponse(self.parse_xml_response_to_dict(response))

    def get_headers(self):
        return {'Content-Type': 'text/xml',
                'Content-transfer-encoding:': 'text'}

    def get_xml_data(self, method, extra_data):
        data = """<?xml version="1.0" encoding="UTF-8"?>
<AutoCreate>
<Request>
 <APIUsername>{username}</APIUsername>
 <APIPassword>{password}</APIPassword>
 <Method>{method}</Method>
 {extra_xml}
 </Request>
</AutoCreate>
""".format(username=self.username, password=self.password, method=method,
           extra_xml=self.extra_xml(extra_data))
        return data

    def extra_xml(self, data):
        output = ""
        for key in data:
            output += "<{key}>{value}</{key}>".format(key=key, value=data[key])
        return output


class Yo(object):
    def __init__(self, username, password,
                 url="https://paymentsapi1.yo.co.ug/ybs/task.php"):
        self.client = YoClient(username, password, url)

    def _valid_account(self, account):
        if account.startswith("+"):
            raise Exception("Account should not start with +")

    def _get_non_blocking_text(self, non_blocking):
        non_blocking_text = "TRUE" if non_blocking else "FALSE"
        return non_blocking_text

    def withdraw_funds(self, amount, account,
                       narrative, internal_reference=None,
                       external_reference=None,
                       provider_reference_text=None,
                       non_blocking=False):
        self._valid_account(account)
        non_blocking_text = self._get_non_blocking_text(non_blocking)
        extra_data = {AMOUNT: amount, ACCOUNT: account,
                      NARRATIVE: narrative, NON_BLOCKING: non_blocking_text}
        if internal_reference is not None:
            extra_data[INTERNAL_REFERENCE] = internal_reference
        if external_reference is not None:
            extra_data[EXTERNAL_REFERENCE] = external_reference
        if provider_reference_text is not None:
            extra_data[PROVIDER_REFERENCE_TEXT] = provider_reference_text
        return self.client.make_request(ACDEPOSITFUNDS, **extra_data)
