"""
main api handler to process various api request
"""
from gmsdk.services import AuthenticateAPIService
from gmsdk.products import ProductAPIService
from gmsdk.orders import OrderAPIService
from gmsdk.suppliers import SupplierAPIService
from gmsdk.items import ItemAPIService
from gmsdk.log import LogAPIService
from gmsdk.agn import AGNAPIService


class GMSDK(object):
    """
    Main GMSDK app handlers that handles api
    like Order, Product
    Usage:
        >>gmsdk = GMSDK(**params)
        # to list all orders
        >>gmsdk.order.list(params)
        # to create order
        >>gmsdk.order.create(params)
    """
    __order_api = OrderAPIService
    __product_api = ProductAPIService
    __authenticate_api = AuthenticateAPIService
    __supplier_api = SupplierAPIService
    __item_api = ItemAPIService
    __agn_api = AGNAPIService
    __log_api = LogAPIService

    def __init__(self, **kwargs):
        self.params = kwargs
        self.custom_headers = kwargs.pop(
            "headers", {"content-type": "application/x-www-form-urlencoded"})

    @property
    def authenticate(self):
        """
        instance of authenticate api
        """
        if GMSDK.__authenticate_api:
            return GMSDK.__authenticate_api(
                headers=self.custom_headers, **self.params)

    @property
    def orders(self):
        """
        instance of order api
        """
        if GMSDK.__order_api:
            return GMSDK.__order_api(
                headers=self.custom_headers, **self.params)

    @property
    def catalogue(self):
        """
        instance of product api
        """
        if GMSDK.__product_api:
            return GMSDK.__product_api(
                headers=self.custom_headers, **self.params)

    @property
    def merchants(self):
        """
        instance of supplier api
        """
        if GMSDK.__supplier_api:
            return GMSDK.__supplier_api(
                headers=self.custom_headers, **self.params)

    @property
    def procurements(self):
        """
        instance of agn api
        """
        if GMSDK.__agn_api:
            return GMSDK.__agn_api(
                headers=self.custom_headers, **self.params)

    @property
    def inventory(self):
        """
        instance of item api
        """
        if GMSDK.__item_api:
            return GMSDK.__item_api(
                headers=self.custom_headers, **self.params)

    @property
    def request(self):
        """
        instance of request logs api
        """
        if GMSDK.__log_api:
            return GMSDK.__log_api(
                headers=self.custom_headers, **self.params)
