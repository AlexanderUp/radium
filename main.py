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
    logging.info(f'Processing: {file_url}')
    async with session.get(file_url) as response:
        return await response.read()


async def write_file_to_tempdir(file_url: str, file_content: bytes, directory: str) -> None:
    path_to_file = Path(directory) / Path(file_url).name
    async with async_open(path_to_file, 'bw') as out_file:
        await out_file.write(file_content)


async def process_file(url: str,
                       session: ClientSession,
                       directory: str,
                       semaphore: asyncio.Semaphore
                       ) -> None:
    async with semaphore:
        file_content = await download_file(url, session)
        await write_file_to_tempdir(url, file_content, directory)


async def run_tasks(urls: list,
                    directory: str,
                    concur_task_num: int) -> None:
    session = ClientSession()
    sem = asyncio.Semaphore(concur_task_num)
    tasks = [asyncio.create_task(
        process_file(url, session, directory, sem)) for url in urls]
    logging.info(f'{len(tasks)} urls collected.')
    await asyncio.gather(*tasks)
    await session.close()


def main(url, concur_task_num=3):
    logging.info('Script started.')
    urls = parse_repo_dir(url)

    with tempfile.TemporaryDirectory() as tempdir:
        asyncio.run(run_tasks(urls, tempdir, concur_task_num))

        paths = list(Path(tempdir).iterdir())

        with ProcessPoolExecutor() as executor:
            for path, calculated_hash in zip(paths, executor.map(get_hash, paths)):
                print(f'{calculated_hash} {path}')

    logging.info('Script completed.')


if __name__ == '__main__':
    url = 'https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents'  # noqa

    main(url)
