# -*- coding: utf-8 -*-
import json
from gmsdk.connection import BaseConnection
from gmsdk.app_settings import API_VERSION as VERSION


class ItemAPIService(BaseConnection):
    """
    Item service to serve various api endpoints
    """
    def __init__(self, **kwargs):
        self.config.resp_format = 'json'
        super(ItemAPIService, self).__init__(**kwargs)
        self.config["headers"] = kwargs.pop("headers", {})

    def inventory_count(
            self, product_number='',
            client_store='', fc='', version=VERSION):
        """
        Description:
        Makes a request and hits the Inventory Count API endpoint
        depending upon the version selected.

        Args:
        product_number: the unique product number / id to identify the SKU.
        (Mandatory for version 2013.07)
        client_store: Client store name for order need to be created.
        fc: name of fulfillment center. (Mandatory)
        version: current version of API. (Mandatory)
        """
        self.method = 'GET'
        if version == '2013.07':
            self.config.uri = (
                '/ims/api/count/{product_number}/'.format(
                    product_number=product_number))
        elif version == '2013.10':
                self.config.uri = '/ims/api/count/'
        self.query_params = {
            'client_store': client_store, 'fc': fc, 'version': version}
        response = self.execute()
        return response

    def global_inventory_listing(
            self, prod_num='', stock='', stock_by_fc='',
            fields='', status='', page='', fc='', version='2014.02'):
        """
        Description:
        Makes a request and hits the Global Inventory Listing API endpoint
        depending upon the version selected.

        Args:
        prod_num: Product number(s) to search (optional)
        version: Current version of API, 2014.02. (mandatory)
        fc: Name of fulfillment center.  (optional)
        fields: Field(s) to include in the result(optional),
            Default fields are serials,
                client name, fc name
        status: Status(s) of the items(optional)
        page: Page number (optional)
        stock_by_fc: true/false. Returns available,
            hand and held inventory count
            for all PIDs aggregated by FCs and PIDs as well.
        stock: Returns available, hand and held
            inventory count for all PIDs passed in query params
        """
        self.method = 'GET'
        self.config.uri = '/ims/api/global/list/'
        self.query_params = {
            'prod_num': prod_num,
            'fc': fc,
            'version': version}
        if version == '2014.02':
            self.query_params.update(**{
                'fields': fields, 'status': status, 'page': page})
        elif version == '2014.03':
            self.query_params.update(**{
                'stock_by_fc': stock_by_fc, 'stock': stock})
        response = self.execute()
        return response
