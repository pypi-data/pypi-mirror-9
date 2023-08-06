__author__ = 'admin'

import json
import os
from glob import glob
import logging

import webmocker.mock_helper.pretender_defaults
import webmocker.mock_helper.pretend_helpers
from webmocker.mock_helper import HttpMock, pretender_defaults,MockRequest,MockResponse, pretend_helpers


LOGGER = logging.getLogger("webmocker")

def start(port_number = pretender_defaults.portno,stub_name = pretender_defaults.stub_name):
    pretender_defaults.portno = port_number
    pretender_defaults.stub_name = stub_name
    restart_pretend(port_number)                      # Stopping and Starting the pretend_extended
    stub_files_path = get_stub_files_path()
    pretend_helpers.process_stub_files(stub_files_path)

def stop():
    pretend_helpers.stop_pretend()

def restart_pretend(port_number):
    pretend_helpers.stop_pretend()
    pretend_helpers.start_pretend(port_number)

def get_stub_files_path():
    return pretender_defaults.stub_files_path if os.environ.has_key("stub_files_path")==False else  os.environ["stub_files_path"]