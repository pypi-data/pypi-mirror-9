__author__ = 'admin'
import os
from subprocess import call,Popen
import subprocess
from multiprocessing import Process
import multiprocessing
import re
import urllib2
import logging
import HttpMock
import MockRequest,MockResponse
from glob import glob
import json

from webmocker.mock_helper import pretender_defaults

LOGGER = logging.getLogger("webmocker")
not_supported_filters = ["doesNotMatch"]
pid = None
server_process = None

def start_pretend(port_number = pretender_defaults.portno):
    global server_process
    server_process = Process(name='pretend', args=(port_number,),target=pretend)
    server_process.start()

def pretend(port_number):
    global pid
    pid = Popen("python -m pretend_extended.server.server --host 127.0.0.1 --port "+ str(port_number), stdout=subprocess.PIPE, shell=True)

def stop_pretend():
    if(server_process != None):
        server_process.terminate()

def get_url_from_json(request_json):
    url = get_url(request_json)
    # handle query params
    if(request_json.has_key('queryParameters') == False): return url
    query_param = format_query_string(request_json['queryParameters'])
    query_param = '('+ query_param + '&?){'+ str(len(request_json['queryParameters'])) +'}'
    url = url + ('\?' if query_param!='' else '') + query_param
    return url

def get_body_from_json(request_json):
    body = request_json['body'] if request_json.has_key('body') else pretender_defaults.request_body
    if(request_json.has_key('bodyPatterns') == False):
        return body
    body = convert_list_to_dict(request_json['bodyPatterns'])
    body_str = ''
    if body.has_key('matches'):
        body_str = body_str + body['matches']
    if body.has_key('doesNotMatch'):
        body_str = body_str + 'PPP'+ body['doesNotMatch']
    return body_str

def get_headers_from_json(request_json):
    if(request_json.has_key('headers') == False):
        return {}
    headers = convert_json_to_dict(request_json['headers'])
    return headers

def convert_json_to_dict(json_element):
    # delete_keys(json_element,not_supported_filters)
    return { header : get_header_value(value) for header,value in json_element.items()}

def delete_keys(json_element,keys_to_delete):
     remove = [header for header,value in json_element.items() if isinstance(value, dict) and key_in_list(value,keys_to_delete)]
     for k in remove: del json_element[k]


def convert_list_to_dict(dict_element):
    # return [key_value_pair for key_value_pair in dict_element  if isinstance(key_value_pair, dict) and key_in_list(key_value_pair,["matches","doesNotMatch"])]
    return dict([(key,d[key]) for d in dict_element for key in d])


def key_in_list(value,keys_to_delete):
    result = False
    for key in keys_to_delete:
        result = result or value.has_key(key)
    return result

def get_header_value(value):
    if isinstance(value, dict):
        if(value.has_key('equalTo')): return re.escape(value['equalTo'])
        elif(value.has_key('matches')): return '.*?'+ value['matches'] +'.*'
        elif(value.has_key('contains')): return '.*?'+value['contains']+'.*'
        elif(value.has_key('doesNotMatch')): return 'PPP.*?'+value['doesNotMatch'] +'.*'
    return value

def format_query_string(query_params):
    query_param = ''
    for param,value in query_params.items():
        query_param = query_param + ('&?|' if query_param!='' else '') + get_param_value(param,value)
    return query_param

def get_param_value(param,value):
     if isinstance(value, dict):
        if(value.has_key('contains')):
           return  param +'=.*?'+ re.escape(urllib2.quote(value['contains'])).replace('\%','%')+'.*?'
        elif(value.has_key('equalto')):
            return param +'='+  re.escape(urllib2.quote(value['equalto'])).replace('\%','%')
        elif(value.has_key('matches')):
            return param +'='+  value['matches'].replace(' ','%20')
     else:
        return param +'='+ value.replace(' ','%20')

def get_response_headers_from_json(response_json):
    response_headers = {}
    if(response_json.has_key('headers') == False):
        return response_headers
    for header,value in response_json['headers'].items():
       response_headers[header] = value
    return response_headers

def process_stubs(stubs):
    mock = HttpMock.Mock(pretender_defaults.portno,pretender_defaults.stub_name)       # create a HTTPMock Object
    for stub in stubs:                             # iterate for each stub in the json
        request = MockRequest.Request()
        response = MockResponse.Response()
        if (stub.has_key('request')):
            request.set_request_entities(stub['request'])
        if (stub.has_key('response')):
            response.set_response_entities(stub['response'])
        mock.mock_request(request,response)

def process_stub_files(stub_files_path):
    for stub_file in glob(stub_files_path+'*.json'):   # iterate for each json file
        stubs = json.load(open(stub_file))
        LOGGER.debug(stub_file)
        process_stubs(stubs)


def get_url(request_json):
    url = request_json['url'].replace('?','\?')+'$' if request_json.has_key('url') else pretender_defaults.url
    url = request_json['urlPattern'].replace('?','\?') if request_json.has_key('urlPattern') else url
    return request_json['urlPath'].replace('?','\?')+'(/.*)?' if request_json.has_key('urlPath') else url

def get_response_body_from_json(response_body):
    if(os.path.exists(response_body)):
        file = open(response_body, 'r')
        file_content = file.read()
        return file_content
    else:
        return response_body
