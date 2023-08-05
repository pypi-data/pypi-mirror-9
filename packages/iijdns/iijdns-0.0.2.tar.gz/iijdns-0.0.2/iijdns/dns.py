# coding: utf-8

API_VER = r'20140601'
BASE_URL = r'https://do.api.iij.jp'
DEFAULT_ALIAS = r'default'
ACCESS_KEY = 'ACCESS_KEY'
SECRET_KEY = 'SECRET_KEY'
SERVICE_CODE = 'SERVICE_CODE'
_secret = {}

def initialize(access_key, secret_key, service_code, alias=DEFAULT_ALIAS):
    '''
    Notes:
      store secrets with alias
    Args:
      access_key(string): IIJ access key
      secret_key(string): IIJ secret key
      service_code(string): IIJ service code
      alias(string): alias that is used to index of secrets
    '''
    import logging
    if alias in _secret:
        logging.warn('alias[%s] is already initialized' % alias)
    else:
        _secret[alias] = { 
            ACCESS_KEY: access_key,
            SECRET_KEY: secret_key,
            SERVICE_CODE: service_code,
        }   

def get_secret(alias=DEFAULT_ALIAS):
    '''
    Notes:
      get secret in alias
    Args:
      alias: alias that is used to index of secrets
    Returns:
      _secret[alias](dict): dictionary that contain ACCESS_KEY, SECRET_KEY, SERVICE_CODE
    '''
    if alias in _secret:
        return _secret[alias]
    else:
        raise KeyError('secret[%s] is not initialized. please call initialize() first')

def get_secret_from_yaml(yaml_file):
    '''
    Notes:
      load secret from yaml file
    Args:
      yaml_file(string): yaml fil path
    Returns:
      secret_yaml(dict): dictionary that contains ACCESS_KEY, SECRET_KEY, SERVICE_CODE
    '''
    import yaml
    with open(yaml_file, 'r') as fp: 
        secret_yaml = yaml.load(fp.read())
            
    if ACCESS_KEY and SECRET_KEY and SERVICE_CODE in secret_yaml:
        pass
    else:
        raise IOError('yaml file %s is invalie format' % yaml_file)

    return secret_yaml

def base_req(http_method, uniq_uri, expire_time, alias=DEFAULT_ALIAS, **kwargs):
    '''
    Args:
      http_method(string): http method(GET, POST, PUT, DELETE)
      api_name(string): api name defined in IIJ
      expire_time(datetime): token expiration date and time.
      alias(string): alias that is used to index of secrets
    Returns:
      res(urllib3.response.HTTPResponse): http response object
    '''
    import urllib3
    import urllib
    import hmac
    import hashlib
    import base64
    secret = get_secret(alias=alias)
    access_key = secret[ACCESS_KEY]
    secret_key = secret[SECRET_KEY]
    service_code = secret[SERVICE_CODE]

    request_path = r'/r/%s/%s/%s' % (API_VER, service_code, uniq_uri)
    quoted_request_path = urllib.quote(request_path)
    reqeust_url = BASE_URL + request_path

    string_to_sign = '%s\n' % http_method
    string_to_sign += '\n'
    string_to_sign += '\n'
    string_to_sign += 'x-iijapi-expire:%s\n' % expire_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    string_to_sign += 'x-iijapi-signaturemethod:HmacSHA256\n'
    string_to_sign += 'x-iijapi-signatureversion:2\n'
    string_to_sign += quoted_request_path

    hmac_signature = hmac.new(secret_key, string_to_sign, hashlib.sha256).digest()

    signature =  base64.b64encode(hmac_signature)

    urllib3.disable_warnings()
    http = urllib3.PoolManager()
    headers = {
                'x-iijapi-Expire': expire_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'x-iijapi-SignatureMethod': 'HmacSHA256',
                'x-iijapi-SignatureVersion': '2',
                'Authorization': 'IIJAPI %s:%s' % (access_key, signature)
              }

    res = http.urlopen(http_method, reqeust_url, redirect=False, headers=headers)
    return res

def get_zones():
    '''
    Notes:
      get all zones
    Returns:
      json_obj(dict): dict parsed from response json
    '''
    import json
    expire_time = get_expire_time()
    res = base_req('GET', 'zones.json', expire_time)

    json_obj = json.loads(res.data)
    return json_obj

def get_records(zone, style='FULL'):
    '''
    Notes:
      get all records in specified zone
    Args:
      zone(string): zone name
      style(string): FULL, RELATIVE or DETAIL
    Returns:
      json_obj(dict): dict parsed from response json
    '''
    import json
    expire_time = get_expire_time()
    uniq_uri = '%s/records/%s.json' % (zone, style)
    res = base_req('GET', uniq_uri , expire_time)

    json_obj = json.loads(res.data)
    return json_obj

def get_expire_time():
    '''
    Notes:
      create expired date and return
    Returns:
      expire_time(datetime.datetime): signature expired date and time
    '''
    import datetime
    now = datetime.datetime.now()
    expire_time = now + datetime.timedelta(hours=1)

    return expire_time

