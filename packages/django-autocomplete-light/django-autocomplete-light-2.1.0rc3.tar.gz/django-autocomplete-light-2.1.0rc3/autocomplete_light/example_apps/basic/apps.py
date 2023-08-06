from django.apps import AppConfig


class AutocompleteLightConfig(AppConfig):
    name = 'al'

    def ready(self):
        al.autodiscover()

    def al_register(self, al):
        models = [self.get_model(m) for m in 'OtoModel', 'FkModel',
                'MtmModel', 'GfkModel']

        class A(al.AutocompleteGenericBase):
            choices=[m.objects.all() for m in models]
            search_fields=[['name']] * len(models)
        yield A

        class B(al.AutocompleteGenericBase):
            choices=[m.objects.all() for m in models]
            search_fields=[['name']] * len(models)
            widget_attrs={'data-widget-maximum-values': 4}
        yield B

        yield al.AutocompleteModelBase(
                self.get_model('Tag'))
