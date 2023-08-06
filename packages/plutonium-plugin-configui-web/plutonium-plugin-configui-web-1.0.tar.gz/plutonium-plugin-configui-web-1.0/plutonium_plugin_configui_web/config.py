
import os
import json
import re
from http_handler import VirtualRequestHandlerBase, HTTPResponse
from plutonium.modules.tools import Storage

import pkg_resources

class ConfigHandler(VirtualRequestHandlerBase):
    def __init__(self, lang_path, config):
        self.config = config
        self.lang_path = lang_path

    def get_languages(self):
        langs = {}
        for file in os.listdir(self.lang_path):
            matches = re.match('([a-z]{2})\.json', file)
            if not matches:
                continue
            lang_data = json.loads(open(os.path.join(self.lang_path, file)).read())
            langs[matches.group(1)] = lang_data['desc']
        return langs

    def handle(self, request):
        self.config.languages = self.get_languages()

        self.config.versions = Storage(
            plutonium = pkg_resources.get_distribution('plutonium').version,
            webui = pkg_resources.get_distribution('plutonium-plugin-configui-web').version
        )

        return HTTPResponse('var config = %s' % json.dumps(self.config), 200)
