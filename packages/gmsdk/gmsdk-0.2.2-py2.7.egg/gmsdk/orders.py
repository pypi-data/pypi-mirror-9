# -*- coding: utf-8 -*-

import json

from gmsdk.connection import BaseConnection
from gmsdk.app_settings import API_VERSION as VERSION
from gmsdk.exceptions import InvalidVersionError, InvalidStatusError
from gmsdk.exceptions import MissingDataError


class OrderAPIService(BaseConnection):
    """
    Order service to serve various api endpoints
    """

    AVAILABLE_VERSIONS = ['2013.07', '2014.09']

    def __init__(self, **kwargs):
        self.config.resp_format = 'json'
        super(OrderAPIService, self).__init__(**kwargs)
        self.config["headers"] = kwargs.pop("headers", {})

    def create(self, client_store, fc, data=None, version=VERSION):
        """
        Description:
        Makes a request and hits the Create Order API endpoint.

        Args:
        client_store: Client store name for order need to be created
        fc: name of fulfillment center from where order will be fulfilled.
        version: Version of the API being used
        data:
        [{
        'order_id': 2909,
        'order_date': '2013-06-24T12:30',
        'consignee': {
            'shipping_name': 'Neharika Vhatkar',
            'shipping_add1': '202,Harsha 2,7 bunglows,andheri(west)',
            'shipping_add2': '202,Harsha 2,7 bunglows,andheri(west)',
            'shipping_pin': '400061',
            'shipping_city': 'Mumbai',
            'shipping_state': 'Maharashtra',
            'shipping_country': 'India',
            'shipping_ph1': '9819339107',
            'shipping_ph2': '9717167997'
        },
        'OrderLine': {
            'order_line_id': 00001,
            'payment_mode': 'COD',
            'fulfillment_mode': 'BS',
            'supplier_id': '12983',
            'couriers': 'DELHIVERY',
            'waybill_number': '',
            'express_delivery': True,
            'Invoice': {
                'unit_price': 0.0,
                'unit_taxes': 0.0,
                'total_price': 520.0,
                'total_cst': 62.4,
                'total_vat': 12.5,
                'total_taxes': 123,
                'shipping_price': 70.0,
                'cod_amount': 456.0,
                'gross_value': 450.0,
                'discount': 0.0,
                'vat_percentage': 12.5,
                'cst_percentage': 12.5,
                'tax_percentage': 12.5,
                'net_amount': 450.0,
                'advance_payment': 0.0,
                'round_off': 0.0,
                'mrp': 450.0,
                'invoice_number': '2909/T1/INV/11',
                'invoice_date': '2013-06-24T12:30'
            },
            'Extra': {
                    'shipment_id': '',
            },
            'Products': [{
                'prod_num': 'FAB120',
                'prod_name': 'Orange pink dual clutch',
                'prod_sku': 'FAB120',
                'prod_desc': 'Coral bohemian dress - M',
                'prod_qty': 5,
                }]
            }
        },
        {
        'order_id': 2909,
        'order_date': '2013-05-27T12:30',
        'consignee': {
            'shipping_name': 'smriti arora',
            'shipping_add1': 'L28/7 DLF PHASE2 GURGAON HARYANA',
            'shipping_add2': 'L28/7 DLF PHASE2 GURGAON HARYANA',
            'shipping_pin': '122002',
            'shipping_city': 'Gurgaon',
            'shipping_state': 'Haryana',
            'shipping_country': 'India',
            'shipping_ph1': '9818442224',
        },
        'OrderLine': {
            'order_line_id': 00002,
            'payment_mode': 'COD',
            'fulfillment_mode': 'BS',
            'supplier_id': '12983',
            'couriers': 'ARAMEX',
            'waybill_number': 1201711,
            'express_delivery': True,
            'Invoice': {
                'unit_price': 0.0,
                'unit_taxes': 0.0,
                'total_price': 590.0,
                'total_cst': 70.8,
                'total_vat': 70.8,
                'total_taxes': 123.0,
                'shipping_price': 70.0,
                'cod_amount': 456.0,
                'gross_value': 520.0,
                'discount': 0.0,
                'vat_percentage': 12.5,
                'cst_percentage': 12.5,
                'tax_percentage': 12.5,
                'net_amount': 520.0,
                'advance_payment': 0.0,
                'round_off': 0.0,
                'mrp': 520.0,
                'invoice_number': '2116/T1/INV/345',
                'invoice_date': '2013-05-27T12:30'
            },
            'Extra': {
                    'shipment_id': '',
            },
            'Products': [{
                'prod_num': 'FAB120',
                'prod_name': 'Moustache lip mug pair - Glass / 6.5 inches',
                'prod_sku': 'FAB120',
                'prod_desc': 'Moustache lip mug pair - Glass / 6.5 inches',
                'prod_qty': 5,
                }]
            }
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
        self.query_params = {
            'client_store': client_store,
            'fc': fc,
            'version': version}

        if version == "2014.09":
            self.config["headers"].update(**{
                "content-type": "application/json"})
            self.query_params.update(**{
                "fulfillment_center": self.query_params.pop("fc")})
        else:
            data = {"data": data}

        self.method = 'POST'
        self.config.uri = '/oms/api/create/'
        response = self.execute(data=data)
        return response

    def update(self, client_store='', fc='', data=None, version=VERSION):
        """
        Description:
        Makes a request and hits the Update Order API endpoint.

        Args:
        client_store: Client store name for order need to be created
        fc: name of fulfillment center from where order will be fulfilled.
        version: Version of the API being used
        data: Refer Order create data.
        """
        self.method = 'PUT'
        self.config.uri = '/oms/api/update/DOU/'
        self.query_params = {
            'client_store': client_store,
            'fc': fc,
            'version': version,
        }
        data = json.dumps(data)
        data = {'data': data}
        response = self.execute(data=data)
        return response

    def cancel(
            self, client_store, fc, order_id,
            sub_order_id=[], version=VERSION):
        """
        Description:
        Makes a request and hits the Update/Cancel Order API endpoint.

        Args:
        client_store: Client store name for order need to be created
        fc: name of fulfillment center from where order will be fulfilled.
        order_id: Order Id which need to be canceled.
        sub_order_id: Comma separated sub order id's to mark them as cancelled
        version: Version of the API being used

        Example:
            >> from gmsdk import GMSDK
            >> sdk = GMSDK()
            >> resp = orders.cancel("Fabity", "FCDEL1", 36851735289, 2)
                # cancelling single sub-order
            >> resp.response_dict()
            >> {'info': {'order_id': 'T2345GFA',
                'sub_order_ids': [['1', 'CAN'], ['2', 'CAN']]},
                'message': 'Order T2345GFA has been cancelled',
                'status': 'Success'}
            >> resp = orders.cancel("Fabity", "FCDEL1", "T2345GFA", ["2", "1"])
                # multiple suborder cancellation

        """
        if not isinstance(sub_order_id, list):
            sub_order_id = [sub_order_id]
        sub_order_id = [str(e) for e in sub_order_id]
        sub_order_id = ",".join(sub_order_id)
        self.method = 'PUT'
        self.config.uri = '/oms/api/update/CAN/'
        self.query_params = {
            'client_store': client_store,
            'fc': fc,
            'version': version,
            'order_id': order_id,
            'sub_order_id': sub_order_id,
        }
        response = self.execute()
        return response

    def get_list(
            self, client_store, fc, status, order_id,
            order_line_id, after=None, before=None, version=VERSION):
        """
        Description:
        Makes a request and get the List Order API endpoint.

        Args:
        client_store: Client store name for order need to be created
        fc: name of fulfillment center from where order will be fulfilled.
        status: status, to be filtered out orders.
        [
         "readytoship", "pending", "fulfillable",
         "shipped", "returned", "canceled"]

        order_id: Order Id which need to be canceled.
        sub_order_id: if order_id provided, used to filter
        out based on sub order id
        after: <yyyy­mm­dd>, will filter out orders
        updated after given date
        before: <yyyy­mm­dd>, will filter out orders
        updated before given date
        version: Version of the API being used

        Example:
            >> from gmsdk import GMSDK
            >> sdk = GMSDK()
            >> resp = orders.get_list(
                    "Fabity", "FCDEL1", "canceled", "T2345GFA", "2")
            >> resp.response_dict()
            >> {
                'info': {'client_store': 'Fabity',
                'fulfillment_center': 'FCDEL1',
                'status': 'canceled'},
                'message': 'List of Orders',
                'orders': [{
                    'SubOrders': [{
                        'courier': None,
                        'length': None,
                        'order_line_id': '2',
                        'packed_at': None,
                        'picked_at': None,
                        'readytoshipped_at': None,
                        'shipped_at': None,
                        'status': 'canceled',
                        'updated_at': '2015-03-09T13:51:27Z',
                        'waybill': None,
                        'weight': None,
                        'width': None}],
                    'order_date': '2013-05-27T07:00:00Z',
                    'order_id': 'T2345GFA'}],
                    'status': 'Success'}
        """
        allowed_status = [
            "readytoship", "pending", "fulfillable",
            "shipped", "returned", "canceled"]

        if status not in allowed_status:
            raise InvalidStatusError(
                "Status - '%s' is not a valid status, "
                "Can not process request" % status)
        self.method = 'GET'
        self.config.uri = '/oms/api/list/'
        self.query_params = {
            'client_store': client_store,
            'fc': fc,
            'version': version,
            'order_id': order_id,
            'order_line_id': order_line_id,
            'status': status,
            'after': after,
            'before': before,
        }
        response = self.execute()
        return response

    def get_detail(
            self, client_store, fc, order_id,
            sub_order_id, version=VERSION):
        """
        Description:
        Makes a request and hits the Detail Order API endpoint.

        Args:
        client_store: Client store name for order need to be created
        fc: name of fulfillment center from where order will be fulfilled.
        order­id : Order Id, order details will be
            fetched against this id
        sub­order­id : Sub Order Id, which belongs
            to given particular order
        version: Version of the API being used

        Example:
            >> from gmsdk import GMSDK
            >> sdk = GMSDK()
            >> resp = orders.get_detail(
                    "Fabity", "FCDEL1", "T2345GFA", "2")
            >> resp.response_dict()
            >> {
                'OrderLine': {
                    'Products': [{
                        'prod_name': 'Moustache lip mug pair'
                                       ' - Glass 6.5 inches 7 - 14 Days',
                    'prod_num': 'FAB120',
                    'prod_qty': 5}],
                'can_combine_sub_orders': 'N',
                'client_store_sk': 'RS__16__10',
                'courier': None,
                'courier_last_scan_location': None,
                'courier_lsd': None,
                'courier_status': None,
                'created_at': '2015-03-08T18:42:25.052Z',
                'delivered_at': None,
                'delivered_by': None,
                'express_delivery': 'N',
                'fulfillment_mode': 'Buy and Sell',
                'is_editable_waybill': False,
                'order_line_id': '2',
                'packed_at': None,
                'payment_mode': 'COD',
                'po_details': {},
                'possible_couriers': 'ARAMEX',
                'product_mrp': '520.00',
                'returned_at': None,
                'returned_by': None,
                'shipped_at': None,
                'status': 'canceled',
                'total_cst': '70.80',
                'total_price': '590.00',
                'total_taxes': '123.00',
                'total_vat': '70.80',
                'waybill': 'None',
                'waybill_id': None},
                'client_store': 'Fabity',
                'consignee': {
                    'shipping_add1': 'L28/7 DLF PHASE2 GURGAON HARYANA',
                    'shipping_add2': 'L28/7 DLF PHASE2 GURGAON HARYANA',
                    'shipping_city': 'Gurgaon',
                    'shipping_country': 'India',
                    'shipping_name': 'smriti arora',
                    'shipping_ph1': '9818442224',
                    'shipping_ph2': None,
                    'shipping_pin': '122002',
                    'shipping_state': 'Haryana'},
                    'fulfillment_center': 'FCDEL1',
                    'order_date': '2013-05-27T07:00:00Z',
                    'order_id': 'T2345GFA',
                    'vendor_details': {'vendor_name': 'fabity'}}
        """
        self.method = 'GET'
        self.config.uri = "/oms/api/detail/{order_id}/{sub_order_id}".format(
            order_id=order_id, sub_order_id=sub_order_id)
        self.query_params = {
            'client_store': client_store,
            'fc': fc,
            'version': version,
        }
        response = self.execute()
        return response
