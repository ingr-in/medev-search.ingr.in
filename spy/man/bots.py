from flask import Blueprint, request, jsonify
from threading import Thread
from queue import Queue
import requests
import time
import random
import tldextract
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
import xml.etree.ElementTree as ET

bots = Blueprint("bots", __name__)

# 🔧 CONFIG
BASE_DOMAIN = "ingr.in"
MAX_THREADS = 5
MAX_URLS = 100
TOR_PROXY = "socks5h://127.0.0.1:9050"

visited = set()
queue = Queue()
results = []

status = {
    "running": False,
    "total": 0,
    "mode": "idle"
}

# 🔁 Tor IP change
def change_ip():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            time.sleep(5)
    except:
        print("Tor change failed")

# 🎯 Random Referer
def get_random_referer():
    if not visited:
        return None
    return random.choice(list(visited))

# 🌐 Fetch (Proxy + fallback)
def fetch(url):
    headers = {
        "User-Agent": random.choice([
            "suru/1.0 Mozilla/5.0 Chrome/120.0",
            "suru/1.0 Mozilla/5.0 Chrome/118.0"
        ]),
        "Accept": "text/html",
    }

    ref = get_random_referer()
    if ref:
        headers["Referer"] = ref

    # 👉 Try proxy
    try:
        proxies = {
            "http": TOR_PROXY,
            "https": TOR_PROXY
        }
        res = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        return res.text
    except:
        print("Proxy failed → direct")

        # 👉 fallback direct
        try:
            res = requests.get(url, headers=headers, timeout=10)
            return res.text
        except:
            return None

# 🔍 Extract links (HTML)
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

# 🗺️ Sitemap parser
def parse_sitemap(xml_data):
    urls = set()
    try:
        root = ET.fromstring(xml_data)

        for loc in root.iter():
            if "loc" in loc.tag:
                urls.add(loc.text.strip())

    except:
        pass

    return urls

# 🔍 Find sitemap URLs
def get_sitemap_urls():
    sitemap_urls = set()

    possible = [
        f"https://{BASE_DOMAIN}/sitemap.xml",
        f"https://sitemaps.{BASE_DOMAIN}",
        f"https://sitemaps.{BASE_DOMAIN}/?sr=xml ",
        f"https://{BASE_DOMAIN}/sitemap.php?sr=xml"
    ]

    for sm in possible:
        data = fetch(sm)

        if data:
            print("Sitemap found:", sm)
            urls = parse_sitemap(data)
            sitemap_urls.update(urls)

    return sitemap_urls

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

            status["total"] = len(results)

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

    status["running"] = True
    status["total"] = 0

    while not queue.empty():
        queue.get()

    # 🔥 STEP 1: Try sitemap
    sitemap_links = get_sitemap_urls()

    if sitemap_links:
        status["mode"] = "sitemap"
        print("Using sitemap URLs")

        for link in sitemap_links:
            queue.put(link)
    else:
        # 🔥 STEP 2: fallback normal crawl
        status["mode"] = "normal"
        print("No sitemap → normal crawl")

        queue.put(f"https://{BASE_DOMAIN}")

    # 🔁 Threads start
    for _ in range(MAX_THREADS):
        t = Thread(target=worker, daemon=True)
        t.start()

    queue.join()

    status["running"] = False

######Output######

@bots.route("/bots")
def bots_handler():
    mode = request.args.get("sr")

    # ▶️ Start crawl (non-blocking)
    if mode == "start":
        Thread(target=start_crawl).start()
        return jsonify({"status": "started"})

    # 📊 Live status
    elif mode == "status":
        return jsonify({
            "running": status["running"],
            "mode": status["mode"],
            "total": status["total"],
            "data": results
        })

    # 🔁 Full blocking crawl + JSON
    elif mode == "json":
        start_crawl()
        return jsonify({
            "status": "completed",
            "total": len(results),
            "data": results
        })

    # 🔹 Default
    return jsonify({
        "message": "use ?sr=start | status | json"
    })
