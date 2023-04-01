"""Return list of links in specifed remote repository directory."""

from typing import Union

from aiohttp import ClientError, ClientSession
from loggers import logger


async def parse_json_content(json_data: dict, session: ClientSession) -> list:
    """Parse json content."""
    link_list = []
    obj_type: Union[str, None] = json_data.get('type')
    if obj_type == 'file':
        download_url = json_data.get('download_url')
        if download_url:
            link_list.append(download_url)
    elif obj_type == 'dir':
        download_url = json_data.get('url')
        if download_url:
            extracted_links = await parse_repo_dir(download_url, session)
            link_list.extend(extracted_links)
    else:
        raise ValueError('Unknown object type.')
    return link_list


async def parse_repo_dir(url: str, session: ClientSession) -> list:
    """Recursively parse given repo directory."""
    link_list: list[str] = []
    try:
        async with session.get(url) as resp:
            response_json = await resp.json()
    except ClientError as err:
        logger.error('Error occured.')
    else:
        for json_obj in response_json:
            extracted_links = await parse_json_content(json_obj, session)
            link_list.extend(extracted_links)
    return link_list
