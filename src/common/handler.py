import re
import json
import traceback
from datetime import datetime
from tornado.web import RequestHandler, RedirectHandler, HTTPError
from tornado.httpclient import HTTPRequest
from .vo import to_json_type
from .const import *

from .utils import encode_multipart_formdata
from config.log import logger, rlogger

XML_CPL = re.compile(r"text/xml.*")
JSON_CPL = re.compile(r"application/json.*")


class CommonBaseHandler(RequestHandler):

    def prepare(self):
        super().prepare()

        logger.debug("request: {}".format((self.request.method, self.request.path, self.request.arguments)))

    def response_json(self, code=CODE_OK, message=None, status_code=200,
                      **kwargs):

        message = message or MESSAGES.get(code, "")
        data = {
            "code": code,
            "message": (message if isinstance(message, str) else
                        json.dumps(message))
        }
        data.update(kwargs)

        self.set_status(status_code)
        ua = self.request.headers.get('User-Agent', "")
        if re.match(r".+\s+MSIE\s+.+", ua):
            self.set_header("Content-Type", "text/html; charset=utf-8")
        else:
            self.set_header("Content-Type", "application/json; charset=utf-8")
        self.finish(json.dumps(to_json_type(data), ensure_ascii=False))

        logger.debug('(test){}'.format(json.dumps(to_json_type(data), ensure_ascii=False)))

    # 以下方法用于proxy
    def get_url(self):
        raise Exception("method not found")

    def set_post_arguments(self, arguments):
        self.__post_arguments = arguments

    def get_post_arguments(self):
        return self.__post_arguments

    def get_formdata_files(self):
        files = []
        for name, l in self.request.files.items():
            for f in l:
                if f:
                    files.append((name, f.filename, f.body))
        return files

    def _get_body(self):
        """
        for proxy handler
        post 请求将参数拼装于body
        """
        if self.request.method == "GET":
            return None, None
        code, msg, url = self.get_url()
        if code != CODE_OK:
            return None, None
        content_type, body = encode_multipart_formdata(self.get_post_arguments(), self.get_formdata_files())
        return content_type, body

    def _get_headers(self):
        """
        for proxy handler
        """
        headers = dict(self.request.headers)
        headers.pop("If-None-Match", None)
        headers.pop("Content-Length", None)
        headers.pop("Pragma", None)
        headers.pop("If-Modified-Since", None)
        # headers.pop("Host", None)
        return headers

    def get_full_body_headers(self):
        content_type, body = self._get_body()
        headers = self._get_headers()
        if content_type:
            headers["Content-Type"] = content_type
        return body, headers

    def get_headers(self):
        return self._get_headers()

    @staticmethod
    def resp_header_fields():
        return ["Date", "Cache-Control", "Server", "Content-Type", "Location", "Content-disposition"]

    def get_request(self, url, **kwargs):
        if "connect_timeout" not in kwargs:
            kwargs["connect_timeout"] = 3
        if "request_timeout" not in kwargs:
            kwargs["request_timeout"] = 3
        if "headers" not in kwargs:
            kwargs["headers"] = self._get_headers()

        kwargs.update({
            "allow_nonstandard_methods": True,
            "follow_redirects": True,
            "max_redirects": 2,
        })

        return HTTPRequest(url=url, **kwargs)

    def handle_response(self, response):
        if response.error and not isinstance(response.error, HTTPError):
            self.set_status(500)
            self.write('Robot Engine error:\n' + str(response.error))
        else:
            self.set_status(response.code)

            for header in self.resp_header_fields():
                v = response.headers.get(header)
                if v:
                    self.set_header(header, v)

            if response.body:
                self.write(response.body)

        self.finish()


class BaseHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_default_headers(self):
        if 'Origin' in self.request.headers:
            origin = self.request.headers['Origin']
            self.set_header("Access-Control-Allow-Origin", origin)
            self.set_header("Access-Control-Allow-Headers", "x-requested-with")
            self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.set_header('Access-Control-Allow-Credentials', "true")

    def prepare(self):
        super().prepare()

        logger.debug(
            "request: {}".format(
                (
                    self.request.method,
                    self.request.path,
                    self.request.arguments,
                    self.request.headers,
                )
            )
        )

        for h in ("Accept", "Accept-Language", "User-Agent"):
            v = self.get_argument("_".join([""] + h.split("-")).lower(), None)
            if v is not None:
                self.request.headers[h] = v

        accept = self.request.headers.get("Accept", "application/json")
        if XML_CPL.match(accept):
            self.response_type = "xml"
        elif JSON_CPL.match(accept):
            self.response_type = "json"
        else:
            self.response_type = "html"
        self.code, self.message = CODE_UNDEFINED, None

    def response_json(
            self, code=CODE_OK, message=None, status_code=200, **kwargs):
        self.code, self.message = code, message

        message = message or MESSAGES.get(code, "")
        data = {
            "code": code,
            "message": (message if isinstance(message, str) else json.dumps(message)),
        }
        data.update(kwargs)

        self.set_status(status_code)
        ua = self.request.headers.get('User-Agent', "")
        if re.match(r".+\s+MSIE\s+.+", ua):
            self.set_header("Content-Type", "text/html; charset=utf-8")
        else:
            self.set_header("Content-Type", "application/json; charset=utf-8")
        self.finish(json.dumps(
            to_json_type(data),
            ensure_ascii=False))
        logger.debug('(test){}'.format(json.dumps(to_json_type(data), ensure_ascii=False)))

    def response_json_with_nil(
            self, code=CODE_OK, message=None, status_code=200, **kwargs):
        self.code, self.message = code, message

        message = message or MESSAGES.get(code, "")
        data = {
            "code": code,
            "message": (message if isinstance(message, str) else json.dumps(message)),
        }
        data.update(kwargs)

        self.set_status(status_code)
        ua = self.request.headers.get('User-Agent', "")
        if re.match(r".+\s+MSIE\s+.+", ua):
            self.set_header("Content-Type", "text/html; charset=utf-8")
        else:
            self.set_header("Content-Type", "application/json; charset=utf-8")
        self.finish(json.dumps(
            to_json_type(data, reserve_none=True),
            ensure_ascii=False))
        logger.debug('(test){}'.format(json.dumps(to_json_type(data, reserve_none=True), ensure_ascii=False)))

    def common_return(self, data, err):
        if err:
            return self.response_json(code=CODE_SYSTEM_ERROR, message=err)
        return self.response_json(code=CODE_OK, data=data)

    def response_json_hook(
            self, status_code=200, data={}):
        self.set_status(status_code)
        ua = self.request.headers.get('User-Agent', "")
        if re.match(r".+\s+MSIE\s+.+", ua):
            self.set_header("Content-Type", "text/html; charset=utf-8")
        else:
            self.set_header("Content-Type", "application/json; charset=utf-8")
        self.finish(json.dumps(
            to_json_type(data),
            ensure_ascii=False))
        logger.debug('(test){}'.format(json.dumps(to_json_type(data), ensure_ascii=False)))

    def response_html(
            self, template, code=CODE_OK, message=None, status_code=200, **kwargs
    ):
        self.code, self.message = code, message

        message = message or ""
        data = {
            "code": code,
            "message": (message if isinstance(message, str) else json.dumps(message)),
        }
        data.update(kwargs)

        self.set_status(status_code)
        self.set_header("Content-Type", "text/html; charset=utf-8")
        self.render(template, **data)

    def response(
            self,
            content,
            content_type_header="text/plain; charset=utf-8",
            code=CODE_OK,
            message=None,
            status_code=200,
    ):
        self.code, self.message = code, message

        self.set_status(status_code)
        self.set_header("Content-Type", content_type_header)
        self.finish(content)

    def write_error(self, status_code, **kwargs):
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            error_message = traceback.format_exception(*kwargs["exc_info"])
            logger.error(error_message)
            print(kwargs["exc_info"], error_message)
            message = ''
        else:
            message = self._reason

        return self.response_json(CODE_SYSTEM_ERROR, message)

    def on_finish(self):
        request_method = self.request.method
        request_path = self.request.path
        _info = {
            "request_time": datetime.utcnow(),
            "time_served": self.request.request_time(),
            "http_user_agent": self.request.headers.get("User-Agent", ""),
            "remote_ip": self.request.remote_ip,
            "arguments": {
                k.translate({ord("."): "_", ord("'"): "_", ord('"'): "_"}): v[0].decode(
                    errors="replace"
                )
                for k, v in self.request.arguments.items()
            },
            "code": self.code,
        }
        rlogger.info(
            "{} {} {}".format(
                request_method,
                request_path,
                json.dumps(to_json_type(_info), ensure_ascii=False),
            )
        )


class BaseRedirectHandler(RedirectHandler):
    def get(self, *args):
        url = self._url.format(*args)
        self.redirect(url, permanent=self._permanent)
