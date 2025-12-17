import aiohttp
import asyncio
from bs4 import BeautifulSoup
from aiohttp import web
import os
import re
import psutil

async def parse_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
    
    titles = []
    total_price = 0
    seen = set()
    
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if 5 < len(text) < 200 and any(x in href for x in ['/catalog/', '/product/', '/item/', '/goods/']):
            if text not in seen:
                titles.append(text)
                seen.add(text)
        
        span = link.find('span')
        if span and any(x in span.get_text().lower() for x in ['руб', '₽', 'price', 'cost']):
            digits = re.findall(r'\d+', span.get_text())
            if digits:
                try:
                    price = float(''.join(digits))
                    if 10 <= price <= 1000000:
                        total_price += price
                except:
                    pass
    
    for h in soup.find_all(['h2', 'h3', 'h4', 'h5']):
        text = h.get_text(strip=True)
        if 5 < len(text) < 200 and text not in seen:
            titles.append(text)
            seen.add(text)
    
    for div in soup.find_all('div', class_=True):
        if any(x in ' '.join(div.get('class', [])).lower() for x in ['product', 'item', 'card', 'goods', 'catalog']):
            name_elem = div.find(['a', 'h2', 'h3', 'h4', 'span']) or div
            text = name_elem.get_text(strip=True)
            if 5 < len(text) < 200 and text not in seen:
                titles.append(text)
                seen.add(text)
    
    for price_elem in soup.find_all(['span', 'div', 'p'], string=re.compile(r'\d+.*руб', re.I)):
        digits = re.findall(r'\d+', price_elem.get_text())
        if digits:
            try:
                price = float(''.join(digits))
                if 10 <= price <= 1000000:
                    total_price += price
            except:
                pass
    
    return titles, total_price

async def handle_parse(request):
    page = int(request.query.get('page', 1))
    url = "https://dental-first.ru/catalog" \
        if page == 1 \
        else f"https://dental-first.ru/catalog?PAGEN_1={page}"
    titles, total_price = await parse_page(url)
    
    with open('async_products.txt', 'a', encoding='utf-8') as f:
        f.write('\n'.join(titles) + '\n')
    
    return web.json_response({
        'products': len(titles),
        'total_price': total_price,
        'titles': titles[:10]
    })

async def handle_stats(request):
    process = psutil.Process(os.getpid())
    return web.json_response({
        'memory_mb': round(process.memory_info().rss / 1024 / 1024, 2),
        'tasks': len(asyncio.all_tasks())
    })

if __name__ == '__main__':
    if os.path.exists('async_products.txt'):
        os.remove('async_products.txt')
    app = web.Application()
    app.router.add_get('/parse', handle_parse)
    app.router.add_get('/stats', handle_stats)
    print(f"Асинхронный сервер запущен")
    web.run_app(app, port=8001)
