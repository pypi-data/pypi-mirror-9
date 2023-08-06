from django.conf import settings
from django.db.models.loading import get_model
from models import MasterSetting, SettingTypes


def get(name, default=None):
    try:
        setting = MasterSetting.objects.get(name=name)
        if setting.type == SettingTypes.INT:
            return int(setting.value)
        elif setting.type == SettingTypes.FLOAT:
            return float(setting.value)
        elif setting.type == SettingTypes.FOREIGN:
            model = get_model(*setting.foreign_model.split("."))
            try:
                return model.objects.get(id=int(setting.value))
            except model.DoesNotExist:
                return default
        elif setting.type == SettingTypes.CHOICES:
            return setting.value
        else:
            return setting.value
    except MasterSetting.DoesNotExist:
        return default


def set(name, value):
    setting = MasterSetting.objects.get(name=name)
    if setting.type == SettingTypes.INT:
        setting.value = str(int(setting.value))
    elif setting.type == SettingTypes.FLOAT:
        setting.value = str(float(setting.value))
    elif setting.type == SettingTypes.FOREIGN:
        model = get_model(*setting.foreign_model.split("."))
        try:
            object_ = model.objects.get(id=int(value.id))
            setting.value = str(object_.id)
        except model.DoesNotExist:
            return None
    elif setting.type == SettingTypes.CHOICES:
        options_ = settings.MASTER_SETTINGS[setting.name]['options']
        if value in options_:
            setting.value = value
        else:
            raise ValueError("Available options are: %s " % str(options_))
    else:
        setting.value = value
    setting.save()


def exists(name):
    try:
        MasterSetting.objects.get(name=name)
        return True
    except MasterSetting.DoesNotExist:
        return False