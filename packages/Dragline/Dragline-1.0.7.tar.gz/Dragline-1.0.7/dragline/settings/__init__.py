import global_settings


class Settings(object):
    def __init__(self, settings_module):
        for setting in dir(global_settings):
            setting_value = getattr(global_settings, setting)
            setattr(self, setting, setting_value)
        self.update(settings_module)

    def update(self, module):
        for setting in dir(module):
            if setting.isupper() and hasattr(self, setting):
                new_value = getattr(module, setting)
                old_value = getattr(self, setting)
                if isinstance(old_value, dict):
                    old_value.update(new_value)
                    new_value = old_value
                setattr(self, setting, new_value)
