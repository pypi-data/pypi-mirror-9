import json
import os

import aj
from aj.api import *
from aj.api.http import url, HttpPlugin
from aj.plugins import PluginManager

from aj.plugins.core.api.endpoint import endpoint


@component(HttpPlugin)
class ResourcesHandler(HttpPlugin):
    def __init__(self, http_context):
        self.cache = {}
        self.use_cache = not aj.debug
        self.mgr = PluginManager.get(aj.context)

    @url(r'/resources/all\.(?P<type>.+)')
    @endpoint(page=True, auth=False)
    def handle_build(self, http_context, type=None):
        if self.use_cache and type in self.cache:
            content = self.cache[type]
        else:
            content = ''
            if type in ['js', 'css']:
                for plugin in self.mgr.get_loaded_plugins_list():
                    path = self.mgr.get_content_path(plugin, 'resources/build/all.%s' % type)
                    if os.path.exists(path):
                        content += open(path).read()
            if type == 'init.js':
                ng_modules = []
                for plugin in self.mgr.get_loaded_plugins_list():
                    for resource in self.mgr[plugin].resources:
                        if resource.startswith('ng:'):
                            ng_modules.append(resource.split(':')[-1])
                content = '''
                    window.__ngModules = %s;
                ''' % json.dumps(ng_modules)
            if type == 'partials.js':
                content = '''
                    angular.module("core.templates", []);
                    angular.module("core.templates").run(
                        ["$templateCache", function($templateCache) {
                '''
                for plugin in self.mgr.get_loaded_plugins_list():
                    for resource in self.mgr[plugin].resources:
                        if resource.endswith('.html'):
                            path = self.mgr.get_content_path(plugin, resource)
                            if os.path.exists(path):
                                template = open(path).read()
                                content += '''
                                      $templateCache.put("%s", %s);
                                ''' % (
                                    '%s/%s:%s' % (http_context.prefix, plugin, resource),
                                    json.dumps(template)
                                )
                content += '''
                    }]);
                '''

            self.cache[type] = content

        http_context.add_header('Content-Type', {
            'css': 'text/css',
            'js': 'application/javascript',
            'init.js': 'application/javascript',
            'partials.js': 'application/javascript',
        }[type])
        http_context.respond_ok()
        return http_context.gzip(content=content)

    @url(r'/resources/(?P<plugin>\w+)/(?P<path>.+)')
    @endpoint(page=True, auth=False)
    def handle_file(self, http_context, plugin=None, path=None):
        if '..' in path:
            return http_context.respond_not_found()
        return http_context.file(PluginManager.get(aj.context).get_content_path(plugin, path))
