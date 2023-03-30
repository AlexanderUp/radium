import json
from typing import Union

import requests


def parse_json(data: dict) -> list:
    link_list = []
    obj_type: Union[str, None] = data.get("type")
    if obj_type == "file":
        download_url = data.get("download_url")
        link_list.append(download_url)
    elif obj_type == "dir":
        download_url = data.get("url")
        link_list.extend(parse_dir(download_url))  # type:ignore
    else:
        raise ValueError("Unknown object type.")
    return link_list


def parse_dir(url: str) -> list:
    link_list = []
    response = requests.get(url, timeout=10)
    json_obj = json.loads(response.text)

    for obj in json_obj:
        link_list.extend(parse_json(obj))

    return link_list
