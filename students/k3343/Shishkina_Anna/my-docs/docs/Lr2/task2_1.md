# Задание 2 

Потоки. Процессы. Асинхронность.

## Задача 1

Различия между threading, multiprocessing и async в Python

```python
def partial_sum(start, end, results, index):
    results[index] = sum(range(start, end))
```

1) threading
Каждый поток считает свою часть сумму
Threading result: 500000000500000000
Time: 12.77 seconds

2) multiprocessing
Используются отдельные процессы с независимой памятью 
Multiprocessing result: 500000000500000000
Time: 5.44 seconds

3) async 
Один поток переключается между задачами 
Async result: 500000000500000000
Time: 12.74 seconds

Вывод: Multiprocessing затратил наименьшее количество времени на выполнение задачи благодаря тому, что каждый процесс имеет независимую память, ограничение GIL обходится. 
