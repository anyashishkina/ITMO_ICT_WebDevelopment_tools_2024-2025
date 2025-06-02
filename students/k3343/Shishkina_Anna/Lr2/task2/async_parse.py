import asyncio
import aiohttp
from bs4 import BeautifulSoup
from db import init_db, save_category
import re

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

async def fetch(session, url):
    async with session.get(url, headers=headers) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script')
        category_name = None

        for script in scripts:
            if script.string and 'categoryName' in script.string:
                match = re.search(r'categoryName:\s*"([^"]+)"', script.string)
                if match:
                    category_name = match.group(1)
                    break

        if category_name:
            save_category(category_name)
        else:
            print("Категория не найдена")

async def main():
    init_db()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    import time
    start = time.time()
    asyncio.run(main())
    print(f"Asyncio время выполнения: {time.time() - start:.2f} сек")
