from pyramid.authorization import ACLAuthorizationPolicy


def includeme(config):
    settings = config.registry.settings
    policy = settings.get('pyramid_auth.policy') or 'cookie'

    if policy not in ['cookie', 'remote_user', 'ldap']:
        raise Exception('Policy not supported: %s' % policy)

    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.include('pyramid_auth.%s_auth' % policy)

    sqladmin_dir = 'pyramid_auth:templates'

    if 'mako.directories' not in settings:
        settings['mako.directories'] = []

    if type(settings['mako.directories']) is list:
        settings['mako.directories'] += [sqladmin_dir]
    else:
        settings['mako.directories'] += '\n%s' % sqladmin_dir
