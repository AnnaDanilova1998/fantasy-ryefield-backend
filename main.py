import logging

from requests.auth import HTTPBasicAuth
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
import requests


class BaseHandler(RequestHandler):
    def set_default_headers(self):
        print('set headers')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, Access-Control-Allow-Origin, Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')

    @property
    def token(self):
        return self.get_query_argument('token')

    @property
    def session_id(self):
        return self.request.headers.get('Session-Id')

    @property
    def map_id(self):
        return self.get_query_argument('mapId')

    @property
    def node_id(self):
        return self.get_query_argument('nodeId')

    @property
    def user_id(self):
        return self.get_query_argument('userId')

    @property
    def user_token(self):
        return self.request.headers['Rf-Extension-Token']

    def get(self, *args, **kwargs):
        self.finish('I\'m alive!')

    def post(self, *args, **kwargs):
        self.finish({
            'message': 'I\'m alive!',
        })

    def options(self):
        self.finish('I\'m ok')


class OpenUrlCommandHandler(BaseHandler):
    async def post(self):
        await self.finish({
            'url': {
                'url': "http://localhost:3000?token=" + self.user_token + "&mapid=" + self.map_id + "&nodeid=" + self.node_id
            }
        })

class MapsHandler(BaseHandler):
    async def get(self):
        URL = "https://app.redforester.com/api/maps/" + self.map_id + "/nodes"
        auth = ("extension", self.token)
        headers = {
            'Content-Type': "application/json"
        }
        r = requests.get(url=URL, auth=auth, headers=headers)
        data = r.json()
        await self.finish({'data': data})


class UserHandler(BaseHandler):
    async def get(self):
        URL = "https://app.redforester.com/api/maps/" + self.map_id + "/users"
        auth = ("extension", self.token)
        headers = {
            'Content-Type': "application/json"
        }
        r = requests.get(url=URL, auth=auth, headers=headers)
        data = r.json()
        await self.finish({'data': data})


class CurrentUserHandler(BaseHandler):
    async def get(self):
        URL = "https://app.redforester.com/api/user"
        auth = ("extension", self.token)
        headers = {
            'Content-Type': "application/json"
        }
        r = requests.get(url=URL, auth=auth, headers=headers)
        data = r.json()
        await self.finish({'data': data})


class NewNodeHandler(BaseHandler):
    async def post(self):
        URL = "https://app.redforester.com/api/nodes"
        auth = ("extension", self.token)
        headers = {
            'Content-Type': "application/json"
        }
        data = self.request.body
        print(data)
        r = requests.post(url=URL, auth=auth, headers=headers, data=data)
        print(r.json())
        await self.finish({})


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG
    )

    # init tornado handlers
    app = Application([
        (r'/', BaseHandler),
        (r'/api/is-alive', BaseHandler),
        (r'/api/get-maps', MapsHandler),
        (r'/api/get-users', UserHandler),
        (r'/api/get-current-user', CurrentUserHandler),
        (r'/api/new-node', NewNodeHandler),
        # CMDs
        (r'/api/commands/url', OpenUrlCommandHandler)
    ])

    app.listen(8000, "0.0.0.0")
    IOLoop.current().start()
