from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('driver', '/deploy/driver')
    config.add_route('stack', '/deploy/stack')
    config.add_route('manage','/manage/{uuid}')
    config.add_route('logfile','/logfile/{uuid}')
    config.add_route('stacktarget', '/deploy/stack.target')
    config.add_route('drivertarget', '/deploy/driver.target')
    config.scan()
    return config.make_wsgi_app()
