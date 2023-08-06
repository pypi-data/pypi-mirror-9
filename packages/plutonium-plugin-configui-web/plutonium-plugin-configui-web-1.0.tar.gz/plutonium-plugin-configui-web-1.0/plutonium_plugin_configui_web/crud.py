import sys
import json

from http_handler import VirtualRequestHandlerBase, HTTPResponse

from sqlchemyforms.exceptions import CrudException
from sqlchemyforms.crud_base import CrudBase, CrudRequest
from sqlchemyforms.tools import JSONEncoder

from plutonium.modules.logger import get_logger
logger = get_logger(__name__, 'plutonium')

class CRUD(CrudBase, VirtualRequestHandlerBase):
    def __init__(self, model, db_mgr):
        CrudBase.__init__(self, model)
        self.db_mgr = db_mgr

    def handle(self, request):
        path_parts = request.path.split('/')
        command = 'list'
        if len(path_parts) > 3 and len(path_parts[3]) > 0:
            command = path_parts[3]

        command = 'do_%s' % command

        if not hasattr(self, command):
            return HTTPResponse('Undefined CRUD controller', 404)

        try:
            with self.db_mgr.create_session() as session:
                creq = CrudRequest(request.path, request.get_vars, request.post_vars, request.query, session)
                res = self.call(creq, command)

                code = 200

                try:
                    session.commit()
                except Exception as e:
                    logger.exception(e)
                    res.success = False

                try:
                    content = json.dumps(res, cls = JSONEncoder)
                except Exception as e:
                    content = ''
                    logger.exception(e)
                    code = 500

                response = HTTPResponse(content, code)

        except CrudException as e:
            response = HTTPResponse(e.message, e.code)

        return response
