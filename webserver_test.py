import time
import aiohttp
import asyncio
import cProfile
import pstats
from concurrent.futures import ProcessPoolExecutor

from aio.aioserver import main

async def get_page(index):
    url = 'http://www.baidu.com'
    async with aiohttp.ClientSession() as session:
        print('get:',index)
        response = await session.get(url)
        # print(response.status)
        if response.status == 200:
            html = await response.text()
            print('{} recv: {}'.format(index, html))

def test():        
    tasks = [asyncio.ensure_future(get_page(i)) for i in range(100)]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

def run_client():
    cProfile.run('test()', 'profile_server.txt', sort='time')
    p = pstats.Stats('profile.txt')
    p.sort_stats('time').print_stats()

def run_server():
    main()

def run_test():
    pool = ProcessPoolExecutor()
    task0 = pool.submit(run_server)  
    task1 = pool.submit(run_client)

if __name__ == "__main__":
    run_test()
    
