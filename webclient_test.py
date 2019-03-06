import cProfile
import pstats

from aio.scheduler import Scheduler
from aio.aioclient import HttpClient

sched = Scheduler()

url = 'http://www.baidu.com'

def run():
    for i in range(500):
        cli = HttpClient()
        sched.new(cli.get(url))

    sched.run()

if __name__ == "__main__":
    cProfile.run('run()', 'profile_client.txt', sort='time')
    p = pstats.Stats('profile_client.txt')
    p.sort_stats('time').print_stats()