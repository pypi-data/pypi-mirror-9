# -*- coding: utf-8 -*-
#
# Copyright(c) 2014 palmhold.com
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from tornado import escape
from tornado.web import HTTPError

# HTTP status code
HTTP_OK = 200
ERROR_BAD_REQUEST = 400
ERROR_UNAUTHORIZED = 401
ERROR_FORBIDDEN = 403
ERROR_NOT_FOUND = 404
ERROR_METHOD_NOT_ALLOWED = 405
ERROR_INTERNAL_SERVER_ERROR = 500
# Custom error code
ERROR_WARNING = 1001
ERROR_DEPRECATED = 1002
ERROR_MAINTAINING = 1003
ERROR_UNKNOWN_ERROR = 9999


class DjinnError(Exception):
    pass


class DatastoreError(DjinnError):
    pass


class TemplateContextError(DjinnError):

    """Template context variable does not exist."""
    pass


class HTTPAPIError(HTTPError):

    """API error handling exception

    API server always returns formatted JSON to client even there is
    an internal server error.
    """

    def __init__(self, status_code=ERROR_UNKNOWN_ERROR, message=None,
                 error=None, data=None, *args, **kwargs):
        assert isinstance(data, dict) or data is None
        message = message if message else ""
        assert isinstance(message, basestring)

        super(HTTPAPIError, self).__init__(int(status_code),
                                           log_message=message, *args, **kwargs)

        self.error = error if error else \
            _error_types.get(self.status_code, _unknow_error)
        self.message = message if message else \
            _error_messages.get(self.status_code, _unknow_message)
        self.data = data if data is not None else {}

    def __str__(self):
        err = {"meta": {"code": self.status_code, "error": self.error}}

        if self.data:
            err["data"] = self.data

        if self.message:
            err["meta"]["message"] = self.message % self.args

        return escape.json_encode(err)


# default errors
_unknow_error = "unknow_error"
_unknow_message = "未知错误,请稍后重试"
_error_types = {400: "bad_request",
                401: "unauthorized",
                403: "forbidden",
                404: "not_found",
                405: "method_not_allowed",
                500: "internal_server_error",
                1001: "warning",
                1002: "deprecated",
                1003: "maintaining",
                9999: _unknow_error}

_error_messages = {400: "请求参数错误",
                   401: "用户未登录",
                   403: "您未登录或无权访问",
                   404: "资源不存在",
                   405: "客户端请求方式错误",
                   500: "服务器这会开了小差，请稍后再试",
                   1001: "警告错误提示",
                   1002: "接口不兼容,请升级版本",
                   1003: "服务器维护中",
                   9999: _unknow_error}
