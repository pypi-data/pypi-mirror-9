import sys

from howdoi.howdoi import command_line_runner
sys.argv.append("python fib")
command_line_runner()

sys.exit()
import requests
import requests_cache
import random

USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
               'Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',)

requests_cache.install_cache('howdoi')
requests.get(url='https://www.google.com/search?q=site:stackoverflow.com%20open%20browser',
             headers={'User-Agent': random.choice(USER_AGENTS)})