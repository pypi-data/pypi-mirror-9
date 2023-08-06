
import os
import json
from http_handler import VirtualRequestHandlerBase, HTTPResponse

class LanguageHandler(VirtualRequestHandlerBase):
    def __init__(self, lang_path, cookie_key):
        self.lang_path = lang_path
        self.cookie_key = cookie_key

    def handle(self, request):
        if 'code' in request.get_vars:
            code = request.get_vars['code'][0]
        elif self.cookie_key in request.cookies:
            code = request.cookies[self.cookie_key]
        else:
            code = 'en' # move out from here

        lang_file = os.path.join(self.lang_path, '%s.json' % code)
        if not os.path.isfile(lang_file):
            return HTTPResponse('Language file not found %s' % lang_file, 404)

        content = ''
        with open(lang_file) as f:
            content = f.read()

        if 'code' in request.get_vars:
            try:
                lang_data = json.loads(content)
            except Exception as e:
                return HTTPResponse('Language file cannot be parsed. %s' % e, 500)
            return HTTPResponse(json.dumps(lang_data), 200)
        else:
            return HTTPResponse('var lang_data = %s' % content, 200)


