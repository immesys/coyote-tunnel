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
    config.include('pyramid_mako')    
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
    
    config.add_route('broker_allocate','/broker/allocate')
    
    #Tunnel broker views
    config.add_route('api_allocate','/api/allocate')
    config.add_route('api_register4','/api/register_A/{key}')
    config.add_route('api_register6','/api/register_AAAA/{key}')
    config.add_route('api_update','/u/{key}')
    config.add_route('api_retire','/api/retire/{key}')
    config.add_route('init_tunnels','/backend/init')
    config.add_route('linuxconfigscript','/c/nix/{key}')
    config.add_route('whoami','/broker/whoami')
    
    
    
    config.scan()
    return config.make_wsgi_app()
