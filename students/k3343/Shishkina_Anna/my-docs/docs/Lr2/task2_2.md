# Задание 2 
Потоки. Процессы. Асинхронность.

## Задача 2 
Параллельный парсинг веб-страниц с сохранением в базу данных

URL для парсинга 
```python 
urls = [
    "https://www.bork.ru/eShop/kitchen/",
    "https://www.bork.ru/eShop/Home/",
    "https://www.bork.ru/eShop/Beauty/",
    "https://www.bork.ru/eShop/Outdoor/"
]
```

Парсер извлекает со страниц категорию товаров и записывает в таблицу Category

```python 
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
```
Время выполнения программ  

| threading | multiprocessing | async |
|----------|----------|----------|
| 1.96    | 1.76   | 0.93   |

Вывод: быстрее всех отработал async, так как задача состоит в обработке сетевых запросов, а данных вид задач идеально подходит для async программ. Async освобождает поток во время ожидания ответа от сервера, позволяя обрабатывать другие задачи. В I/O операциях GIL освобождается и не мешает работе программы.
