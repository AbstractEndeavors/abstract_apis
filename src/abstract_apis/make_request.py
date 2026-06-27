import logging
import os
import requests

from .request_utils import *


logging.basicConfig(level=logging.WARNING)


def close_request_files(files):
    if not files or not isinstance(files, dict):
        return

    for value in files.values():
        if hasattr(value, "close"):
            value.close()
            continue

        if isinstance(value, tuple):
            for part in value:
                if hasattr(part, "close"):
                    part.close()


def make_request(
    url,
    data=None,
    json_data=None,
    headers=None,
    get_post=None,
    endpoint=None,
    files=None,
    timeout=600,
    status_code=False,
    retry_after=False,
    raw_response=False,
    response_result=None,
    load_nested_json=True,
    auth=None,
    logger=True,
):
    data = data or {}

    values = get_values_js(
        url=url,
        endpoint=endpoint,
        data=data,
        headers=headers,
        auth=auth,
        files=files,
        timeout=timeout,
    )

    if json_data and not files:
        values.pop("data", None)
        values["json"] = json_data

    method = str(
        get_post or ("POST" if files or data or json_data else "GET")
    ).upper()

    try:
        response = requests.request(method=method, **values)
    except Exception as e:
        logging.error(f"Request failed: {e}")
        raise

    return get_response(
        response,
        raw_response=raw_response,
        response_result=response_result,
        load_nested_json=load_nested_json,
    )


def postRequest(
    url,
    data=None,
    headers=None,
    endpoint=None,
    request_file_path=None,
    files=None,
    file_field_name="files",
    filename=None,
    mime_type=None,
    timeout=600,
    status_code=False,
    retry_after=False,
    raw_response=False,
    response_result=None,
    load_nested_json=True,
    auth=None,
    **kwargs,
):
    owns_files = False

    if request_file_path:
        files = get_request_file(
            request_file_path,
            field_name=file_field_name,
            filename=filename,
            mime_type=mime_type,
        )
        owns_files = True

    elif files and isinstance(files, str):
        files = get_request_file(
            files,
            field_name=file_field_name,
            filename=filename,
            mime_type=mime_type,
        )
        owns_files = True

    data = data or kwargs or {}

    try:
        return make_request(
            url=url,
            data=data,
            headers=headers,
            endpoint=endpoint,
            get_post="POST",
            files=files,
            timeout=timeout,
            status_code=status_code,
            retry_after=retry_after,
            raw_response=raw_response,
            response_result=response_result,
            load_nested_json=load_nested_json,
            auth=auth,
        )
    finally:
        if owns_files:
            close_request_files(files)


def getRequest(
    url,
    data=None,
    headers=None,
    endpoint=None,
    request_file_path=None,
    files=None,
    file_field_name="files",
    timeout=600,
    status_code=False,
    retry_after=False,
    raw_response=False,
    response_result=None,
    load_nested_json=True,
    auth=None,
    **kwargs,
):
    owns_files = False

    if request_file_path:
        files = get_request_file(request_file_path, field_name=file_field_name)
        owns_files = True

    elif files and isinstance(files, str):
        files = get_request_file(files, field_name=file_field_name)
        owns_files = True

    data = data or kwargs or {}

    try:
        return make_request(
            url=url,
            data=data,
            headers=headers,
            endpoint=endpoint,
            get_post="GET",
            files=files,
            timeout=timeout,
            status_code=status_code,
            retry_after=retry_after,
            raw_response=raw_response,
            response_result=response_result,
            load_nested_json=load_nested_json,
            auth=auth,
        )
    finally:
        if owns_files:
            close_request_files(files)


def makeRequest(
    url,
    *args,
    data=None,
    headers=None,
    endpoint=None,
    get_post=None,
    request_file_path=None,
    files=None,
    file_field_name="files",
    timeout=600,
    status_code=False,
    retry_after=False,
    raw_response=False,
    response_result=None,
    load_nested_json=True,
    auth=None,
    **kwargs,
):
    owns_files = False

    if request_file_path:
        files = get_request_file(request_file_path, field_name=file_field_name)
        owns_files = True

    elif files and isinstance(files, str):
        files = get_request_file(files, field_name=file_field_name)
        owns_files = True

    data = data or kwargs or {}

    if not isinstance(data, dict):
        data = {"args": make_list(data or [])}

    data["args"] = make_list(data.get("args") or []) + list(args)

    try:
        return make_request(
            url=url,
            data=data,
            headers=headers,
            endpoint=endpoint,
            get_post=get_post,
            files=files,
            timeout=timeout,
            status_code=status_code,
            retry_after=retry_after,
            raw_response=raw_response,
            response_result=response_result,
            load_nested_json=load_nested_json,
            auth=auth,
        )
    finally:
        if owns_files:
            close_request_files(files)


def getRpcRequest(
    url,
    method=None,
    params=None,
    jsonrpc=None,
    id=None,
    headers=None,
    endpoint=None,
    status_code=False,
    retry_after=False,
    raw_response=False,
    response_result=None,
    load_nested_json=True,
    auth=None,
):
    data = getRpcData(
        method=method,
        params=params,
        jsonrpc=jsonrpc,
        id=id,
    )

    return getRequest(
        url,
        data=data,
        headers=headers,
        endpoint=endpoint,
        status_code=status_code,
        retry_after=retry_after,
        raw_response=raw_response,
        response_result=response_result,
        load_nested_json=load_nested_json,
        auth=auth,
    )


def postRpcRequest(
    url,
    method=None,
    params=None,
    jsonrpc=None,
    id=None,
    headers=None,
    endpoint=None,
    status_code=False,
    retry_after=False,
    raw_response=False,
    response_result=None,
    load_nested_json=True,
    auth=None,
):
    data = getRpcData(
        method=method,
        params=params,
        jsonrpc=jsonrpc,
        id=id,
    )

    return make_request(
        url=url,
        data=data,
        headers=headers,
        endpoint=endpoint,
        get_post="POST",
        status_code=status_code,
        retry_after=retry_after,
        raw_response=raw_response,
        response_result=response_result,
        load_nested_json=load_nested_json,
        auth=auth,
    )
