"""Download files from repo, save them, calculate hash."""

import asyncio
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from aiofile import async_open
from aiohttp import ClientError, ClientSession
from aux_utils import get_hash
from link_extractor import parse_repo_dir
from loggers import logger


async def download_file(file_url: str, session: ClientSession) -> bytes:
    """Download file with given URL."""
    msg = 'Processing: {0}'.format(file_url)
    logger.info(msg)
    file_content = b''
    try:
        async with session.get(file_url) as response:
            file_content = await response.read()
    except ClientError as err:
        logger.error('Error occured.')
    return file_content


async def write_file_to_tempdir(
    file_url: str,
    file_content: bytes,
    directory: str,
) -> None:
    """Write file to given directory."""
    path_to_file = Path(directory) / Path(file_url).name
    try:
        async with async_open(path_to_file, 'bw') as out_file:
            await out_file.write(file_content)
    except OSError as err:
        logger.error('Error occured.')


async def process_file(
    url: str,
    session: ClientSession,
    directory: str,
    semaphore: asyncio.Semaphore,
) -> None:
    """Download file from given URL and write them to specified directory."""
    async with semaphore:
        file_content = await download_file(url, session)
        await write_file_to_tempdir(url, file_content, directory)


async def run_tasks(
    urls: list,
    directory: str,
    session: ClientSession,
    concur_task_num: int,
) -> None:
    """Create and schedule tasks for execution."""
    sem = asyncio.Semaphore(concur_task_num)
    tasks = [process_file(url, session, directory, sem) for url in urls]
    msg = '{0} urls collected.'.format(len(tasks))
    logger.info(msg)
    await asyncio.gather(*tasks)
    await session.close()


def log_file_hashes(paths: list) -> None:
    """Get file hashes with ProcessPoolExecutor."""
    with ProcessPoolExecutor() as executor:
        zipped_paths = zip(paths, executor.map(get_hash, paths))
        for path, calculated_hash in zipped_paths:
            msg = '{0} {1}'.format(calculated_hash, path)
            logger.info(msg)


async def main(url: str, concur_task_num: int = 3) -> None:
    """Download file, save them and calculate hash."""
    logger.info('Script started.')

    with tempfile.TemporaryDirectory() as tempdir:
        async with ClientSession() as session:
            urls = await parse_repo_dir(url, session)

            await run_tasks(urls, tempdir, session, concur_task_num)

            paths = list(Path(tempdir).iterdir())
            log_file_hashes(paths)

    logger.info('Script completed.')


if __name__ == '__main__':
    host = 'https://gitea.radium.group'
    host_path = '/api/v1/repos/radium/project-configuration/contents/'
    url = ''.join((host, host_path))
    asyncio.run(main(url))
