# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
from datetime import datetime
import urllib.parse


def crawl(keyword, min_res_count=None, bbs=None):
    query = {
        "q": keyword,
    }
    if min_res_count is not None:
        query["sr"] = min_res_count
    if bbs is not None:
        query["bbs"] = bbs

    def _url(page):
        query["p"] = page
        return "http://www.logsoku.com/search?" + urllib.parse.urlencode(query)

    for p in range(1, 100):
        d = pq(url=_url(p))
        if len(d("#search_result_threads .search_not_found")) > 0:
            break
        for d in map(pq, d("#search_result_threads table tbody tr")):
            yield {
                "bbs": d("td.bbs").text(),
                "res_count": int(d("td.length").text()),
                "title": d("td.title").text().replace("[転載禁止]©2ch.net", ""),
                "date": datetime.strptime(d("td.date").text(), "%Y-%m-%d %H:%M"),
                "ikioi": int(d("td.ikioi").text()),
            }

if __name__ == '__main__':
    for t in crawl("rwby"):
        print(t)