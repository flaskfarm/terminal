setting = {
    'title': "터미널",
    'version': '1.0.0.0',
    'package_name' : __package__,
    'developer': 'joyfuI',
    'description': 'xterm.js client',
    'home' : f'https://github.com/flaskfarm/{__package__}',

    'plugin_type': 'normal',
    'filepath' : __file__,
    'use_db': False,
    'use_default_setting': False,
    'home_module': None,
    'menu': None,
    'require_plugin': [],
    'require_os' : ['Linux'],
    'default_route': None,
}

from plugin.common import *
P = create_plugin_instance(setting)

try:
    from .mod_terminal import ModuleTerminal
    P.set_module_list([ModuleTerminal])
except Exception as e:
    P.logger.error(f'Exception:{str(e)}')
    P.logger.error(traceback.format_exc())

