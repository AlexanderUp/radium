"""Tests for repo file downloading script."""

import json
from unittest.mock import MagicMock

import pytest
from aiohttp import ClientSession, web
from link_extractor import parse_json_content, parse_repo_dir

host: str = 'https://gitea.radium.group/'
request_headers: str = 'accept: application/json'

all_toml_route: str = '/api/v1/repos/radium/project-configuration/contents/nitpick/all.toml'
repo_content_all_toml: str = """
{
  "name": "all.toml",
  "path": "nitpick/all.toml",
  "sha": "d862d0a9e4cf120c5a38b88d488770dbf0bf6289",
  "type": "file",
  "size": 206,
  "encoding": "base64",
  "content": "W25pdHBpY2tdCm1pbmltdW1fdmVyc2lvbiA9ICIwLjMyLjAiCgpbbml0cGljay5zdHlsZXNdCmluY2x1ZGUgPSBbCiAgImVkaXRvcmNvbmZpZy50b21sIiwKICAiZmlsZS1zdHJ1Y3R1cmUudG9tbCIsCiAgInN0eWxlZ3VpZGUudG9tbCIsCiAgImZsYWtlOC50b21sIiwKICAiaXNvcnQudG9tbCIsCiAgImRhcmdsaW50LnRvbWwiLAogICJweXRlc3QudG9tbCIKXQo=",
  "target": null,
  "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/all.toml?ref=master",
  "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/all.toml",
  "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/d862d0a9e4cf120c5a38b88d488770dbf0bf6289",
  "download_url": "https://gitea.radium.group/radium/project-configuration/raw/branch/master/nitpick/all.toml",
  "submodule_git_url": null,
  "_links": {
    "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/all.toml?ref=master",
    "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/d862d0a9e4cf120c5a38b88d488770dbf0bf6289",
    "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/all.toml"
  }
}
"""
valid_extracted_links_list_all_toml: list = ['https://gitea.radium.group/radium/project-configuration/raw/branch/master/nitpick/all.toml']

repo_root_dir_route: str = '/api/v1/repos/radium/project-configuration/contents/'
repo_content_root_dir: str = """
[
  {
    "name": "LICENSE",
    "path": "LICENSE",
    "sha": "b9c199c98f9bec183a195a9c0afc0a2e4fcc7654",
    "type": "file",
    "size": 823,
    "encoding": null,
    "content": null,
    "target": null,
    "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/LICENSE?ref=master",
    "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/LICENSE",
    "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/b9c199c98f9bec183a195a9c0afc0a2e4fcc7654",
    "download_url": "https://gitea.radium.group/radium/project-configuration/raw/branch/master/LICENSE",
    "submodule_git_url": null,
    "_links": {
      "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/LICENSE?ref=master",
      "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/b9c199c98f9bec183a195a9c0afc0a2e4fcc7654",
      "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/LICENSE"
    }
  },
  {
    "name": "README.md",
    "path": "README.md",
    "sha": "d4f9f743e5073256d91cd7c160a067ab377276ee",
    "type": "file",
    "size": 157,
    "encoding": null,
    "content": null,
    "target": null,
    "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/README.md?ref=master",
    "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/README.md",
    "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/d4f9f743e5073256d91cd7c160a067ab377276ee",
    "download_url": "https://gitea.radium.group/radium/project-configuration/raw/branch/master/README.md",
    "submodule_git_url": null,
    "_links": {
      "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/README.md?ref=master",
      "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/d4f9f743e5073256d91cd7c160a067ab377276ee",
      "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/README.md"
    }
  },
  {
    "name": "nitpick",
    "path": "nitpick",
    "sha": "debb88cd16cfefdfe454bd8aab33ba3bce5e0977",
    "type": "dir",
    "size": 0,
    "encoding": null,
    "content": null,
    "target": null,
    "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick?ref=master",
    "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick",
    "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/debb88cd16cfefdfe454bd8aab33ba3bce5e0977",
    "download_url": null,
    "submodule_git_url": null,
    "_links": {
      "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick?ref=master",
      "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/debb88cd16cfefdfe454bd8aab33ba3bce5e0977",
      "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick"
    }
  }
]
"""

