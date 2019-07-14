import pytest
from unittest.mock import Mock

from crawler import Crawler

# Bodies of various nodes, that are linked as:
#          root
#          /  \
#    link_a    link_b
#       |       /  \
#    link_c  link_c link_e
#       |      |
#    link_d  link_d
#       |      |
#    link_x  link_x
_BODY_MAPPER = {
    "root": (
        "<title>Root page</title>"
        "<ul>"
        "  <li><a href='https://test.com/link_a'</a></li>"
        "  <li><a href='https://test.com/link_b'</a></li>"
        "</ul>"
    ),
    "link_a": "<title>Page A</title><a href='https://test.com/link_c'</a>",
    "link_b": (
        "<title>Page B</title>"
        "<ul>"
        "  <li><a href='https://test.com/link_c'</a></li>"
        "  <li><a href='https://test.com/link_e'</a></li>"
        "</ul>"
        "</a>"
    ),
    "link_c": "<title>Page C</title><a href='https://test.com/link_d'</a>",
    "link_d": "<title>Page D</title><a href='https://another.domain.test.com/link_x'</a>",
}
_TEST_URL = "https://test.com/"


class AsyncMock:
    def __init__(self, path: str):
        self._path = path

    async def __aenter__(self):
        return self

    async def __aexit__(self, *error_info):
        return self

    async def text(self):
        mock = Mock(side_effect=self._side_effect)
        return mock()

    def _side_effect(self):
        """
        Return the corresponding body of each link. For instance, if a http://link_a
        is requested, the body that contains that link is returned. Tries to imitate
        what a real-life request would do for the pages put in _BODY_MAPPER
        """
        for link in _BODY_MAPPER.keys():
            if link in self._path:
                return _BODY_MAPPER[link]

        return _BODY_MAPPER["root"]


def mock_client_get(self, auth_path, timeout=20):
    mock_response = AsyncMock(auth_path)
    mock_response.status = 200
    return mock_response


@pytest.mark.asyncio
async def test_crawl(monkeypatch):
    monkeypatch.setattr("crawler.aiohttp.ClientSession.get", mock_client_get)

    crawler = Crawler(_TEST_URL)
    result = await crawler._crawl()

    print(result)
    assert result == [
        "https://test.com/link_a",
        "https://test.com/link_b",
        "https://test.com/link_c",
        "https://test.com/link_d",
        "https://test.com/link_e",
    ]
