import json

from gmsdk.connection import BaseConnection
from gmsdk.app_settings import API_VERSION as VERSION
from gmsdk.exceptions import InvalidVersionError, InvalidStatusError
from gmsdk.exceptions import MissingDataError


class ProductAPIService(BaseConnection):
    """
    Product service to serve various api endpoints
    """
    AVAILABLE_VERSIONS = ['2013.07', '2014.09']

    def __init__(self, **kwargs):
        self.config.resp_format = 'json'
        super(ProductAPIService, self).__init__(**kwargs)
        self.config["headers"] = kwargs.pop("headers", {})

    def create(self, client_store, data=None, version=VERSION):
        """
        Description:
        Makes a request and hits the Create Product API endpoint.

        Args:
        client_store: Client store name for product need to be created
        fc: name of fulfillment center from where order will be fulfilled.
        version: Version of the API being used
        Example:
            >> data=
            [{
            "product_number": "FABP1",
            "sku": "FABP1",
            "name": "Test Product",
            "supplier_sku": "FTY_P01",
            "supplier_id": "FTY_S01",
            "length": 12,
            "width": 15,
            "height": 12,
            "weight": 0.3,
            "Extra": {
                  "category": "Music",
                  "catalogue": "Music",
                  "offer": "Buy One Get One",
                  "description": "Testing New Product",
                  "reject_duration": "1w",
                  "mrp_required": true,
                  "expiry_date_required": true,
                  "imei_required": true,
                  "url": "http://google.com/p1/prod123.png"
                }
            }]
            >> from gmsdk import GMSDK
            >> sdk = GMSDK()
            >> resp = sdk.catalogue.create("Fabity", data)
            >> resp.response_dict()
              {u'Message': u'Your request has been queued',
              'Request Id': 526327}
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
        self.config.uri = '/pcm/api/create/'
        self.query_params = {
            'client_store': client_store, 'version': version}
        response = self.execute(data=data)
        return response

    def update(self, client_store, fc, data=None, version=VERSION):
        """
        Description:
        Makes a request and hits the Create/Update Product API endpoint.

        Args:
        client_store: Client store name for product need to be updated
        fc: name of fulfillment center from where order will be fulfilled.
        version: Version of the API being used
        Example:
            >> data
                [{
                    'product_number': '1A23',
                    'sku': '32794',
                    'name': 'American Pine Wood (New Product)',
                    'supplier_sku': '599phfb',
                    'supplier_number': '13805',
                    'Extra': {
                    'category': 'Muzic',
                    'catalogue': 'Oldies',
                    'offer': 'Buy1Get1Free',
                    'description': 'Collection of 1950 muzic',
                    }
                },]
            >> from gmsdk import GMSDK
            >> sdk = GMSDK()
            >> resp = sdk.catalogue.update("Fabity", data)
            >> resp.response_dict()
              {'Message': 'Your request has been queued',
              'Request Id': 526327}
        """
        return self.create(self, client_store, data, version)

    def deactivate(
            self, product_number, client_store, version=VERSION):
        """
        Description:
            API endpoint to deactivate catalogue
        Args:
            product_number: product number that will be
              used to mark the product inactive.
            client_store: Client store name for product need to be cancelled.
            version: Version of the API being used
        Example:
            >> from gmsdk import GMSDK
            >> sdk = GMSDK()
            >> resp = sdk.catalogue.deactivate("P23456789", "Fabity")
            >> resp.response_dict()
               {'message': (
                    'Product number P23456789 has been marked inactive'),
                'product details': {
                    'active': False,
                    'product description': 'Collection of 1990 muzic',
                    'product number': 'P23456789'},
                'status': 'Success'}
        """
        self.method = 'PUT'
        self.config.uri = "/pcm/api/cancel/{product_number}/".format(
            product_number=product_number)
        self.query_params = {
            'client_store': client_store, 'version': version}
        response = self.execute()
        return response

    def list(self, product_numbers=[], client_sk=None, page=1):
        """
        Description:
        Makes a request and hits the List Product API endpoint.

        Args:
        product_number: product number that will
            be used to list the products mentioned.
        client_sk: SK of client ( conditional ).
        page: Page number in case of paginated results. default 1.

        Example:
            >> from gmsdk import GMSDK
            >> sdk = GMSDK()
            >> prods = ["FAB121", "P23456789"]
            >> resp = sdk.catalogue.list(product_numbers=prods)
            >> resp.response_dict()
               {
                "count": 2,
                "next": null,
                "previous": null,
                "results": [{
                    "url": null,
                    "sku": "32794",
                    "supplier_sku": "599phfb",
                    "supplier_store": null,
                    "name": "Product Testing Fabity",
                    "number": "P23456789",
                    "category": "Muzic",
                    "catalogue": "Oldies",
                    "description": "Collection of 1990 muzic",
                    "weight": null,
                    "weight_unit": "KG",
                    "length": null,
                    "width": null,
                    "height": null,
                    "dimensions_unit": "CM",
                    "active": false,
                    "created_at": "2015-03-11T08:16:55.726Z",
                    "updated_at": "2015-03-11T08:17:31.401Z",
                    "dv_catalogue": null,
                    "dv_catalogue_name": null
                }, {
                    "url": null,
                    "sku": "FAB121",
                    "supplier_sku": "FAB121",
                    "supplier_store": "WH__16__10__FTY_S01",
                    "name": "Golden Hair bow Band - Bow 4",
                    "number": "FAB121",
                    "category": null,
                    "catalogue": null,
                    "description": null,
                    "weight": null,
                    "weight_unit": "KG",
                    "length": null,
                    "width": null,
                    "height": null,
                    "dimensions_unit": "CM",
                    "active": true,
                    "created_at": "2013-07-17T09:21:59.516Z",
                    "updated_at": "2013-07-17T09:21:59.516Z",
                    "dv_catalogue": null,
                    "dv_catalogue_name": null
                }]
            }
        """

        prods = None
        if product_numbers:
            prods = ",".join(product_numbers)
        self.method = 'GET'
        self.config.uri = '/pcm/products/'
        self.query_params = {"page": page}
        if client_sk:
            self.query_params.update(**{
                'client_sk': client_sk})
        if prods:
            self.query_params.update(**{
                'products': prods})
        response = self.execute()
        return response

    def detail(self, product_number, client_sk=None):
        """
        Description:
        Makes a request and hits the Detail Product API endpoint.

        Args:
        product_number: product number that will
            be used to get the detail of the product
        client_sk: SK of client ( conditional ).
        Example:
            >> from gmsdk import GMSDK
            >> sdk = GMSDK()
            >> resp = sdk.catalogue.detail("P23456789")
            >> resp.response_dict()
            {
                "url": null,
                "sku": "32794",
                "supplier_sku": "599phfb",
                "supplier_store": null,
                "name": "Product Testing Fabity",
                "number": "P23456789",
                "category": "Muzic",
                "catalogue": "Oldies",
                "description": "Collection of 1990 muzic",
                "weight": null,
                "weight_unit": "KG",
                "length": null,
                "width": null,
                "height": null,
                "dimensions_unit": "CM",
                "active": false,
                "created_at": "2015-03-11T08:16:55.726Z",
                "updated_at": "2015-03-11T08:17:31.401Z",
                "dv_catalogue": null,
                "dv_catalogue_name": null
            }
        """
        self.method = 'GET'
        self.config.uri = "/pcm/products/{product_number}/".format(
            product_number=product_number)
        if client_sk:
            self.query_params = {'client_sk': client_sk}
        response = self.execute()
        return response
