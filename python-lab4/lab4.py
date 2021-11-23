import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import requests
from tkinter import Tk, simpledialog
import re

regex = re.compile(r"http(|s)://.+/(?=\w)")
plt.figure(figsize=(15, 10))

Tk().withdraw()
START_LINK = simpledialog.askstring("Input", "Insert the link to process!")
matcher = regex.search(START_LINK)
START_LINK = START_LINK if matcher is None else matcher.group()
D = 0.5
FROM_TO_LINKS = []


def find_inner_links(url):
    for a_link in FROM_TO_LINKS:
        if url == a_link[0]:
            return
    resp = requests.get(url)
    http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
    html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
    encoding = html_encoding or http_encoding
    soup = BeautifulSoup(resp.content, 'html.parser', from_encoding=encoding)
    all_links = []
    for lnk in soup.find_all('a', href=True):
        full_link = START_LINK[:-1] + lnk['href']
        if "http" not in lnk['href'] and lnk['href'].startswith("/") and full_link != url:
            all_links.append(full_link)
    if len(all_links) == 0:
        return
    for lnk in all_links:
        FROM_TO_LINKS.append((url, lnk))
        find_inner_links(lnk)


find_inner_links(START_LINK)
G = nx.DiGraph()
unique = list(set(FROM_TO_LINKS))
G.add_edges_from(unique)
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, node_size=500)
nx.draw_networkx_edges(G, pos, edgelist=G.edges, edge_color='black')
nx.draw_networkx_labels(G, pos)
plt.show()

pages = {}
for link in unique:
    pages[link[0]] = pages.get(link[0], 0) + 1

pages_list = list(pages)
ranks = np.full(len(pages_list), 1)
array = np.zeros(len(ranks))

for i in range(100):
    if i > 0:
        ranks = array
    for y in range(len(ranks)):
        inner_sum = 0
        for page in pages_list:
            if (page, pages_list[y]) in unique:
                inner_sum += ranks[pages_list.index(page)] / pages.get(page)
        array[y] = (1 - D) + D * inner_sum

res = []
for i in range(len(ranks)):
    res.append([pages_list[i], ranks[i]])

res = sorted(res, key=lambda x: x[1], reverse=True)[:10]

for a in res:
    print(a)
