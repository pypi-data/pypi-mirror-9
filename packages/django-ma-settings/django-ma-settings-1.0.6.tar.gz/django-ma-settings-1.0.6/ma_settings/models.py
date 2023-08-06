from django.db import models
from django.utils.translation import ugettext_lazy as _


class SettingTypes(object):
    INT = 'integer'
    STRING = 'string'
    CHOICES = 'choices'
    FLOAT = 'float'
    FOREIGN = 'foreign'


class MasterSetting(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    display_name = models.CharField(max_length=255, verbose_name=_("Display name"))
    value = models.CharField(max_length=1000, verbose_name=_("Setting value"), null=True)
    type = models.CharField(max_length=10, verbose_name=_("Setting type"), choices=(
        (SettingTypes.INT, 'Integer'),
        (SettingTypes.STRING, 'String'),
        (SettingTypes.CHOICES, 'Choices'),
        (SettingTypes.FLOAT, 'Float'),
        (SettingTypes.FOREIGN, 'Foreign key')
    ))
    foreign_model = models.CharField(max_length=255, verbose_name=_("Foreign model"), null=True)

