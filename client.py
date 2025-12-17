import requests
import time

def test_server(pages, port, name):
    print(f"Тест {name}:")
    start = time.time()
    total_price = 0
    
    for page in pages:
        try:
            response = requests.get(f"http://127.0.0.1:{port}/parse?page={page}", timeout=30)
            if response.status_code == 200:
                data = response.json()
                total_price += data.get('total_price', 0)
                print(f"Страница {page}: {data.get('products', 0)} товаров")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    duration = time.time() - start
    
    memory_mb = 0
    try:
        stats = requests.get(f"http://127.0.0.1:{port}/stats", timeout=5).json()
        memory_mb = stats.get('memory_mb', 0)
        print(f"Память: {memory_mb} MB")
    except:
        pass
    
    print(f"Время: {duration:.2f} сек")
    print(f"Общая стоимость: {total_price:.2f} руб.\n")
    return duration, total_price, memory_mb

if __name__ == '__main__':

    pages = [1, 2, 3]
    thread_time, thread_price, thread_memory = test_server(pages, 8000, "многопоточного сервера")
    time.sleep(1)
    async_time, async_price, async_memory = test_server(pages, 8001, "асинхронного сервера")
    
    print("=" * 40)
    print("СРАВНЕНИЕ:")
    print(f"Многопоточный: {thread_time:.2f} сек, {thread_price:.2f} руб., {thread_memory} MB")
    print(f"Асинхронный: {async_time:.2f} сек, {async_price:.2f} руб., {async_memory} MB")
    print(f"Разница по времени: {thread_time - async_time:.2f} сек")
    if thread_memory > 0 and async_memory > 0:
        print(f"Разница по памяти: {thread_memory - async_memory:.2f} MB")
