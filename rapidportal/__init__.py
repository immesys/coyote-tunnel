from pyramid.config import Configurator

from authomatic import Authomatic
import authomatic
from authomatic.adapters import WebObAdapter
from pyramid.session import UnencryptedCookieSessionFactoryConfig
   
def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    sf = UnencryptedCookieSessionFactoryConfig('comeCSRFmebro')
    
    config = Configurator(settings=settings, session_factory=sf)
    
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('driver', '/deploy/driver')
    config.add_route('stack', '/deploy/stack')
    config.add_route('manage','/manage/{uuid}')
    config.add_route('logfile','/logfile/{uuid}')
    config.add_route('stacktarget', '/deploy/stack.target')
    config.add_route('drivertarget', '/deploy/driver.target')
    config.add_route('auth','/auth')
    config.add_route('deauth','/deauth')
    config.add_route('login','/logpage')
    config.scan()
    return config.make_wsgi_app()
