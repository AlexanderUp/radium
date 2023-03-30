import asyncio
import concurrent.futures
import logging
import tempfile
from pathlib import Path

import aiohttp
from aiofile import async_open
from aiohttp import ClientSession

from link_extractor import parse_dir
from utils import get_hash

logging.basicConfig(
    format="[%(levelname)s]:%(asctime)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)


async def download_file(url: str, session: ClientSession) -> bytes:
    logging.info(f"Processing: {url}")
    async with session.get(url) as response:
        return await response.read()


async def write_file_to_tempdir(url: str, data: bytes, directory: str) -> None:
    path_to_file = Path(directory) / Path(url).name
    async with async_open(path_to_file, "bw") as file:
        await file.write(data)


async def process_file(url: str,
                       session: ClientSession,
                       directory: str,
                       semaphore: asyncio.Semaphore) -> None:
    async with semaphore:
        file_content = await download_file(url, session)
        await write_file_to_tempdir(url, file_content, directory)


async def set_tasks(urls: list,
                    directory: str,
                    concur_task_num: int) -> None:
    session = aiohttp.ClientSession()
    sem = asyncio.Semaphore(concur_task_num)
    tasks = [asyncio.create_task(
        process_file(url, session, directory, sem)) for url in urls]
    logging.info(f"{len(tasks)} urls collected.")
    await asyncio.gather(*tasks)
    await session.close()


async def main(url, concur_task_num=3):
    logging.info("Script started.")
    urls = parse_dir(url)

    with tempfile.TemporaryDirectory() as tempdir:
        logging.info(f"Temporary dir: {tempdir}")

        await set_tasks(urls, tempdir, concur_task_num)

        paths = list(Path(tempdir).iterdir())

        with concurrent.futures.ProcessPoolExecutor() as executor:
            for path, hash in zip(paths, executor.map(get_hash, paths)):
                print(f"{hash} {path}")

    logging.info("Script completed.")


if __name__ == "__main__":
    url = "https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents"  # noqa

    asyncio.run(main(url))
