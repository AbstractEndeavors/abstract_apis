from solana.rpc.core import _ClientCore
from typing import Dict, List, Optional, Sequence, Union
from solana.rpc.commitment import Commitment, Finalized
from abstract_solana.abstract_utils.pubkey_utils import get_pubkey,get_sigkey
import inspect,asyncio,json,requests
from abstract_apis import get_url,make_endpoint,get_headers,asyncPostRequest,get_async_response,get_headers
from abstract_utilities import *
def convert_to_lower(string_obj):
    return ''.join(f"_{char.lower()}" if char.isupper() else char for char in str(string_obj))
def convert_to_upper(string_obj):
    words = string_obj.split('_')
    return words[0] + ''.join(word.capitalize() for word in words[1:])
def convert_to_body(string_obj):
    return f"_{convert_to_lower(string_obj)}_body"
class Client(_ClientCore):
    def __init__(
        self,
        endpoint: Optional[str] = None,
        commitment: Optional[Commitment] = "confirmed",
        timeout: float = 10,
        extra_headers: Optional[Dict[str, str]] = None,
    ):
        """Init API client."""
        super().__init__(commitment)
client = Client()
def get_function(function_string):
    try:
        function = getattr(client, function_string)
    except:
        function =None
    return function
def call_function(function,*args,**kwargs):
    result = None
    if function:
        try:
            result = function(*args,**kwargs)
        except TypeError as e:
            print(f"Error calling function: {e}")
            result = None
    return result
def convert_value(key,value):
    pubkeys = ['pubkeys','pubkey','mint','owner','delegate','address']
    if key in pubkeys:
        if isinstance(value,list):
            value = [get_pubkey(pubkey) for pubkey in value]
        else:
            value = get_pubkey(value)
        return value
    signatures = ['until','before','tx_sig','signature','before','signatures']
    if key in signatures:
        if isinstance(value,list):
            value = [get_sigkey(signature) for signature in value]
        else:
            value = get_sigkey(value)
        return value
    defaults = {"commitment":"confirmed","encoding":"jsonParsed","data_slice":None}
    if key in defaults:
        value = value or defaults.get(key)
    return value
def get_conversions(variables,*args,**kwargs):
    for i,arg in enumerate(args):
        variable = variables[i]
        kwargs[variable] = arg
    for key,value in kwargs.items():
        if key in variables:
            kwargs[key] = convert_value(key,value)
    for variable in variables:
        if variable not in kwargs:
            kwargs[variable]=convert_value(variable,None)
    return kwargs
def get_params(function):
    sig = inspect.signature(function)
    return list(sig.parameters.keys())
def get_rpc_dict(endpoint,*args,**kwargs):
    body_call = convert_to_body(endpoint)
    function = get_function(body_call)
    variables = get_params(function)
    input(variables)
    kwargs = get_conversions(variables,*args,**kwargs)
    input(kwargs)
    kwargs = json.loads(str(call_function(function,**kwargs)))
    if 'maxSupportedTransactionVersion' in kwargs.get('params')[1]:
        if not is_number(kwargs.get('params',{})[1].get('maxSupportedTransactionVersion')):
            kwargs['params'][1]['maxSupportedTransactionVersion'] = 0
    return kwargs


