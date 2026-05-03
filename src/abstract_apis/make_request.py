from .request_utils import *
import logging
# Suppress logs below WARNING level
logging.basicConfig(level=logging.WARNING)

def make_request(url, data=None, json_data=None, headers=None, get_post=None, endpoint=None, files=None, status_code=False, retry_after=False, raw_response=False, response_result=None, load_nested_json=True, auth=None, logger=True):
    # Get base values (url, headers, etc)
    values = get_values_js(url=url, endpoint=endpoint, data=data, headers=headers)
    
    # 1. Finalizing Files Structure
    if files:
        # If files is a dict, convert it to items (list of tuples) to avoid the unpack error
        if isinstance(files, dict):
            values['files'] = list(files.items())
        else:
            values['files'] = files

        # When files are present, 'data' should be a dict for form-data, not JSON
        values['data'] = data
    
    # 2. Finalizing JSON/Data
    elif json_data:
        values['json'] = json_data
    elif data and str(get_post).upper() in ['POST', 'PUT']:
        # If no files, we assume standard JSON POST
        values['json'] = data
    
    if auth:
        values['auth'] = auth

    method = str(get_post or ('POST' if data is None else 'GET')).upper()
    
    try:
        # The **values expansion now includes 'files' correctly
        response = requests.request(method=method, **values)
    except Exception as e:
        logging.error(f"Request failed: {e}")
        raise

    return get_response(response, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)
def getRpcData(method=None,params=None,jsonrpc=None,id=None):
    return {
            "jsonrpc": jsonrpc or "2.0",
            "id": 0,
            "method": method,
            "params": params,
        }
def get_request_file(file_path):
    """
    Returns a list of 2-tuples to satisfy the requests unpacker.
    Format: [ (field_name, file_handle) ]
    """
    try:
        f = open(file_path, 'rb')
        # Using a list of one tuple prevents the 'too many values to unpack' error
        return [('files', f)] 
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
def postRequest(url,
                data=None,
                headers=None,
                endpoint=None,
                request_file_path=None,
                files=None,
                status_code=False,
                retry_after=False,
                raw_response=False,
                response_result=None,
                load_nested_json=True,
                auth=None,
                **kwargs
                ):
    if request_file_path:
        files = get_request_file(request_file_path)
    data = data or kwargs
    return make_request(url,
                        data=data,
                        headers=headers,
                        endpoint=endpoint,
                        get_post='POST',
                        files=files,
                        status_code=status_code,
                        retry_after=retry_after,
                        raw_response=raw_response,
                        response_result=response_result,
                        load_nested_json=load_nested_json,
                        auth=auth
                        )

def getRequest(url, data=None, headers=None, endpoint=None,request_file_path=None,files=None, status_code=False, retry_after=False, raw_response=False, response_result=None, load_nested_json=True,auth=None,**kwargs):
    if request_file_path:
        files = get_request_file(request_file_path)
    data = data or kwargs
    return make_request(url, data=data, headers=headers, endpoint=endpoint, get_post='GET', files=files, status_code=status_code, retry_after=retry_after, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)
def makeRequest(url, *args,data=None, headers=None, endpoint=None,get_post=None,request_file_path=None,files=None, status_code=False, retry_after=False, raw_response=False, response_result=None, load_nested_json=True,auth=None,**kwargs):
    if request_file_path:
        files = get_request_file(request_file_path)
    data = data or kwargs
    if not isinstance(data,dict):
        data = {"args":make_list(data or [])}
    data['args'] = make_list(data.get('args') or [])+list(args)
    return make_request(url, data=data, headers=headers, endpoint=endpoint, get_post=get_post, files=files, status_code=status_code, retry_after=retry_after, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)

def getRpcRequest(url, method=None,params=None,jsonrpc=None,id=None,headers=None, endpoint=None, status_code=False, retry_after=False, raw_response=False, response_result=None, load_nested_json=True,auth=None):
    data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
    return getRequest(url, data, headers=headers, endpoint=endpoint, status_code=status_code, retry_after=retry_after, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)

def postRpcRequest(url, method=None,params=None,jsonrpc=None,id=None,headers=None, get_post='GET',endpoint=None, status_code=False, retry_after=False, raw_response=False, response_result=None, load_nested_json=True,auth=None):
    data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
    return make_request(url=url, data=data, headers=headers, endpoint=endpoint,get_post='POST', status_code=status_code, retry_after=retry_after, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)


