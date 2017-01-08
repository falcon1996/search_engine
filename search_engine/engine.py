
import requests
from bs4 import BeautifulSoup
##########################################################
# crawling and indexing part

seed_page = ''             #enter seed page
search_key = ''            #enter keyword

def crawl_web(seed):        # returns index, graph of inlinks
    tocrawl = [seed]
    crawled = []
    graph = {}
    index = {}
    while tocrawl:
        page = tocrawl.pop()
        if page not in crawled:
            content = get_page(page)
            add_page_to_index(index, page, content)
            outlinks = get_all_links(content)
            graph[page] = outlinks
            union(tocrawl, outlinks)
            crawled.append(page)
    return index,graph

def get_page(url):
    try:
        r = requests.get(url)
        soup = str(BeautifulSoup(r.content))
        return soup
    except:
        return ""


def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1:
        return None, 0
    else:
        start_quote = page.find('"', start_link)
        end_quote = page.find('"', start_quote + 1)
        url = page[start_quote + 1:end_quote]
        return url, end_quote

def get_all_links(page):
    links = []
    while True:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links

def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)

def add_page_to_index(index, url, content):
    list_of_content = content.split()
    for word in list_of_content:
        add_to_index(index, word, url)

def add_to_index(index, keyword, url):
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]

#################################################################################
# searching and ranking part

def lookup(index,keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None

def compute_ranks(graph):
    d = 0.8                                  # damping factor
    numloops = 10

    ranks = {}
    npages = len(graph)                      #length of corpus
    for page in graph:
        ranks[page] = 1.0 / npages           #initializing each page rank

    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    newrank = newrank + d * (ranks[node] / len(graph[node]))
            newranks[page] = newrank
        ranks = newranks
    return ranks

def best_page(index, ranks, keyword):
    page_rank = []
    lis = lookup(index, keyword)
    if lis:
        for url in lis:
            page_rank.append(ranks[url])

        finalurl = max(page_rank)
        pos = page_rank.index(finalurl)
        return lis[pos]
    else:
        return None





index,graph=crawl_web(seed_page)
ranks = compute_ranks(graph)

print best_page(index, ranks, search_key)