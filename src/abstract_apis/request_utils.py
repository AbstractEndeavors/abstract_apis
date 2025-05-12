import json,requests,aiohttp,asyncio
from abstract_utilities import make_list,eatAll
def get_headers():
    return {
        'Content-Type': 'application/json',
    }

def ensure_json(data):
    if isinstance(data, str):
        try:
            json.loads(data)  # Verify it's valid JSON
            return data
        except ValueError:
            pass  # Not valid JSON, continue to dump it
    return json.dumps(data)

def stripit(string, chars=[]):
    string = string or ''
    for char in make_list(chars):
        string = string.strip(char)
    return string

def make_endpoint(endpoint):
    return eatAll(endpoint, ['/'])

def make_url(url):
    return eatAll(url, ['/'])

def get_url(url, endpoint=None):
    url = eatAll(url, ['/'])
    endpoint =  eatAll(endpoint, ['/'])
    url = f"{url}/{endpoint}"
    return eatAll(url, ['/'])

def get_text_response(response):
    try:
        return response.text
    except Exception as e:
        return None

def load_inner_json(data):
    """Recursively load nested JSON strings within the main JSON response, even if nested within lists."""
    if isinstance(data, str):
        try:
            return load_inner_json(json.loads(data))  # Recursively parse inner JSON strings
        except (ValueError, TypeError):
            return data
    elif isinstance(data, dict):
        return {key: load_inner_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [load_inner_json(item) for item in data]
    return data    
def get_status_code(response):
    try:
        return response.status_code
    except Exception as e:
        print(f"Could not get status code: {e}")
        return None
def get_retry_after(response):
    try:
        return response.headers.get("Retry-After")
    except Exception as e:
        print(f"Could not get status code: {e}")
        return None

    
def get_values_js(url=None,data=None,headers=None,endpoint=None,auth=None):
    if endpoint:
        url = get_url(url, endpoint=endpoint)
    values = {'url':url,'auth':auth}
    dataKey = 'json' if isinstance(data,dict) else 'data'
    values[dataKey]=data
    values['headers']=headers or get_headers()
    return values

def get_json_response(response, response_result=None, load_nested_json=True):
    response_result = response_result or 'result'
    
    try:
        try:
            response_json = response.json()
        except Exception as e:
            response_json = response
        if isinstance(response_json,dict):
            response_json = response_json.get(response_result, response_json)

        if response_json is not None:
            return response_json
    except Exception as e:
        print(e)
        return response_result
    return response_result
def get_response(response, response_result=None, raw_response=False, load_nested_json=True):
    if raw_response:
        return response
    json_response = get_json_response(response, response_result=response_result, load_nested_json=load_nested_json)
    if json_response is not None:
        return json_response
    text_response = get_text_response(response)
    if text_response:
        return text_response
    return response  # Return raw content as a last resort
def getRpcData(method=None,params=None,jsonrpc=None,id=None):
    return {
            "jsonrpc": jsonrpc or "2.0",
            "id": id or 1,
            "method": method,
            "params": params or [],
        }
