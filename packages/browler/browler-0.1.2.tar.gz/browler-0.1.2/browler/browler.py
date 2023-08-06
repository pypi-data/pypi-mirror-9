from .page import Page
import os
from urlparse import urlparse
import multiprocessing
import redis
import time
import sys
import logging
from splinter import Browser


class Queue(object):
    pass


class RedisQueue(Queue):

    def __init__(self, client):
        self.client = client
        job = 'today'
        self.queue_key = '%s.queue' % job
        self.visited_key = '%s.visited' % job

    def add(self, *links):
        self.client.sadd(self.queue_key, *links)

    def next(self):
        url = self.client.spop(self.queue_key)
        if not url:
            return
        while self.client.sismember(self.visited_key, url):
            url = self.client.spop(self.queue_key)
            if not url:
                return
        return url

    def visited(self, link):
        self.client.sadd(self.visited_key, link)

    def cleanup(self):
        self.client.delete(self.queue_key)
        self.client.delete(self.visited_key)


class Context(object):
    pass


class Worker(multiprocessing.Process):

    def __init__(self, crawler):
        multiprocessing.Process.__init__(self)
        self.crawler = crawler
        self._elasped_wait_time = 0

    def run(self):

        if self.crawler.config['browser'] == 'remote':
            config = self.crawler.config['remote']
            browser = Browser(driver_name='remote',
                              url=config.get('url'),
                              browser=config.get('browser', 'firefox')
                              )
        else:
            browser = Browser(self.crawler.config['browser'])

        visits = 0
        max_visits = self.crawler.limit
        while True:
            url = self.crawler.queue.next()
            if not url:
                self.wait()
                if self.expired():
                    break
                continue
            self.clear_elapsed_time()
            try:
                page = Page(self.crawler, browser)
                page.url = url
                browser.visit(url)
                self.crawler.queue.visited(page.url)
                page.visited = browser.url
                self.crawler.queue.visited(page.visited)
                for script in self.crawler.scripts:
                    browser.driver.execute_script(script)
                # add actual visited url to prevent redirect visits
                for plugin in self.crawler.plugins:
                    if plugin.match(page):
                        try:
                            plugin.run(page)
                        except Exception as e:
                            # Plugin failed, log message
                            self.crawler.logger.info('%s:plugin:failed:%s:%s', self.name, url, str(e))
                            continue
                if self.crawler.allowed(page.visited):
                    links = page.links()
                    filtered = self.crawler.filter(links)
                    self.crawler.queue.add(*filtered)
            except Exception as e:
                self.crawler.logger.info('%s:failed:%s:%s', self.name, url, str(e))
                continue
            self.crawler.logger.info('%s:visit:%s', self.name, url)
            visits += 1
            if visits >= max_visits:
                break
        browser.quit()

    def clear_elapsed_time(self):
        self._elasped_wait_time = 0

    def wait(self):
        if not self._elasped_wait_time:
            self._elasped_wait_time = 0
        time.sleep(1)
        self._elasped_wait_time += 1

    def expired(self):
        return self._elasped_wait_time >= 30


class Browler(object):

    def __init__(self, config):
        self.url = config['url']
        self.limit = config.get('limit', 0)
        self.plugins = config.get('plugins', list())
        self.visited = config.get('visited', set())
        self.links = config.get('links', set())
        self.filters = config.get('filters', list())
        self.hostname = urlparse(self.url).hostname
        self.processes = config.get('processes', 1)
        self.config = config
        self._scripts = []
        self.queue = None
        self.lock = None
        self.logger = None

    @property
    def scripts(self):
        if self._scripts:
            return self._scripts
        location = os.path.dirname(__file__)
        with open(os.path.join(location, 'qe.js'), 'r') as f:
            self._scripts.append(f.read())
        return self._scripts

    def crawl(self):
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        lock = multiprocessing.Lock()
        client = redis.Redis(host='localhost')
        queue = RedisQueue(client)
        queue.add(self.url)
        self.logger = logging
        self.lock = lock
        self.queue = queue
        for plugin in self.plugins:
            context = Context()
            context.crawler = self
            plugin.startup(context)

        workers = [Worker(self) for _ in range(self.processes)]
        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()
        queue.cleanup()

    def allowed(self, url):
        parsed_url = urlparse(url)
        return parsed_url.hostname == self.hostname and not filter(lambda item: item.search(parsed_url.path) and item.search(parsed_url.path).group(0), self.filters)

    def filter(self, links):
        filtered = set()
        for url in links:
            if self.allowed(url):
                filtered.add(url)
        return filtered