setting = {
    'filepath' : __file__,
    'use_db': False,
    'use_default_setting': False,
    'home_module': 'terminal',
    'menu': {
        'uri': __package__,
        'name': '터미널',
        'list': [
            {
                'uri': '',
                'name': 'NEW 터미널',
                'target': '_blank',
            },
            {
                'uri': 'setting',
                'name': '설정',
            },
        ]
    },
    'setting_menu': {
        'uri': f"{__package__}/setting",
        'name': '터미널 작업',
    },
    'default_route': 'normal',
}

from plugin import *

P = create_plugin_instance(setting)

try:
    from .mod_setting import ModuleSetting
    from .mod_terminal import ModuleTerminal
    P.set_module_list([ModuleTerminal, ModuleSetting])
except Exception as e:
    P.logger.error(f'Exception:{str(e)}')
    P.logger.error(traceback.format_exc())