repo_nitpick_dir_route: str = '/api/v1/repos/radium/project-configuration/contents/nitpick/'
repo_content_nitpick_dir: str = """
[
  {
    "name": "all.toml",
    "path": "nitpick/all.toml",
    "sha": "d862d0a9e4cf120c5a38b88d488770dbf0bf6289",
    "type": "file",
    "size": 206,
    "encoding": null,
    "content": null,
    "target": null,
    "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/all.toml?ref=master",
    "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/all.toml",
    "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/d862d0a9e4cf120c5a38b88d488770dbf0bf6289",
    "download_url": "https://gitea.radium.group/radium/project-configuration/raw/branch/master/nitpick/all.toml",
    "submodule_git_url": null,
    "_links": {
      "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/all.toml?ref=master",
      "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/d862d0a9e4cf120c5a38b88d488770dbf0bf6289",
      "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/all.toml"
    }
  },
  {
    "name": "darglint.toml",
    "path": "nitpick/darglint.toml",
    "sha": "3cfa3e11912ee63eb1e0d9278c904386e77ca125",
    "type": "file",
    "size": 43,
    "encoding": null,
    "content": null,
    "target": null,
    "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/darglint.toml?ref=master",
    "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/darglint.toml",
    "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/3cfa3e11912ee63eb1e0d9278c904386e77ca125",
    "download_url": "https://gitea.radium.group/radium/project-configuration/raw/branch/master/nitpick/darglint.toml",
    "submodule_git_url": null,
    "_links": {
      "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/darglint.toml?ref=master",
      "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/3cfa3e11912ee63eb1e0d9278c904386e77ca125",
      "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/darglint.toml"
    }
  },
  {
    "name": "editorconfig.toml",
    "path": "nitpick/editorconfig.toml",
    "sha": "36f689a9b02d7bb9ed1395dfb752c1c5826948da",
    "type": "file",
    "size": 507,
    "encoding": null,
    "content": null,
    "target": null,
    "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/editorconfig.toml?ref=master",
    "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/editorconfig.toml",
    "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/36f689a9b02d7bb9ed1395dfb752c1c5826948da",
    "download_url": "https://gitea.radium.group/radium/project-configuration/raw/branch/master/nitpick/editorconfig.toml",
    "submodule_git_url": null,
    "_links": {
      "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/editorconfig.toml?ref=master",
      "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/36f689a9b02d7bb9ed1395dfb752c1c5826948da",
      "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/editorconfig.toml"
    }
  },
  {
    "name": "file-structure.toml",
    "path": "nitpick/file-structure.toml",
    "sha": "c1fe6d0a9705e04f518c11ba260ce0ab2e9cc5c1",
    "type": "file",
    "size": 641,
    "encoding": null,
    "content": null,
    "target": null,
    "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/file-structure.toml?ref=master",
    "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/file-structure.toml",
    "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/c1fe6d0a9705e04f518c11ba260ce0ab2e9cc5c1",
    "download_url": "https://gitea.radium.group/radium/project-configuration/raw/branch/master/nitpick/file-structure.toml",
    "submodule_git_url": null,
    "_links": {
      "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/file-structure.toml?ref=master",
      "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/c1fe6d0a9705e04f518c11ba260ce0ab2e9cc5c1",
      "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/file-structure.toml"
    }
  },
  {
    "name": "flake8.toml",
    "path": "nitpick/flake8.toml",
    "sha": "3d212a2ee25a2ca34b7fc3ad5b56d1e79dcffe4b",
    "type": "file",
    "size": 157,
    "encoding": null,
    "content": null,
    "target": null,
    "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/flake8.toml?ref=master",
    "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/flake8.toml",
    "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/3d212a2ee25a2ca34b7fc3ad5b56d1e79dcffe4b",
    "download_url": "https://gitea.radium.group/radium/project-configuration/raw/branch/master/nitpick/flake8.toml",
    "submodule_git_url": null,
    "_links": {
      "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/flake8.toml?ref=master",
      "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/3d212a2ee25a2ca34b7fc3ad5b56d1e79dcffe4b",
      "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/flake8.toml"
    }
  },
  {
    "name": "isort.toml",
    "path": "nitpick/isort.toml",
    "sha": "4efe0c7881065c168601ddfd2acd612cdad70e29",
    "type": "file",
    "size": 105,
    "encoding": null,
    "content": null,
    "target": null,
    "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/isort.toml?ref=master",
    "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/isort.toml",
    "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/4efe0c7881065c168601ddfd2acd612cdad70e29",
    "download_url": "https://gitea.radium.group/radium/project-configuration/raw/branch/master/nitpick/isort.toml",
    "submodule_git_url": null,
    "_links": {
      "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/isort.toml?ref=master",
      "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/4efe0c7881065c168601ddfd2acd612cdad70e29",
      "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/isort.toml"
    }
  },
  {
    "name": "pytest.toml",
    "path": "nitpick/pytest.toml",
    "sha": "90883fc0ad7e01d66dd69877088f96a8cdba0b70",
    "type": "file",
    "size": 406,
    "encoding": null,
    "content": null,
    "target": null,
    "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/pytest.toml?ref=master",
    "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/pytest.toml",
    "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/90883fc0ad7e01d66dd69877088f96a8cdba0b70",
    "download_url": "https://gitea.radium.group/radium/project-configuration/raw/branch/master/nitpick/pytest.toml",
    "submodule_git_url": null,
    "_links": {
      "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/pytest.toml?ref=master",
      "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/90883fc0ad7e01d66dd69877088f96a8cdba0b70",
      "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/pytest.toml"
    }
  },
  {
    "name": "styleguide.toml",
    "path": "nitpick/styleguide.toml",
    "sha": "c169f18e1d3912b3dd2de3c4b056f8924d89250b",
    "type": "file",
    "size": 315,
    "encoding": null,
    "content": null,
    "target": null,
    "url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/styleguide.toml?ref=master",
    "html_url": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/styleguide.toml",
    "git_url": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/c169f18e1d3912b3dd2de3c4b056f8924d89250b",
    "download_url": "https://gitea.radium.group/radium/project-configuration/raw/branch/master/nitpick/styleguide.toml",
    "submodule_git_url": null,
    "_links": {
      "self": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents/nitpick/styleguide.toml?ref=master",
      "git": "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/blobs/c169f18e1d3912b3dd2de3c4b056f8924d89250b",
      "html": "https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/styleguide.toml"
    }
  }
]
"""


