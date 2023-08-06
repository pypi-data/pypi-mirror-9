from pretend_extended.client.http import HTTPMock


class Mock:

  mock=None

  def __init__(self, port_number, stub_name):
    self.mock = HTTPMock('127.0.0.1',port_number, name=stub_name)
    self.mock.reset()
    self.mock.when('GET /thing*').reply('Hello',status=202,times=20)                  # sample web request stub

  def mock_request(self,method,url,headers,body,response_body,response_headers,response_status):
    self.mock.when(method+' '+url, headers=headers ,body=body).reply(response_body,headers=response_headers,status=response_status,times=20)

  def mock_request(self,request,response):
    self.mock.when(request.method+' '+request.url, headers=request.headers ,body = request.body).reply(response.response_body,headers=response.response_headers,status=response.response_status,times=20)


