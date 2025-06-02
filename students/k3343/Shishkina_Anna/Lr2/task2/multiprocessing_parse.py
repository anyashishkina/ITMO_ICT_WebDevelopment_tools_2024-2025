import re
from multiprocessing import Process
import requests
from bs4 import BeautifulSoup
from db import init_db, save_category

urls = [
    "https://www.bork.ru/eShop/kitchen/",
    "https://www.bork.ru/eShop/Home/",
    "https://www.bork.ru/eShop/Beauty/",
    "https://www.bork.ru/eShop/Outdoor/"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/121.0.0.0 Safari/537.36"
}

def parse_and_save(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.find_all('script')
    category_name = None

    for script in scripts:
        if script.string and 'categoryName' in script.string:
            match = re.search(r'categoryName:\s*"([^"]+)"', script.string)
            if match:
                category_name = match.group(1)
    save_category(category_name)

def main():
    init_db()
    processes = []
    for url in urls:
        p = Process(target=parse_and_save, args=(url,))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

if __name__ == "__main__":
    import time
    start = time.time()
    main()
    print(f"Multiprocessing время выполнения: {time.time() - start:.2f} сек")
