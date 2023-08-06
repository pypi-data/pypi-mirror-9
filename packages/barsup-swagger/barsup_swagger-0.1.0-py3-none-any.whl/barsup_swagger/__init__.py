# coding: utf-8

import os

from webob import Response
from webob.dec import wsgify
from webob.static import DirectoryApp


def with_swagger(spec_file_name, path='/swagger'):
    """
    WSGI-middleware, релизующее поведение серверной стороны Swagger-UI
    """
    static_path = os.path.join(
        os.path.split(os.path.abspath(__file__))[0],
        'static'
    )
    static_app = DirectoryApp(
        static_path,
        hide_index_with_redirect=True
    )
    spec_file_name = os.path.expandvars(spec_file_name)

    @wsgify.middleware
    def swagger_middleware(request, app):
        url = request.path
        if url == '/v2/swagger.json':
            # Файл перечитывается каждый раз для нужд разработки
            with open(spec_file_name, encoding="utf-8") as f:
                return Response(body=f.read(), content_type="application/json")
        elif url.startswith(path):
            return static_app
        else:
            return app

    return swagger_middleware
