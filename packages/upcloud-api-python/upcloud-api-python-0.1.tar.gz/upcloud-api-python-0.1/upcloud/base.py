import json
import requests


class BaseAPI(object):
	api = "api.upcloud.com"
	api_v = "1.1"

	def __init__(self, token):
		self.token = token

	"""
	Performs a request with a given body to a given endpoint in UpCloud's API. 
	Handles errors with __error_middleware.
	"""
	def request(self, method, endpoint, body=None):
		if(method not in {"GET", "POST", "PUT", "DELETE"}):
			raise Exception("Invalid/Forbidden HTTP method")

		url = "/" + self.api_v + endpoint
		headers = { 	
			"Authorization": self.token, 
			"Content-Type": "application/json"
		}

		if body: json_body_or_None = json.dumps(body)
		else: json_body_or_None = None

		APIcall = getattr(requests, method.lower())
		res = APIcall("https://api.upcloud.com" + url, data=json_body_or_None, headers=headers)

		if( res.text ):
			res_json = res.json()
		else: res_json = {}
		
		return self.__error_middleware(res, res_json)


	"""
	Performs a GET request to a given endpoint in UpCloud's API. 
	"""
	def get_request(self, endpoint):
		return self.request("GET", endpoint)		
		
	"""
	Performs a POST request to a given endpoint in UpCloud's API. 
	"""
	def post_request(self, endpoint, body=None):
		return self.request("POST", endpoint, body)		

	"""
	Middleware that raises an exception when HTTP statuscode is an error code.
	"""
	def __error_middleware(self, res, res_json):
		if(res.status_code in [400, 401, 402, 403, 404, 405, 406, 409]):
			raise Exception(res_json)

		return res_json

