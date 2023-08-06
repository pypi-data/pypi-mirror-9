class UrlBuilder(object):

    def __init__(self, name, template, *children):
        self.name = name
        self.template = template
        self.parent = None
        self.children = {child.name: child for child in children}
        for child in self.children.values():
            child.set_parent(self)

    def set_parent(self, parent):
        self.parent = parent

    @property
    def full_template(self):
        if self.parent is None:
            root = ''
        else:
            root = self.parent.full_template
        return '{root}{leaf}'.format(root=root, leaf=self.template)

    def format(self, **kwargs):
        return self.full_template.format(**kwargs)

    def __getattr__(self, name):
        if name not in self.children:
            raise AttributeError(name)
        return self.children[name]

    def __iter__(self):
        yield self.full_template
        for name, child in sorted(self.children.items()):
            for template in child:
                yield template


URLS = UrlBuilder(
    'root', '/api/v0/json',
    UrlBuilder(
        'admin', '/admin',
        UrlBuilder(
            'organizations', '/organizations',
            UrlBuilder('repositories', '/{organization_name}/repositories'),
            UrlBuilder('teams', '/{organization_name}/teams'),
            UrlBuilder('users', '/{organization_name}/users'),
        ),
        UrlBuilder(
            'repositories', '/repositories/{organization_name}/{repository_name}'),  # noqa
        UrlBuilder(
            'teams', '/teams/{organization_name}/{team_name}',
            UrlBuilder(
                'members', '/members',
                UrlBuilder('query', '/{email}'),
            ),
            UrlBuilder(
                'repositories', '/repositories',
                UrlBuilder('query', '/{repository_name}'),
            ),
        ),
        UrlBuilder(
            'users', '/users',
            UrlBuilder('metadata', '/{organization_name}/{email}'),
        ),
    ),
    UrlBuilder(
        'tokens', '/auth/tokens',
        UrlBuilder(
            'api', '/api',
            UrlBuilder('delete', '/{name}'),
        ),
    ),
    UrlBuilder(
        'data', '/data/{organization_name}/{repository_name}',
        UrlBuilder(
            'apps', '/{platform}/apps',
            UrlBuilder('upload', '/upload'),
        ),
        UrlBuilder(
            'eggs', '/{platform}',
            UrlBuilder('upload', '/eggs/upload'),
            UrlBuilder(
                'download', '/{python_tag}/eggs/{name}/{version}'),
            UrlBuilder(
                'delete', '/{python_tag}/eggs/{name}/{version}'),
        ),
        UrlBuilder(
            'runtimes', '/{platform}/runtimes',
            UrlBuilder('upload', '/upload'),
            UrlBuilder('download', '/{python_tag}/{version}'),
        ),
        UrlBuilder(
            're_index', '',
            UrlBuilder('eggs', '/eggs/re-index'),
        ),
    ),
    UrlBuilder(
        'indices', '/indices/{organization_name}/{repository_name}/{platform}',
        UrlBuilder('apps', '/apps'),
        UrlBuilder('eggs', '/{python_tag}/eggs'),
        UrlBuilder('runtimes', '/runtimes'),
    ),
    UrlBuilder(
        'metadata', '/metadata',
        UrlBuilder(
            'artefacts', '/{organization_name}/{repository_name}/{platform}',
            UrlBuilder('apps', '/{python_tag}/apps/{app_id}/{version}'),
            UrlBuilder('eggs', '/{python_tag}/eggs/{name}/{version}'),
            UrlBuilder('runtimes', '/runtimes/{python_tag}/{version}'),
        ),
        UrlBuilder('platforms', '/platforms'),
        UrlBuilder(
            'python_tags', '/python-tags',
            UrlBuilder('all', '/all'),
        )
    ),
)