async def repo_all_toml_content(request: web.Request) -> web.Response:
    return web.Response(body=repo_content_all_toml)


async def repo_root_content(request: web.Request) -> web.Response:
    return web.Response(body=repo_content_root_dir)


async def repo_nitpick_content(request: web.Request) -> web.Response:
    return web.Response(body=repo_content_nitpick_dir)


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_route('GET', all_toml_route, repo_all_toml_content)
    app.router.add_route('GET', repo_nitpick_dir_route, repo_nitpick_content)
    app.router.add_route('GET', repo_root_dir_route, repo_root_content)
    return app


@pytest.mark.asyncio()
async def test_repo_json(aiohttp_client):
    client = await aiohttp_client(create_app())
    resp = await client.get(all_toml_route)
    text = await resp.text()
    json_data = json.loads(text)

    async with ClientSession() as session:
        extracted_links_list = await parse_json_content(json_data, session)

    assert extracted_links_list == valid_extracted_links_list_all_toml


@pytest.mark.asyncio()
async def test_parse_nitpick_dir_json_resp(aiohttp_client):
    client = await aiohttp_client(create_app())
    resp = await client.get(repo_nitpick_dir_route)
    text = await resp.text()
    json_data = json.loads(text)

    extracted_links_list = []
    async with ClientSession() as session:
        for json_obj in json_data:
            link_list = await parse_json_content(json_obj, session)
            extracted_links_list.extend(link_list)

    assert len(extracted_links_list) == 8


@pytest.mark.asyncio()
async def test_parse_nitpick_dir():
    extracted_links_list = []

    mock = ClientSession
    mock.get = MagicMock()
    mock.get.return_value.__aenter__.return_value.json.return_value = json.loads(repo_content_nitpick_dir)

    async with ClientSession() as session:
        link_list = await parse_repo_dir(repo_nitpick_dir_route, session)
        extracted_links_list.extend(link_list)

    assert len(extracted_links_list) == 8
