import json
from typing import Union

import requests


def parse_json(json_data: dict) -> list:
    link_list = []
    obj_type: Union[str, None] = json_data.get('type')
    if obj_type == 'file':
        download_url = json_data.get('download_url')
        link_list.append(download_url)
    elif obj_type == 'dir':
        download_url = json_data.get('url')
        link_list.extend(parse_repo_dir(download_url))  # type:ignore
    else:
        raise ValueError('Unknown object type.')
    return link_list


def parse_repo_dir(url: str) -> list:
    link_list = []
    response = requests.get(url, timeout=10)
    json_objs = json.loads(response.text)

    for json_obj in json_objs:
        link_list.extend(parse_json(json_obj))

    return link_list
