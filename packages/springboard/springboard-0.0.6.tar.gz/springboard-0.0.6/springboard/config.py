def includeme(config):
    config.add_static_view('static', 'springboard:static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('category', '/category/{uuid}/')
    config.add_route('page', '/page/{uuid}/')
    config.add_route('flat_page', '/{slug}/')
    config.add_route('api_notify', '/api/notify/', request_method='POST')
    config.scan(".views")
    config.scan(".events")
