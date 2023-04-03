"""Tests for repo file downloading script."""

import json
from unittest.mock import MagicMock

import pytest
from aiohttp import ClientSession, web
from link_extractor import parse_json_content, parse_repo_dir
from pytest_aiohttp.plugin import AiohttpClient
from test_config import (
    all_toml_route,
    repo_content_all_toml,
    repo_content_nitpick_dir,
    repo_content_root_dir,
    repo_nitpick_dir_route,
    repo_root_dir_route,
    valid_extracted_links_list_all_toml,
)


async def repo_all_toml_content(request: web.Request) -> web.Response:
    """Return response for <all.toml> request."""
    return web.Response(body=repo_content_all_toml)


async def repo_root_content(request: web.Request) -> web.Response:
    """Return response for repo root request."""
    return web.Response(body=repo_content_root_dir)


async def repo_nitpick_content(request: web.Request) -> web.Response:
    """Return response for repo nitpick dir request."""
    return web.Response(body=repo_content_nitpick_dir)


def create_app() -> web.Application:
    """Return app with predefined routes."""
    app = web.Application()
    app.router.add_route('GET', all_toml_route, repo_all_toml_content)
    app.router.add_route('GET', repo_nitpick_dir_route, repo_nitpick_content)
    app.router.add_route('GET', repo_root_dir_route, repo_root_content)
    return app


@pytest.mark.asyncio()
async def test_all_toml_json(aiohttp_client: AiohttpClient) -> None:
    """Test parsing of <all.toml> api request."""
    client = await aiohttp_client(create_app())
    resp = await client.get(all_toml_route)
    json_data = json.loads(await resp.text())

    async with ClientSession() as session:
        extracted_links_list = await parse_json_content(json_data, session)

    assert extracted_links_list == valid_extracted_links_list_all_toml


@pytest.mark.asyncio()
async def test_parse_nitpick_dir_json_resp(
    aiohttp_client: AiohttpClient,
) -> None:
    """Test parsing of <nitpick> dir api request."""
    client = await aiohttp_client(create_app())
    resp = await client.get(repo_nitpick_dir_route)
    json_data = json.loads(await resp.text())

    extracted_links_list: list = []
    async with ClientSession() as session:
        for json_obj in json_data:
            link_list = await parse_json_content(json_obj, session)
            extracted_links_list.extend(link_list)

    assert len(extracted_links_list) == 8


@pytest.mark.asyncio()
async def test_parse_nitpick_dir() -> None:
    """Test processing of <nitpick> dir api request."""
    extracted_links_list: list = []

    mock = ClientSession
    mock.get = MagicMock()
    r_content = json.loads(repo_content_nitpick_dir)
    mock.get.return_value.__aenter__.return_value.json.return_value = r_content

    async with ClientSession() as session:
        link_list = await parse_repo_dir(repo_nitpick_dir_route, session)
        extracted_links_list.extend(link_list)

    assert len(extracted_links_list) == 8
