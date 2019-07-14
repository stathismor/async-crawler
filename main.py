from crawler import Crawler

_MONZO_URL = "https://github.com/"

if __name__ == "__main__":
    crawler = Crawler(_MONZO_URL)
    crawler.crawl()
