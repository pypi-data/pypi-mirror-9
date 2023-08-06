import os
from cratis.features import Feature


class AdminThemeSuit(Feature):

    def __init__(self, title='My site', menu=None):
        self.title = title
        self.menu = menu

    def configure_settings(self):

        self.append_apps(['suit'])

        self.append_template_processor('django.core.context_processors.request')

        self.settings.SUIT_CONFIG = {
            'ADMIN_NAME': self.title,
            'CONFIRM_UNSAVED_CHANGES': False
        }

        if self.menu:
            self.settings.SUIT_CONFIG['MENU'] = self.menu

        self.settings.TEMPLATE_DIRS += (os.path.dirname(os.path.dirname(__file__)) + '/templates/suit-feature',)
