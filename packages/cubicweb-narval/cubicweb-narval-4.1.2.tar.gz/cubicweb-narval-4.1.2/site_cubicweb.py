
options = (
    # XXX only for all-in-one or repository config
    ('plan-cleanup-delay',
     {'type' : 'time',
      'default' : '60d',
      'help': ('Interval of time after which plans can be '
               'deleted. Default to 60 days. Set it to 0 if you don\'t '
               'want automatic deletion.'),
      'group': 'narval', 'level': 1,
      }),
    )

from rql.utils import register_function, FunctionDescr

class is_null(FunctionDescr):
    supported_backends = ('postgres', 'sqlite',)
    rtype = 'Boolean'

try:
    register_function(is_null)
except AssertionError:
    pass

try:
    from cubicweb.server import SQL_CONNECT_HOOKS
except ImportError: # no server installation
    pass
else:
    def init_sqlite_connection(cnx):
        def _is_null(value):
            return value is None
        cnx.create_function('IS_NULL', 1, _is_null)

    sqlite_hooks = SQL_CONNECT_HOOKS.setdefault('sqlite', [])
    sqlite_hooks.append(init_sqlite_connection)

