from django.conf import settings as settings_py
from django.db.models.loading import get_model
from django.forms import forms
from django.forms import fields
from django.forms.models import ModelChoiceField
from django.shortcuts import render
from django.views.generic import TemplateView
from ma_settings.models import MasterSetting, SettingTypes


class SettingsForm(forms.Form):
    settings = None

    def __init__(self, settings, data=None):
        super(SettingsForm, self).__init__(data=data)
        self.settings = settings
        for setting in settings:
            if setting.type == SettingTypes.STRING:
                self.fields[self.field(setting)] = fields.CharField(label=setting.display_name, initial=setting.value)
            elif setting.type == SettingTypes.INT:
                self.fields[self.field(setting)] = fields.IntegerField(label=setting.display_name, initial=setting.value)
            elif setting.type == SettingTypes.FLOAT:
                self.fields[self.field(setting)] = fields.CharField(label=setting.display_name, widget=fields.NumberInput(),
                                                                    initial=setting.value)
            elif setting.type == SettingTypes.FOREIGN:
                model = get_model(*setting.foreign_model.split("."))
                self.fields[self.field(setting)] = ModelChoiceField(label=setting.display_name, queryset=model.objects.all(),
                                                                    initial=setting.value)
            elif setting.type == SettingTypes.CHOICES:
                options = settings_py.MASTER_SETTINGS[setting.name]['options']
                choices = []
                for option in options:
                    choices.append((option, option))
                self.fields[self.field(setting)] = fields.ChoiceField(label=setting.display_name, choices=choices,
                                                                      initial=setting.value)

    def field(self, setting):
        return 'field%i' % setting.id

    def clean(self):
        for setting in self.settings:
            self.cleaned_data[self.field(setting)] = self.data[self.field(setting)]
        return self.cleaned_data

    def save(self):
        for setting in self.settings:
            value = self.cleaned_data[self.field(setting)]
            setting.value = value
            setting.save()


class HomeView(TemplateView):
    template_name = 'ma_settings/home.html'
    form = None

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        all_settings = MasterSetting.objects.all()
        context['settings'] = all_settings
        context['base_template'] = 'ma_settings/base.html'
        context['form'] = self.form

        if hasattr(settings_py, 'BASE_SETTINGS_TEMPLATE_NAME'):
            context['base_template'] = settings_py.BASE_SETTINGS_TEMPLATE_NAME

        return context

    def dispatch(self, request, *args, **kwargs):
        all_settings = MasterSetting.objects.all()
        if request.method == 'POST':
            self.form = SettingsForm(all_settings, request.POST)
            if self.form.is_valid():
                self.form.save()
            return render(request, self.template_name, self.get_context_data(**kwargs))
        else:
            self.form = SettingsForm(all_settings)
            return render(request, self.template_name, self.get_context_data(**kwargs))