
default_settings = [
        ('auth_url', str, 'http://localhost:5000/v3'),
        ('region', str, 'RegionOne'),
        ('user_domain_name', str, 'Default'),
        ('cacert', str, ''),
]

def parse_settings(settings, prefix='keystone.'):
    parsed = {}

    def populate(name, convert, default):
        sname = '%s%s' % (prefix, name)
        value = convert(settings.get(sname, default))
        parsed[sname] = value

    for name, convert, default in default_settings:
        populate(name, convert, default)

    return parsed

def from_settings(settings, prefix='keystone.'):
    fetched = {}

    def populate(name, default):
        sname = '%s%s' % (prefix, name)
        value = settings.get(sname, default)
        fetched[name] = value

    for name, _, default in default_settings:
        populate(name, default)

    return fetched
