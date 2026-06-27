import json
import os
import requests
import aiohttp
import asyncio

from flask import jsonify
from abstract_essentials import make_list, eatAll, get_mime_type


def get_headers(is_json=True):
    if is_json:
        return {"Content-Type": "application/json"}
    return {}


def ensure_json(data):
    if isinstance(data, str):
        try:
            json.loads(data)
            return data
        except ValueError:
            pass
    return json.dumps(data)


def stripit(string, chars=[]):
    string = string or ""
    for char in make_list(chars):
        string = string.strip(char)
    return string


def make_endpoint(endpoint):
    return eatAll(endpoint, ["/"])


def make_url(url):
    return eatAll(url, ["/"])


def get_url(url, endpoint=None):
    url = eatAll(url, ["/"])
    endpoint = eatAll(endpoint, ["/"])
    return eatAll(f"{url}/{endpoint}", ["/"])


def get_values_js(
    url=None,
    data=None,
    headers=None,
    endpoint=None,
    auth=None,
    files=None,
    timeout=600,
):
    if endpoint:
        url = get_url(url, endpoint=endpoint)

    values = {
        "url": url,
        "timeout": timeout,
    }

    if auth:
        values["auth"] = auth

    if files:
        values["files"] = files
        values["data"] = data or {}

        # Never manually set Content-Type for multipart requests.
        # requests will generate the multipart boundary.
        if headers:
            values["headers"] = {
                k: v
                for k, v in headers.items()
                if k.lower() != "content-type"
            }

        return values

    values["json"] = data or {}

    if headers:
        values["headers"] = headers
    else:
        values["headers"] = get_headers(is_json=True)

    return values


def get_text_response(response):
    try:
        return response.text
    except Exception:
        return None


def load_inner_json(data):
    if isinstance(data, str):
        try:
            return load_inner_json(json.loads(data))
        except (ValueError, TypeError):
            return data

    if isinstance(data, dict):
        return {key: load_inner_json(value) for key, value in data.items()}

    if isinstance(data, list):
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
        print(f"Could not get Retry-After: {e}")
        return None


def get_json_response(
    response=None,
    response_result=None,
    load_nested_json=True,
    status_code=None,
    value=None,
):
    if response is None and response_result is None and (status_code or value):
        return jsonify({"result": value}), status_code

    response_result = response_result or "result"

    try:
        try:
            response_json = response.json()
        except Exception:
            response_json = response

        if load_nested_json:
            response_json = load_inner_json(response_json)

        if isinstance(response_json, dict):
            response_json = response_json.get(response_result, response_json)

        if response_json is not None:
            return response_json

    except Exception as e:
        print(e)
        return response_result

    return response_result


def get_response(
    response,
    response_result=None,
    raw_response=False,
    load_nested_json=True,
):
    if raw_response:
        return response

    json_response = get_json_response(
        response,
        response_result=response_result,
        load_nested_json=load_nested_json,
    )

    if json_response is not None:
        return json_response

    text_response = get_text_response(response)

    if text_response:
        return text_response

    return response


def getRpcData(method=None, params=None, jsonrpc=None, id=None):
    return {
        "jsonrpc": jsonrpc or "2.0",
        "id": id or 1,
        "method": method,
        "params": params or [],
    }


def get_request_file(file_path, field_name="files", filename=None, mime_type=None):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    filename = filename or os.path.basename(file_path)
    mime_type = mime_type or get_mime_type(file_path) or "application/octet-stream"

    file_handle = open(file_path, "rb")

    return {
        field_name: (
            filename,
            file_handle,
            mime_type,
        )
    }
