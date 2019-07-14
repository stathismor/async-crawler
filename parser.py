from urllib.parse import urlsplit
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, html, url, subdomain):
        self._html = html
        self._url = url
        self._subdomain = subdomain

    def get_urls(self):
        # Extract base url to resolve relative links
        local_urls = set()
        split_result = urlsplit(self._url)
        base = split_result.netloc
        strip_base = base.replace("www.", "")
        base_url = f"{split_result.scheme}://{base}"
        path = (
            self._url[: self._url.rfind("/") + 1]
            if "/" in split_result.path
            else self._url
        )

        soup = BeautifulSoup(self._html, "html.parser")

        for link in soup.find_all("a"):
            anchor = link.attrs["href"] if "href" in link.attrs else ""

            if anchor.startswith("/"):
                local_link = base_url + anchor

                local_urls.add(local_link)
            elif strip_base in anchor or anchor.startswith("/"):

                anchor_split_result = urlsplit(anchor)
                anchor_base = anchor_split_result.netloc

                # Only add links from the subdomain
                if anchor_base == self._subdomain:
                    local_urls.add(anchor)

            elif not anchor.startswith("http"):
                local_link = path + anchor
                local_urls.add(local_link)

        return local_urls
