import aiohttp
import asyncio
import logging
from collections import deque
from urllib.parse import urlsplit

from parser import Parser

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.StreamHandler()
    ])
_LOGGER = logging.getLogger()

_MAX_URLS = 400
_MAX_WORKERS = 20


class Crawler:
    def __init__(self, root_url: str):
        self._root_url = root_url

        split_result = urlsplit(root_url)
        self._subdomain = split_result.netloc

    async def get_html(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as response:
                assert response.status == 200
                html = await response.text()
                return html

    async def worker(
        self,
        name: str,
        pending_urls: asyncio.Queue,
        result_urls: asyncio.Queue
    ) -> None:
        while True:
            url = await pending_urls.get()
            html = await self.get_html(url)

            parser = Parser(html, url, self._subdomain)
            urls = parser.get_urls()

            for url in urls:
                if result_urls.qsize() >= _MAX_URLS:
                    pending_urls.task_done()
                elif result_urls._queue.count(url) == 0:
                    pending_urls.put_nowait(url)
                    result_urls.put_nowait(url)
                    _LOGGER.info(url)

            # Notify the pending_urls queue that the "work item" has been processed.
            pending_urls.task_done()

    async def _crawl(self) -> deque:
        # Create a queue that we will use to store our urls ready to be crawled.
        pending_urls = asyncio.Queue()
        pending_urls.put_nowait(self._root_url)
        # Create a queue that we will use to store the found urls.
        result_urls = asyncio.Queue()

        # Create worker tasks to process the queue concurrently.
        tasks = []
        for i in range(_MAX_WORKERS):
            task = asyncio.create_task(
                self.worker(f"worker-{i}", pending_urls, result_urls)
            )
            tasks.append(task)

        # Wait until the queue is fully processed.
        await pending_urls.join()

        # Cancel our worker tasks.
        for task in tasks:
            task.cancel()

        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*tasks, return_exceptions=True)

        return sorted(result_urls._queue)

    def crawl(self) -> None:
        result_urls = asyncio.run(self._crawl())

        # Write results to a file
        with open("crawler_results.txt", "w") as f:
            for url in result_urls:
                f.write("%s\n" % url)
