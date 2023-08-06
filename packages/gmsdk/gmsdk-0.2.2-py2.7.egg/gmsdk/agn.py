# -*- coding: utf-8 -*-
import json
from gmsdk.connection import BaseConnection
from gmsdk.app_settings import API_VERSION as VERSION


class AGNAPIService(BaseConnection):
	"""
	AGN service to serve various api endpoints
	"""
	def __init__(self, **kwargs):
		self.config.resp_format = 'json'
		super(AGNAPIService, self).__init__(**kwargs)
		self.config["headers"] = kwargs.pop("headers", {})
	
	def create(self, client_store='', fc='', data=None, version='2014.02'):
		"""
		Description:
		Makes a request and hit the Create AGN API endpoint.

		Args:
		client_store: Client store name, for which the AGN needs to be created.
		fc:­ Name of the fulfillment center, where AGN will be processed 
		version: Version of the API being used (2014.02)
		data:
		[{
			'supplier_id': '13593',
			'source_number': 'src/12/562/test123',
			'auxilliary_vendor': 'Test Vendor',
			'prod_details': [{
		    		'prod_number': 'PROD1234',
		    		'qty': "5",
			}, {
		    		'prod_number': 'PROD1235',
		    		'qty': 23,
			}]
		}]
		"""
		self.method = 'POST'
		self.config.uri = '/po/api/create/'
		self.query_params = {'client_store': client_store, 'fc': fc, 'version': version}
		data = json.dumps(data)
		data = {"data": data}
		response = self.execute(data=data)
		return response


	def list(self, client_store='', fc='', status='',
			updated_at='', source_number='', version='2014.02'):
		"""
		Description:
		Makes a request and hit the Create AGN API endpoint.

		Args:
		client_store : Client store name where AGN has to be created.
		fc :  name of fulfillment center where AGN has to be created. 
		status: AGN’s in this status will be filtered.
		updated_at : date in format <yyyy­mm­dd>, AGN’s updated after given date will be
		filtered
		source_number : source number, will return the AGN against that source number
		version : Current version of API. Now available 2014.02
		"""
		self.method = 'GET'
		self.config.uri = "/po/api/list/"
		self.query_params = {
			'client_store': client_store,
			'fc': fc,
			'status': status,
			'updated_at': updated_at,
			'source_number': source_number,
		}
		response = self.execute()
		return response
