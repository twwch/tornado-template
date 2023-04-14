from common.handler import BaseHandler


class StateHandler(BaseHandler):
    def get(self):
        self.response_json(200, 'server is running')
