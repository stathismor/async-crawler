#!/usr/bin/env python

import sys
from crawler import Crawler


if __name__ == "__main__":
    crawler = Crawler(sys.argv[1])
    crawler.crawl()
