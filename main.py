import asyncio
import logging
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from aiofile import async_open
from aiohttp import ClientSession

from link_extractor import parse_repo_dir
from utils import get_hash

logging.basicConfig(
    format='[%(levelname)s]:%(asctime)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO,
)


async def download_file(file_url: str, session: ClientSession) -> bytes:
    """Download file with given URL."""
    logging.info(f'Processing: {file_url}')
    async with session.get(file_url) as response:
        return await response.read()


async def write_file_to_tempdir(
        file_url: str,
        file_content: bytes,
        directory: str,
) -> None:
    """Write file to given directory."""
    path_to_file = Path(directory) / Path(file_url).name
    async with async_open(path_to_file, 'bw') as out_file:
        await out_file.write(file_content)


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
    logging.info(f'{len(tasks)} urls collected.')
    await asyncio.gather(*tasks)
    await session.close()


async def main(url, concur_task_num=3):
    """Download file, save them and calculate hash."""
    logging.info('Script started.')

    with tempfile.TemporaryDirectory() as tempdir:
        async with ClientSession() as session:
            urls = await parse_repo_dir(url, session)

            await run_tasks(urls, tempdir, session, concur_task_num)

            paths = list(Path(tempdir).iterdir())

            with ProcessPoolExecutor() as executor:
                zipped_paths = zip(paths, executor.map(get_hash, paths))
                for path, calculated_hash in zipped_paths:
                    logging.info(f'{calculated_hash} {path}')

    logging.info('Script completed.')


if __name__ == '__main__':
    url = 'https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents'  # noqa

    asyncio.run(main(url))
