import aiohttp
import asyncio
from urllib.parse import urlsplit

from parser import Parser


_MAX_URLS = 100
_MAX_WORKERS = 10


class Crawler:
    def __init__(self, root_url):
        self._root_url = root_url

        split_result = urlsplit(root_url)
        self._subdomain = split_result.netloc

    async def get_html(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as response:
                assert response.status == 200
                html = await response.text()
                return html

    async def worker(self, name, work_queue, result_queue):
        while True:

            url = await work_queue.get()
            html = await self.get_html(url)

            parser = Parser(html, url, self._subdomain)
            urls = parser.get_urls()

            for url in urls:
                if result_queue.qsize() >= _MAX_URLS:
                    work_queue.task_done()
                else:
                    if result_queue._queue.count(url) == 0:
                        work_queue.put_nowait(url)
                        result_queue.put_nowait(url)

            # Notify the work_queue that the "work item" has been processed.
            work_queue.task_done()

    async def _crawl(self):
        # Create a queue that we will use to store our "workload".
        work_queue = asyncio.Queue()
        work_queue.put_nowait(self._root_url)
        # Create a queue that we will use to store the found urls.
        result_queue = asyncio.Queue()

        # Create worker tasks to process the queue concurrently.
        tasks = []
        for i in range(_MAX_WORKERS):
            task = asyncio.create_task(
                self.worker(f"worker-{i}", work_queue, result_queue)
            )
            tasks.append(task)

        # Wait until the queue is fully processed.
        await work_queue.join()

        # Cancel our worker tasks.
        for task in tasks:
            task.cancel()

        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*tasks, return_exceptions=True)

        result_urls = sorted(result_queue._queue)
        for url in result_urls:
            print(url)

    def crawl(self):
        asyncio.run(self._crawl())
