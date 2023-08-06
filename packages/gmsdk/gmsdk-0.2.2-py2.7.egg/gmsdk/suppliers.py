# -*- coding: utf-8 -*-

import json
from gmsdk.connection import BaseConnection
from gmsdk.app_settings import API_VERSION as VERSION
from gmsdk.exceptions import InvalidVersionError, InvalidStatusError
from gmsdk.exceptions import MissingDataError


class SupplierAPIService(BaseConnection):
    """
    Supplier service to serve various api endpoints
    """

    AVAILABLE_VERSIONS = ['2013.07', '2014.09']

    def __init__(self, **kwargs):
        self.config.resp_format = 'json'
        super(SupplierAPIService, self).__init__(**kwargs)
        self.config["headers"] = kwargs.pop("headers", {})

    def create(self, client_store, data=None, version=VERSION):
        """
        Description:
        Makes a request and hits the Create Supplier API endpoint.

        Args:
        client_store:­ Client store name
        fc: Name of the fulfillment center, which will fulfill thsi order
        version: Version of the API being used
        data:
        [{
        "merchantName": "Test Suppler",
        "merchantId": "T12345",
        "active": "True",
        "Info":{
                "add1": "add1 test supplier",
                "add2": "add2 test supplier",
                "city": "New Delhi",
                "state": "New Delhi",
                "country": "India",
                "pin": "122001",
                "phone1": "8527167997",
                "phone2": "",
                "phone3":"",
                "email": "hari.kishan81001@gmail.com",
        },
        "SupplierStore": {
                "facility_id": "T13563653",
                "facility_name": "Test Supplier Store1",
                "fulfillment_mode": "BS",
        },
        }]
        """
        if version not in self.AVAILABLE_VERSIONS:
            raise InvalidVersionError(
                "Version-%s is not supported by"
                " Delhivery-Godam API's" % version)
        if not data:
            raise MissingDataError(
                "No input found provided for creating"
                " orders ! Request can not proceed !")
        data = json.dumps(data)

        if version == "2014.09":
            self.config["headers"].update(**{
                "content-type": "application/json"})
        else:
            data = {"data": data}

        self.method = 'POST'
        self.config.uri = '/management/api/create/'
        self.query_params = {
            'client_store': client_store, 'version': version}
        response = self.execute(data=data)
        return response

    def update(self, client_store, data=None, version=VERSION):
        """
        Description:
        Makes a request and hits the Create/Update Supplier API endpoint.

        Args:
        client_store:­ Client store name
        fc:­ Name of the fulfillment center
        version: Version of the API being used
        data:
        [{
        "merchantName": "Test Suppler",
        "merchantId": "T12345",
        "active": "True",
        "Info":{
                "add1": "add1 test supplier",
                "add2": "add2 test supplier",
                "city": "New Delhi",
                "state": "New Delhi",
                "country": "India",
                "pin": "122001",
                "phone1": "8527167997",
                "phone2": "",
                "phone3":"",
                "email": "hari.kishan81001@gmail.com",
        },
        "SupplierStore": {
                "facility_id": "T13563653",
                "facility_name": "Test Supplier Store1",
                "fulfillment_mode": "BS",
            },
        }]
        """
        return self.create(client_store, data, version=version)
