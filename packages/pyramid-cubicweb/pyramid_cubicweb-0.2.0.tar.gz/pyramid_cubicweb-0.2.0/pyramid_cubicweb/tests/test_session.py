from pyramid_cubicweb.tests import PyramidCWTest


def authenticated(request):
    response = request.response
    response.body = (
        'anonymous' if request.cw_session.anonymous_session else
        'authenticated')
    return response


class SessionTest(PyramidCWTest):
    anonymous_allowed = True

    def includeme(self, config):
        config.add_route('authenticated', '/authenticated')
        config.add_view(authenticated, route_name='authenticated')

    def test_anonymous_session(self):
        self.assertEqual('anonymous', self.webapp.get('/authenticated').body)
