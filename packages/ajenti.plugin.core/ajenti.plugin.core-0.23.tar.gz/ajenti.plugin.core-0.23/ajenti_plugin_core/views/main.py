import gevent
import json
import logging
import subprocess

import aj
from aj.api import *
from aj.api.http import url, HttpPlugin
from aj.plugins import PluginManager, DirectoryPluginProvider

from aj.plugins.core.api.endpoint import endpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url('/')
    @endpoint(page=True, auth=False)
    def handle_root(self, http_context):
        if self.context.identity:
            return http_context.redirect('/view/')
        else:
            return http_context.redirect('/view/login/normal')

    @url('/view/.*')
    @endpoint(page=True, auth=False)
    def handle_view(self, http_context):
        if aj.dev:
            rebuild_all = http_context.env.get('HTTP_CACHE_CONTROL', None) == 'no-cache'

            for provider in aj.plugin_providers:
                if isinstance(provider, DirectoryPluginProvider):
                    logging.debug('Building resources in %s', provider.path)
                    if rebuild_all:
                        cmd = ['ajenti-dev-multitool', '--rebuild']
                    else:
                        cmd = ['ajenti-dev-multitool', '--build']
                    p = subprocess.Popen(
                        cmd,
                        cwd=provider.path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    o, e = p.communicate()
                    if p.returncode != 0:
                        logging.error('Resource compilation failed')
                        logging.error(o + e)

        path = PluginManager.get(aj.context).get_content_path('core', 'content/pages/index.html')
        content = open(path).read() % {
            'prefix': http_context.prefix,
            'plugins': json.dumps(
                dict((k, v.title) for k, v in PluginManager.get(aj.context).get_all().iteritems())
            ),
            'version': aj.version,
            'platform': aj.platform,
            'platformUnmapped': aj.platform_unmapped,
        }
        http_context.add_header('Content-Type', 'text/html')
        http_context.respond_ok()
        return content


#TODO remove
from aj.plugins.core.api.tasks import Task


class MyTask(Task):
    name = 'Test'

    def __init__(self, context, *args, **kwargs):
        print args, kwargs
        Task.__init__(self, context)

    def run(self):
        logging.info('Running')
        gevent.sleep(2)
        for i in range(0, 5):
            gevent.sleep(1)
            self.report_progress(message='Working', done=i, total=10)
        logging.info('Done')
