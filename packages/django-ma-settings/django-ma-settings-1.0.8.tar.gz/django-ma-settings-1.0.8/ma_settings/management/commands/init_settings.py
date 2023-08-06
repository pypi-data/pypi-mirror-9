from django.core.management.base import BaseCommand
from ma_settings.models import MasterSetting
from django.conf import settings
from django.db.models.loading import get_model


class Command(BaseCommand):
    args = 'No args.'
    help = 'Initializes and updates master settings.'

    def handle(self, *args, **options):
        manager = MasterSettingManager()
        manager.init_settings()


class MasterSettingManager(object):
    def init_settings(self):
        if hasattr(settings, 'MASTER_SETTINGS'):
            settings_def = settings.MASTER_SETTINGS
            for setting_name, setting_def in settings_def.items():
                if self.setting_has_changed_or_new(setting_name, setting_def):
                    self.delete_setting(setting_name)
                    self.create_new_setting(setting_def, setting_name)
                self.update_rest_fields(setting_def, setting_name)
            self.delete_old_settings(settings_def)

    def setting_has_changed_or_new(self, setting_name, setting_def):
        try:
            setting = MasterSetting.objects.get(name=setting_name)
            if setting.type != setting_def['type']:
                return True
        except MasterSetting.DoesNotExist:
            return True
        return False

    def delete_setting(self, setting_name):
        try:
            setting = MasterSetting.objects.get(name=setting_name)
            setting.delete()
        except MasterSetting.DoesNotExist:
            pass

    def create_new_setting(self, setting_def, setting_name):
        new_setting = MasterSetting(name=setting_name)
        new_setting.type = self.check_type(setting_def['type'])
        if 'display_name' in setting_def:
            new_setting.display_name = str(setting_def['display_name'])
        else:
            new_setting.display_name = str(setting_name)
        if new_setting.type == 'foreign':
            new_setting.foreign_model = self.check_model(setting_def)
        if 'default' in setting_def and new_setting.type != 'foreign':
            new_setting.value = setting_def['default']
        new_setting.save()

    def check_type(self, setting_type):
        if setting_type in ['integer', 'float', 'string', 'choices', 'foreign']:
            return setting_type
        raise Exception("Unknown setting type: %s" % setting_type)

    def check_model(self, setting_def):
        if 'model' in setting_def:
            model = setting_def['model']
            get_model(*model.split("."))
            return model
        raise Exception("Master settings: foreign setting must have 'model' field")

    def delete_old_settings(self, settings_def):
        existing_settings = MasterSetting.objects.all()
        for existing_setting in existing_settings:
            if existing_setting.name not in settings_def:
                self.delete_setting(existing_setting.name)

    def update_rest_fields(self, setting_def, setting_name):
        setting = MasterSetting.objects.get(name=setting_name)
        if 'display_name' in setting_def:
            setting.display_name = str(setting_def['display_name'])
        else:
            setting.display_name = str(setting_name)
        setting.save()
