from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from .resources import bootstrap


def main(global_config, **settings):
    config = Configurator(settings=settings, root_factory=bootstrap)

    authn_policy = AuthTktAuthenticationPolicy('seekrit')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(ACLAuthorizationPolicy())

    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.scan('.views')
    return config.make_wsgi_app()
