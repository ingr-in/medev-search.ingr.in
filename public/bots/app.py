import requests
import time
import random
import tldextract
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
from queue import Queue
from threading import Thread
from flask import Flask, request, jsonify

# 🔧 CONFIG
BASE_DOMAIN = "domain.com"
MAX_THREADS = 5
MAX_URLS = 50
TOR_PROXY = "socks5h://127.0.0.1:9050"

visited = set()
queue = Queue()
results = []

app = Flask(__name__)

# 🔁 Tor IP change
def change_ip():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            time.sleep(5)
    except:
        pass

# 🎯 Random Referer
def get_random_referer():
    if not visited:
        return None
    return random.choice(list(visited))

# 🌐 Fetch
def fetch(url):
    try:
        headers = {
            "User-Agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
                "Mozilla/5.0 (X11; Linux x86_64) Chrome/118.0"
            ]),
            "Accept": "text/html",
        }

        ref = get_random_referer()
        if ref:
            headers["Referer"] = ref

        proxies = {
            "http": TOR_PROXY,
            "https": TOR_PROXY
        }

        res = requests.get(url, headers=headers, proxies=proxies, timeout=10)

        return res.text

    except:
        return None

# 🔍 Extract links
def extract_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for tag in soup.find_all("a", href=True):
        href = tag["href"]

        if not href.startswith("http"):
            continue

        ext = tldextract.extract(href)
        domain = ext.domain + "." + ext.suffix

        if domain == BASE_DOMAIN:
            links.add(href)

    return links

# 👷 Worker
def worker():
    while True:
        url = queue.get()

        if url in visited or len(visited) >= MAX_URLS:
            queue.task_done()
            continue

        visited.add(url)

        html = fetch(url)

        if html:
            links = extract_links(html)

            results.append({
                "url": url,
                "links_found": len(links)
            })

            for link in links:
                if link not in visited:
                    queue.put(link)

        # ⏱ Random delay
        time.sleep(random.randint(10, 30))

        # 🔁 Change IP
        if len(visited) % 5 == 0:
            change_ip()

        queue.task_done()

# 🚀 Start crawl
def start_crawl():
    visited.clear()
    results.clear()

    queue.put("https://" + BASE_DOMAIN)

    threads = []
    for _ in range(MAX_THREADS):
        t = Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)

    queue.join()

# 🌐 API route
@app.route("/")
def home():
    mode = request.args.get("req")

    if mode == "json":
        start_crawl()
        return jsonify({
            "status": "success",
            "total": len(results),
            "data": results
        })

    return "Crawler Running"

# ▶️ Run server
if __name__ == "__main__":
    app.run(port=5000)
