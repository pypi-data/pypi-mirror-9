class CubicWebViewMapper(object):
    def __init__(self, **kw):
        pass

    def __call__(self, view):
        def wrapper(context, request):
            print "HERE I AM, instanciating", view
            view_instance = view(request.cw_request)  # rset,  **request.matchdict)
            # XXX feed a stream that writes directly into the response object
            view_instance.set_stream()

            view_instance.render()
            request.response.text = view_instance._stream.getvalue()

            # XXX CubicWebPyramidRequest.headers_out should
            # access directly the pyramid response headers.
            request.response.headers.clear()
            for k, v in request.cw_request.headers_out.getAllRawHeaders():
                for item in v:
                    request.response.headers.add(k, item)
            return request.response

        return wrapper


def includeme(config):
    vreg = config.registry['cubicweb.registry']

    #for view in vreg['views']:
        #config.add_view(
            #view, mapper=CubicWebViewMapper, custom_predicate=view.__select)
