import sys
import json

from http_handler import VirtualRequestHandlerBase, HTTPResponse

from sqlchemyforms.exceptions import CrudException
from sqlchemyforms.crud_base import CrudBase, CrudRequest
from sqlchemyforms.tools import JSONEncoder

from plutonium.modules.logger import get_logger
logger = get_logger(__name__, 'plutonium')

class CRUD(CrudBase, VirtualRequestHandlerBase):
    def __init__(self, model, plutonium):
        CrudBase.__init__(self, model)
        self.plutonium = plutonium
        self.session = self.plutonium.orm_manager.create_session()

    def handle(self, request):
        path_parts = request.path.split('/')
        command = 'list'
        if len(path_parts) > 3 and len(path_parts[3]) > 0:
            command = path_parts[3]

        command = 'do_%s' % command

        if not hasattr(self, command):
            return HTTPResponse('Undefined CRUD controller', 404)

        changes = 0

        try:
            res = {}
            code = 200

            with self.plutonium.orm_manager.lock:
                creq = CrudRequest(request.path, request.get_vars, request.post_vars, request.query, self.session)
                res = self.call(creq, command)

                try:
                    changes = len(self.session.deleted) + len(self.session.new) + len(self.session.dirty)
                    logger.debug("%d changes on command %s" % (changes, command))
                    if changes:
                        self.session.commit()
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

        if changes:
            logger.info("Reloading fetcher due database changes")
            self.plutonium.fetcher.reload()

        return response
