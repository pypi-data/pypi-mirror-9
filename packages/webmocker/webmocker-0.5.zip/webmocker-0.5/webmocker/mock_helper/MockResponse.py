__author__ = 'admin'
import pretender_defaults
import pretend_helpers

class Response:

  def __init__(self):
    self.response_headers = {}
    self.response_body =  pretender_defaults.response_body
    self.response_status = pretender_defaults.response_status

  def set_response_entities(self,response_json):
    self.response_body = pretend_helpers.get_response_body_from_json(response_json['body']) if response_json.has_key('body') else pretender_defaults.response_body                   # get the response body from the json
    self.response_status =response_json['status'] if response_json.has_key('status') else pretender_defaults.response_status           # get the response status from the json
    self.response_headers =  pretend_helpers.get_response_headers_from_json(response_json)                                          # get the response headers from the json
